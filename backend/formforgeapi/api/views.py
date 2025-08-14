# path: backend/formforgeapi/api/views.py

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

from ..models import (
    Department, 
    Form, 
    FormField, 
    FormSubmission, 
    SubmissionValue,
    FormFieldOption
)
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

# ==============================================================================
# BAĞIMSIZ API VIEW'LERİ (VIEWSET DIŞI)
# ==============================================================================

class UpdateFormFieldOrderView(APIView):
    """
    Form alanlarının sırasını toplu olarak günceller.
    Bu yaklaşım, ModelViewSet'teki standart metodlarla (örn: PUT) çakışmayı önler.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Sıralama verisini (örn: [{'id': 1, 'order': 0}, ...]) alır ve servise iletir."""
        order_data = request.data
        try:
            # Servis katmanı, bulk_update ile veritabanını verimli şekilde günceller.
            return formforgeapi_service.update_formfield_order(order_data)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Beklenmedik hatalar için genel bir loglama ve hata mesajı.
            # logging.error(f"Sıralama güncellenirken hata: {str(e)}")
            return Response(
                {"error": "Sunucu hatası, sıralama güncellenemedi."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ==============================================================================
# VIEWSET'LER
# ==============================================================================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Kullanıcıları listeler (frontend'deki 'userpicker' gibi bileşenler için)."""
    serializer_class = SimpleUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Veriyi, optimize edilmiş sorguları içeren servis katmanından alır."""
        return formforgeapi_service.get_user_list()

class DepartmentViewSet(viewsets.ModelViewSet):
    """Departmanları yönetir."""
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

class FormViewSet(viewsets.ModelViewSet):
    """Form şemalarını ve versiyonlarını yönetir."""
    # TEMEL QUERYSET: Tüm sorgular için veritabanını optimize eder.
    queryset = Form.objects.all().select_related(
        'department', 'created_by'
    ).prefetch_related(
        'fields__options' # Alanları ve her alanın seçeneklerini tek seferde çeker.
    )
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def get_queryset(self):
        """
        Dinamik olarak queryset'i filtreler.
        Liste görünümünde sadece en son, aktif versiyonları gösterir.
        """
        queryset = super().get_queryset()
        if self.action == 'list':
            # Sadece ana formları (versiyon olmayan) ve 'Dağıtımda' olanları listele.
            return queryset.filter(parent_form__isnull=True, status=Form.FormStatus.PUBLISHED)
        # Detay (retrieve) görünümünde her türlü forma erişime izin verilir.
        return queryset

    def perform_create(self, serializer):
        """Yeni form oluşturulurken 'created_by' alanını ve varsayılan durumu ayarlar."""
        serializer.save(created_by=self.request.user, status=Form.FormStatus.PUBLISHED)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Mevcut bir formdan yeni bir versiyon oluşturur."""
        try:
            new_form = formforgeapi_service.create_new_form_version(pk, request.user)
            serializer = self.get_serializer(new_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Form.DoesNotExist:
            raise NotFound(detail="Kopyalanacak form bulunamadı.")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Arşivleme işlemleri için diğer @action metodlarınız buraya eklenebilir.
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        form = self.get_object()
        form.status = Form.FormStatus.ARCHIVED
        form.save()
        return Response({'status': 'Form arşivlendi'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='unarchive')
    def unarchive(self, request, pk=None):
        form = self.get_object()
        form.status = Form.FormStatus.PUBLISHED
        form.save()
        return Response({'status': 'Form arşivi kaldırıldı'}, status=status.HTTP_200_OK)


class FormFieldViewSet(viewsets.ModelViewSet):
    """Tekil form alanlarını yönetir (oluşturma, silme, güncelleme)."""
    queryset = FormField.objects.all().prefetch_related('options')
    serializer_class = FormFieldSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='add-option')
    def add_option(self, request, pk=None):
        """Mevcut bir form alanına yeni bir seçenek (örn: select için) ekler."""
        form_field = self.get_object()
        serializer = FormFieldOptionSerializer(
            data=request.data, 
            context={'form_field': form_field} # Serializer'a ana nesneyi context ile ver.
        )
        serializer.is_valid(raise_exception=True)
        # Serializer'ın save metodu, context'ten aldığı form_field ile kaydı oluşturur.
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='options/(?P<option_pk>[^/.]+)')
    def delete_option(self, request, pk=None, option_pk=None):
        """Bir form alanına ait belirli bir seçeneği siler."""
        form_field = self.get_object()
        try:
            option = FormFieldOption.objects.get(pk=option_pk, form_field=form_field)
            option.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FormFieldOption.DoesNotExist:
            raise NotFound("Silinecek seçenek bulunamadı.")


class FormSubmissionViewSet(viewsets.ModelViewSet):
    """Form gönderimlerini ve bu gönderimlerin versiyonlarını yönetir."""
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def get_queryset(self):
        """Veritabanı sorgularını optimize eder ve filtreleme uygular."""
        queryset = super().get_queryset().select_related(
            'created_by', 'form', 'parent_submission'
        ).prefetch_related(
            'values__form_field'
        )
        
        # API'nin liste görünümünde mutlaka bir form ID'si ile çağrılmasını zorunlu kıl.
        form_id = self.request.query_params.get('form')
        if self.action == 'list':
            if not form_id:
                # Eğer form ID belirtilmemişse, boş bir liste döndür.
                return self.queryset.none()
            
            queryset = queryset.filter(form_id=form_id)
            # 'all_versions=true' parametresi yoksa, sadece aktif versiyonları göster.
            if self.request.query_params.get('all_versions') != 'true':
                queryset = queryset.filter(is_active=True)
        
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Yeni bir form gönderimi oluşturur. İş mantığı servis katmanındadır.
        """
        # Serializer.validated_data'dan gerekli bilgileri alıp servisi çağırırız.
        # Bu, mantığın ViewSet içinde daha açık olmasını sağlar.
        form = serializer.validated_data.get('form')
        values_data = self.request.data.get('values', [])
        
        try:
            new_submission = formforgeapi_service.create_submission(
                form.id, values_data, self.request.user
            )
            # Başarılı yaratma sonrası tam veriyi döndürmek için yeniden serialize et.
            # Not: Bu, create_submission servisinin nesneyi döndürdüğünü varsayar.
            response_serializer = self.get_serializer(new_submission)
            # HTTP 201 Created ile tam nesneyi döndür.
            # Ancak serializer'in save metodu zaten bunu yaptığı için aşağıdaki satır yeterli:
            serializer.instance = new_submission
            
        except ValidationError as e:
            # Servisten gelen doğrulama hatalarını yakala.
            raise e # DRF bu hatayı 400 Bad Request olarak işleyecektir.
        
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Mevcut bir gönderiyi günceller (aslında yeni bir versiyon oluşturur).
        """
        original_submission_id = kwargs.get('pk')
        values_data = request.data.get('values', [])

        try:
            new_submission = formforgeapi_service.update_submission_and_create_new_version(
                original_submission_id, values_data, self.request.user
            )
            serializer = self.get_serializer(new_submission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FormSubmission.DoesNotExist:
            raise NotFound("Güncellenecek gönderi bulunamadı.")
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Bir gönderinin tüm versiyon geçmişini getirir."""
        submission = self.get_object()
        history_qs = submission.get_version_history() # Bu metodun modelde olduğunu varsayalım.
        serializer = self.get_serializer(history_qs, many=True)
        return Response(serializer.data)

class SubmissionValueViewSet(viewsets.ModelViewSet):
    """(Genellikle direkt kullanılmaz) Form gönderimlerindeki tekil değerleri yönetir."""
    queryset = SubmissionValue.objects.all()
    serializer_class = SubmissionValueSerializer
    permission_classes = [IsAuthenticated]