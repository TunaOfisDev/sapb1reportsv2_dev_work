# path: backend/formforgeapi/api/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q # DÜZELTME: Q objesi için import eklendi.

from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from .serializers import (
    DepartmentSerializer, 
    FormSerializer, 
    FormFieldSerializer, 
    FormSubmissionSerializer, 
    SubmissionValueSerializer
)
from ..services import formforgeapi_service
from ..permissions import IsCreatorOrReadOnly
from rest_framework.permissions import IsAuthenticated

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return formforgeapi_service.get_department_list()

class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related('department', 'created_by').prefetch_related('fields', 'versions')
        if self.action == 'list':
            status_filter = self.request.query_params.get('status', Form.FormStatus.PUBLISHED)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status=Form.FormStatus.PUBLISHED)
        
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
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return formforgeapi_service.get_formfield_list()

    @action(detail=False, methods=['post'], url_path='update-order')
    def update_order(self, request):
        return formforgeapi_service.update_formfield_order(request.data)

class FormSubmissionViewSet(viewsets.ModelViewSet):
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def get_queryset(self):
        """
        Gönderimleri forma göre filtreler.
        DÜZELTME: is_active filtresi sadece 'list' eylemi için uygulanır.
        Bu, 'history' gibi 'detail' eylemlerinin pasif kayıtları da bulmasını sağlar.
        """
        queryset = self.queryset.select_related('created_by', 'parent_submission').prefetch_related('values__form_field', 'versions')
        
        # Sadece ana listeleme görünümünde aktif olanları filtrele
        if self.action == 'list':
            if self.request.query_params.get('all_versions') != 'true':
                queryset = queryset.filter(is_active=True)

        form_id = self.request.query_params.get('form')
        if form_id:
            return queryset.filter(form_id=form_id)
        
        # 'retrieve', 'update', 'history' gibi eylemler için bu noktaya gelinir
        # ve bu eylemler pk'ya göre çalıştığı için tüm queryset üzerinde çalışabilir.
        # Eğer bir form_id yoksa ve eylem 'list' ise, güvenlik için boş döndür.
        if self.action == 'list':
             return queryset.none()

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
        """
        Belirli bir gönderinin tüm versiyon geçmişini döndürür.
        """
        try:
            submission = self.get_object()
            root_submission = submission.parent_submission or submission
            
            # DÜZELTME: 'models.Q' yerine 'Q' kullanılıyor.
            history_qs = FormSubmission.objects.filter(
                Q(id=root_submission.id) | Q(parent_submission=root_submission)
            ).order_by('version')
            
            # DÜZELTME: Frontend'in detaylı tablo isteği için ana serializer kullanılıyor.
            serializer = self.get_serializer(history_qs, many=True)
            return Response(serializer.data)
            
        except FormSubmission.DoesNotExist:
            return Response({"error": "Gönderi bulunamadı."}, status=404)

class SubmissionValueViewSet(viewsets.ModelViewSet):
    queryset = SubmissionValue.objects.all()
    serializer_class = SubmissionValueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return formforgeapi_service.get_submissionvalue_list()