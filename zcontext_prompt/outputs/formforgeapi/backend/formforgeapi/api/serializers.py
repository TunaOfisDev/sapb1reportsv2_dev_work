# path: backend/formforgeapi/api/serializers.py
from rest_framework import serializers
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class FormSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'department', 'department_name', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'created_by_username']

class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'form', 'label', 'field_type', 'is_required', 'is_master', 'order']

class FormSubmissionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    class Meta:
        model = FormSubmission
        fields = ['id', 'form', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'created_by_username']


class SubmissionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionValue
        fields = ['id', 'submission', 'form_field', 'value']

