# path: backend/formforgeapi/api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from .serializers import (
    DepartmentSerializer, 
    FormSerializer, 
    FormFieldSerializer, 
    FormSubmissionSerializer, 
    SubmissionValueSerializer
)
# Service katmanını ve özel izinleri tekrar import ediyoruz
from ..services import formforgeapi_service
from ..permissions import IsCreatorOrReadOnly
from rest_framework.permissions import IsAuthenticated

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Departmanları yönetmek için kullanılan API endpoint'i.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    # Service katmanı kullanımını geri getiriyoruz
    def get_queryset(self):
        return formforgeapi_service.get_department_list()

class FormViewSet(viewsets.ModelViewSet):
    """
    Form şemalarını yönetmek için kullanılan ana API endpoint'i.
    Arşivleme ve Versiyonlama gibi özel eylemler içerir.
    """
    queryset = Form.objects.all() # Hata ayıklaması sırasında eklenen kritik düzeltme
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Gelen isteğe göre formları filtreler.
        `list` eylemi için `status` parametresine göre filtreleme yapar.
        """
        queryset = self.queryset.select_related('department', 'created_by').prefetch_related('fields', 'versions')
        
        if self.action == 'list':
            status_filter = self.request.query_params.get('status', Form.FormStatus.PUBLISHED)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        
        return queryset

    def perform_create(self, serializer):
        """Yeni form oluşturulduğunda `created_by` ve `status` alanlarını ayarlar."""
        serializer.save(created_by=self.request.user, status=Form.FormStatus.PUBLISHED)
        
    # Özel eylemleri (@action) geri getiriyoruz
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
    """Form alanlarını (FormField) yönetir."""
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return formforgeapi_service.get_formfield_list()

    @action(detail=False, methods=['post'], url_path='update-order')
    def update_order(self, request):
        """Alanların sırasını toplu olarak günceller."""
        return formforgeapi_service.update_formfield_order(request.data)

class FormSubmissionViewSet(viewsets.ModelViewSet):
    """Form gönderimlerini (FormSubmission) yönetir."""
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def get_queryset(self):
        """
        Gönderimleri forma göre filtreler ve varsayılan olarak SADECE AKTİF versiyonları listeler.
        """
        queryset = self.queryset.select_related('created_by', 'parent_submission').prefetch_related('values__form_field', 'versions')
        
        # URL'de 'all_versions=true' parametresi yoksa, sadece aktif olanları göster
        if self.request.query_params.get('all_versions') != 'true':
            queryset = queryset.filter(is_active=True)

        form_id = self.request.query_params.get('form')
        if form_id:
            return queryset.filter(form_id=form_id)
        
        return queryset.none()

    def perform_create(self, serializer):
        """Yeni gönderim oluşturulduğunda `created_by` alanını ayarlar."""
        serializer.save(created_by=self.request.user)

    # GÜNCELLEME: 'update' metodu override edildi.
    def update(self, request, *args, **kwargs):
        """
        Standart güncelleme yerine, yeni bir gönderim versiyonu oluşturur.
        """
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



class SubmissionValueViewSet(viewsets.ModelViewSet):
    """Form gönderimlerindeki her bir alanın değerini (SubmissionValue) yönetir."""
    queryset = SubmissionValue.objects.all()
    serializer_class = SubmissionValueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return formforgeapi_service.get_submissionvalue_list()