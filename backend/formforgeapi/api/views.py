# path: backend/formforgeapi/api/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from .serializers import DepartmentSerializer, FormSerializer, FormFieldSerializer, FormSubmissionSerializer, SubmissionValueSerializer
from ..services import formforgeapi_service

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return formforgeapi_service.get_department_list()

class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer

    def get_queryset(self):
        return formforgeapi_service.get_form_list()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class FormFieldViewSet(viewsets.ModelViewSet):
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer

    def get_queryset(self):
        return formforgeapi_service.get_formfield_list()

    @action(detail=False, methods=['post'])
    def update_order(self, request):
        return formforgeapi_service.update_formfield_order(request.data)


class FormSubmissionViewSet(viewsets.ModelViewSet):
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer

    def get_queryset(self):
        return formforgeapi_service.get_formsubmission_list()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SubmissionValueViewSet(viewsets.ModelViewSet):
    queryset = SubmissionValue.objects.all()
    serializer_class = SubmissionValueSerializer

    def get_queryset(self):
        return formforgeapi_service.get_submissionvalue_list()

