# path: backend/formforgeapi/services/formforgeapi_service.py
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

def get_department_list():
    return Department.objects.all()

def get_form_list():
    return Form.objects.select_related('department', 'created_by').prefetch_related('fields').all()


def get_formfield_list():
    return FormField.objects.select_related('form').all()


def get_formsubmission_list():
    return FormSubmission.objects.select_related('form', 'created_by').prefetch_related('values').all()


def get_submissionvalue_list():
    return SubmissionValue.objects.select_related('submission', 'form_field').all()


@transaction.atomic
def update_formfield_order(data):
    updated_instances = []
    for item in data:
        instance = FormField(id=item['id'], order=item['order'])
        updated_instances.append(instance)

    try:
        FormField.objects.bulk_update(updated_instances, ['order'])
        return Response({"message": "Sıralama başarıyla güncellendi."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
