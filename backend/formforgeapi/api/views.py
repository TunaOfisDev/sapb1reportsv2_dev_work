# path: backend/formforgeapi/api/views.py

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from .serializers import (
    DepartmentSerializer, 
    FormSerializer, 
    FormFieldSerializer, 
    FormFieldOptionSerializer,
    FormSubmissionSerializer, 
    SubmissionValueSerializer,
    SimpleUserSerializer
)
from ..services import formforgeapi_service
from ..permissions import IsCreatorOrReadOnly
from rest_framework.permissions import IsAuthenticated

# ==============================================================================
# BAĞIMSIZ API VIEW'LERİ (VIEWSET DIŞI)
# ==============================================================================

class UpdateFormFieldOrderView(APIView):
    """
    Form alanlarının sırasını toplu olarak günceller.
    ModelViewSet'ten bağımsız olduğu için metod çakışması (405 hatası) riski taşımaz.
    Sadece POST isteklerini kabul eder.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Sıralama verisini alır ve servis katmanına iletir."""
        order_data = request.data
        try:
            return formforgeapi_service.update_formfield_order(order_data)
        except Exception as e:
            return Response(
                {"error": f"Internal server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ==============================================================================
# VIEWSET'LER
# ==============================================================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Kullanıcıları listeler (frontend'deki 'userpicker' için)."""
    serializer_class = SimpleUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Veriyi servis katmanındaki optimize edilmiş fonksiyondan alır."""
        return formforgeapi_service.get_user_list()

class DepartmentViewSet(viewsets.ModelViewSet):
    """formforgeapi içindeki departmanları yönetir."""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]



class FormViewSet(viewsets.ModelViewSet):
    """Form şemalarını ve versiyonlarını yönetir."""
    # DÜZELTME: queryset ve get_queryset metodunu DRF'in standart,
    # en güvenli haline geri döndürüyoruz.
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]

    # GÜNCELLEME: Karmaşık get_queryset metodu ŞİMDİLİK kaldırıldı.
    # DRF, bir formu (retrieve) veya form listesini (list) getirmek için
    # gereken temel optimizasyonları kendisi yapacaktır.
    # Bu değişiklik, ImproperlyConfigured hatasını gidermelidir.

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status=Form.FormStatus.PUBLISHED)
        
    # @action metodlarınız (archive, unarchive, create_version) aynı kalabilir.
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        form = self.get_object()
        form.status = Form.FormStatus.ARCHIVED
        form.save()
        return Response({'status': 'form archived'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='unarchive')
    def unarchive(self, request, pk=None):
        form = self.get_object()
        form.status = Form.FormStatus.PUBLISHED
        form.save()
        return Response({'status': 'form unarchived'}, status=status.HTTP_200_OK)
            
    @action(detail=True, methods=['post'], url_path='create-version')
    def create_version(self, request, pk=None):
        new_form = formforgeapi_service.create_new_form_version(pk, request.user)
        serializer = self.get_serializer(new_form)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    

class FormFieldViewSet(viewsets.ModelViewSet):
    """Tekil form alanlarını yönetir (oluşturma, silme, güncelleme)."""
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='add-option')
    def add_option(self, request, pk=None):
        form_field = self.get_object()
        
        # Gelen veriye 'form_field' ID'sini ekleyerek serializer'ı hazırlıyoruz.
        option_data = request.data.copy()
        # FormFieldOptionSerializer'ın FormField'a ihtiyacı yok, bu satır gereksiz olabilir.
        # Eğer FormFieldOptionSerializer'ınızda 'form_field' alanı zorunlu ise kalmalı.
        # option_data['form_field'] = form_field.pk # Bu satır serializer'ınıza bağlı
        
        # ÖNEMLİ: Serializer'a 'form_field' nesnesini context üzerinden vermek daha sağlam bir yöntemdir.
        serializer = FormFieldOptionSerializer(
            data=request.data, 
            context={'form_field': form_field}
        )
        if serializer.is_valid():
            # Serializer'ın save metodu, context'ten aldığı form_field ile kaydı oluşturmalı.
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FormSubmissionViewSet(viewsets.ModelViewSet):
    """Form gönderimlerini ve versiyonlarını yönetir."""
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset.select_related('created_by', 'parent_submission').prefetch_related('values__form_field', 'versions')
        if self.action == 'list':
            if self.request.query_params.get('all_versions') != 'true':
                queryset = queryset.filter(is_active=True)
        form_id = self.request.query_params.get('form')
        if form_id: return queryset.filter(form_id=form_id)
        if self.action == 'list': return queryset.none()
        return queryset

    def perform_create(self, serializer):
        # Tüm mantık serializer'ın create metodunda, o da servisi çağırıyor.
        serializer.save()

    def update(self, request, *args, **kwargs):
        original_submission_id = kwargs.get('pk')
        values_data = request.data.get('values', [])
        user = request.user
        try:
            new_submission = formforgeapi_service.update_submission_and_create_new_version(
                original_submission_id, values_data, user
            )
            serializer = self.get_serializer(new_submission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FormSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        try:
            submission = self.get_object()
            root_submission = submission.parent_submission or submission
            history_qs = FormSubmission.objects.filter(
                Q(id=root_submission.id) | Q(parent_submission=root_submission)
            ).order_by('version')
            serializer = self.get_serializer(history_qs, many=True)
            return Response(serializer.data)
        except FormSubmission.DoesNotExist:
            return Response({"error": "Gönderi bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

class SubmissionValueViewSet(viewsets.ModelViewSet):
    """(Genellikle direkt kullanılmaz) Form gönderimlerindeki tekil değerleri yönetir."""
    queryset = SubmissionValue.objects.all()
    serializer_class = SubmissionValueSerializer
    permission_classes = [IsAuthenticated]