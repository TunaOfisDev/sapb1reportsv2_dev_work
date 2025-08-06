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
from ..services import formforgeapi_service

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Departmanları yönetmek için kullanılan API endpoint'i.
    Tam CRUD (Create, Retrieve, Update, Delete) işlevselliği sunar.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        # Departman listesini servisten alır.
        return formforgeapi_service.get_department_list()

class FormViewSet(viewsets.ModelViewSet):
    """
    Form şemalarını yönetmek için kullanılan ana API endpoint'i.
    Arşivleme ve Versiyonlama gibi özel eylemler içerir.
    """
    serializer_class = FormSerializer

    def get_queryset(self):
        """
        Bu metod, istenen eyleme göre dinamik olarak queryset döndürür.
        - 'list' eylemi için: URL'deki '?status=' parametresine göre filtreleme yapar.
        - Diğer tüm eylemler (detay, güncelleme, arşivleme vb.) için:
          Arşivlenmiş formları da bulabilmek için filtresiz bir liste kullanır.
        """
        queryset = Form.objects.all().select_related('department', 'created_by').prefetch_related('fields', 'versions')
        
        if self.action == 'list':
            status_filter = self.request.query_params.get('status', Form.FormStatus.PUBLISHED)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        
        return queryset

    def perform_create(self, serializer):
        """Yeni bir form oluşturulduğunda durumunu 'PUBLISHED' olarak ayarlar."""
        serializer.save(created_by=self.request.user, status=Form.FormStatus.PUBLISHED)
        
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        """Belirtilen ID'ye sahip formu arşive kaldırır."""
        try:
            form = self.get_object()
            form.status = Form.FormStatus.ARCHIVED
            form.save()
            return Response({'status': 'form archived'}, status=status.HTTP_200_OK)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='unarchive')
    def unarchive(self, request, pk=None):
        """Belirtilen ID'ye sahip formu arşivden çıkarıp yeniden yayınlar."""
        try:
            form = self.get_object()
            form.status = Form.FormStatus.PUBLISHED
            form.save()
            return Response({'status': 'form unarchived and published'}, status=status.HTTP_200_OK)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=True, methods=['post'], url_path='create-version')
    def create_version(self, request, pk=None):
        """
        Mevcut bir formdan yeni bir versiyon oluşturur.
        Eski versiyonu arşivler ve yeni versiyonu oluşturup döner.
        """
        try:
            new_form = formforgeapi_service.create_new_form_version(pk, request.user)
            serializer = self.get_serializer(new_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Form.DoesNotExist:
            return Response({'error': 'Original form not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FormFieldViewSet(viewsets.ModelViewSet):
    """Form alanlarını (FormField) yönetir."""
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer

    def get_queryset(self):
        return formforgeapi_service.get_formfield_list()

    @action(detail=False, methods=['post'], url_path='update-order')
    def update_order(self, request):
        """Birden çok form alanının sıralamasını tek seferde günceller."""
        # Bu fonksiyonun mantığı servise taşındı, direkt onu çağırıyoruz.
        return formforgeapi_service.update_formfield_order(request.data)

class FormSubmissionViewSet(viewsets.ModelViewSet):
    """Doldurulmuş formları (FormSubmission) yönetir."""
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer

    def get_queryset(self):
        return formforgeapi_service.get_formsubmission_list()

    def perform_create(self, serializer):
        """Yeni bir gönderim oluşturulduğunda 'created_by' alanını otomatik doldurur."""
        serializer.save(created_by=self.request.user)

class SubmissionValueViewSet(viewsets.ModelViewSet):
    """Form gönderimlerindeki her bir alanın değerini (SubmissionValue) yönetir."""
    queryset = SubmissionValue.objects.all()
    serializer_class = SubmissionValueSerializer

    def get_queryset(self):
        return formforgeapi_service.get_submissionvalue_list()