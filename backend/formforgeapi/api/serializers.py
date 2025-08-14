# backend/formforgeapi/api/serializers.py
import json
from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..services import formforgeapi_service
from ..utils.formfields import FieldTypes
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue, FormFieldOption

# YENİ: CustomUser modelinin ilişkili olduğu modelleri authcentral'dan import ediyoruz.
# İsim çakışmasını önlemek için 'Department' modelini 'AuthDepartment' olarak alıyoruz.
from authcentral.models import Department as AuthDepartment, Position

# ==============================================================================
# 1. TEMEL SERIALIZER'LAR
# ==============================================================================

# YENİ: authcentral.models.Department için serializer
class AuthDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthDepartment
        fields = ['id', 'name']

# YENİ: authcentral.models.Position için serializer
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']

class SimpleUserSerializer(serializers.ModelSerializer):
    """
    GÜNCELLEME: CustomUser modelinin zengin yapısını yansıtacak şekilde geliştirildi.
    Departman ve Pozisyon bilgilerini de içerir.
    """
    departments = AuthDepartmentSerializer(many=True, read_only=True)
    positions = PositionSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        # DÜZELTME: İstenen tüm alanlar eklendi.
        fields = ['id', 'email', 'is_active', 'is_staff', 'departments', 'positions']

class DepartmentSerializer(serializers.ModelSerializer):
    """formforgeapi.models.Department modeli için standart serializer."""
    class Meta:
        model = Department
        fields = ['id', 'name']

class FormFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldOption
        # 'form_field' alanını fields listesinden çıkarın, çünkü onu biz vereceğiz.
        fields = ["id", "label", "value", "order"] 
        read_only_fields = ["id"]

    def create(self, validated_data):
        # View'den context ile gönderdiğimiz form_field'ı burada alıp kullanıyoruz.
        form_field = self.context['form_field']
        option = FormFieldOption.objects.create(form_field=form_field, **validated_data)
        return option

# ==============================================================================
# 2. FORM YAPISI SERIALIZER'LARI
# ==============================================================================

class FormFieldSerializer(serializers.ModelSerializer):
    options = FormFieldOptionSerializer(many=True, required=False)
    class Meta:
        model = FormField
        fields = ["id", "form", "label", "field_type", "is_required", "is_master", "order", "options", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
    def create(self, validated_data):
        options_data = validated_data.pop("options", []); form_field = super().create(validated_data)
        for opt in options_data: FormFieldOption.objects.create(form_field=form_field, **opt)
        return form_field
    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None); form_field = super().update(instance, validated_data)
        if options_data is not None:
            instance.options.all().delete()
            for opt in options_data: FormFieldOption.objects.create(form_field=instance, **opt)
        return form_field

class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by = SimpleUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    versions = serializers.StringRelatedField(many=True, read_only=True) 
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'department', 'department_name', 'created_by', 'fields', 'status', 'status_display', 'parent_form', 'version', 'versions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'department_name', 'status_display', 'versions']

# ==============================================================================
# 3. FORM GÖNDERİMİ (SUBMISSION) SERIALIZER'LARI
# ==============================================================================

class SubmissionValueSerializer(serializers.ModelSerializer):
    form_field_label = serializers.CharField(source='form_field.label', read_only=True)
    class Meta:
        model = SubmissionValue
        fields = ['id', 'form_field', 'form_field_label', 'value']
        read_only_fields = ['id', 'form_field_label']

    def to_representation(self, instance):
        representation = super().to_representation(instance); field_type = instance.form_field.field_type; value = representation['value']
        if field_type == FieldTypes.MULTI_SELECT and isinstance(value, str):
            try: representation['value'] = json.loads(value)
            except json.JSONDecodeError: representation['value'] = []
        elif field_type == FieldTypes.USER_PICKER and value:
            User = get_user_model()
            try:
                user = User.objects.get(pk=value)
                representation['value'] = SimpleUserSerializer(user).data
            except User.DoesNotExist:
                representation['value'] = {'id': value, 'email': 'Bilinmeyen Kullanıcı'}
        elif field_type == FieldTypes.DEPARTMENT_PICKER and value:
            try:
                department = Department.objects.get(pk=value)
                representation['value'] = DepartmentSerializer(department).data
            except Department.DoesNotExist:
                representation['value'] = {'id': value, 'name': 'Bilinmeyen Departman'}
        return representation

class FormSubmissionSerializer(serializers.ModelSerializer):
    values = SubmissionValueSerializer(many=True, read_only=True)
    created_by = SimpleUserSerializer(read_only=True)
    
    # DÜZELTME: Bu satıra 'source' parametresi eklendi.
    # Bu, serializer'a API'de alan adının 'versions' olarak kalacağını,
    # ama veriyi modeldeki 'submission_versions' ilişkisinden çekeceğini söyler.
    versions = serializers.StringRelatedField(many=True, read_only=True, source='submission_versions')
    
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmission
        # 'fields' listesi aynı kalabilir, çünkü alanın API'deki adı hala 'versions' olacak.
        fields = ['id', 'form', 'created_by', 'values', 'created_at', 'updated_at', 'parent_submission', 'version', 'is_active', 'versions', 'is_owner']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'versions', 'is_owner']

    def get_is_owner(self, obj):
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated: return False
        return obj.created_by == request.user

    def create(self, validated_data):
        values_data = self.context['request'].data.get('values', [])
        form_instance = validated_data.get('form')
        user = self.context['request'].user
        return formforgeapi_service.create_submission(
            form_id=form_instance.id,
            values_data=values_data,
            user=user
        )