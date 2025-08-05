# path: backend/formforgeapi/api/views.py
from rest_framework import viewsets
from ..services import formforgeapi_service as service
from .serializers import DepartmentSerializer, FormSerializer, FormFieldSerializer, FormSubmissionSerializer, SubmissionValueSerializer
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return service.get_all_departments()

class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer

    def get_queryset(self):
        return service.get_all_forms()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class FormFieldViewSet(viewsets.ModelViewSet):
    serializer_class = FormFieldSerializer

    def get_queryset(self):
        return service.get_all_form_fields()

class FormSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = FormSubmissionSerializer

    def get_queryset(self):
        return service.get_all_form_submissions()

    def perform_create(self, serializer):
        submission = serializer.save(created_by=self.request.user)
        service.save_submission(submission, self.request.data.get('submitted_data', {}))


