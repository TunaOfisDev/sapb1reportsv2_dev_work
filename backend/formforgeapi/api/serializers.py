# backend/formforgeapi/api/serializers.py
import json
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue, FormFieldOption

# ==============================================================================
# 1. TEMEL SERIALIZER'LAR
# ==============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Sadece temel kullanıcı bilgilerini (ID ve email) döndürür."""
    class Meta:
        model = get_user_model()
        fields = ['id', 'email']

class DepartmentSerializer(serializers.ModelSerializer):
    """Departman modeli için standart serializer."""
    class Meta:
        model = Department
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class FormFieldOptionSerializer(serializers.ModelSerializer):
    """Select, Checkbox gibi alanların seçenekleri için serializer."""
    label = serializers.CharField(allow_blank=False, allow_null=False)

    class Meta:
        model = FormFieldOption
        fields = ["id", "label", "order"]
        read_only_fields = ["id"]

    def validate_label(self, value):
        if not value.strip():
            raise serializers.ValidationError("Seçenek etiketi boş olamaz.")
        return value.strip()

# ==============================================================================
# 2. FORM YAPISI SERIALIZER'LARI
# ==============================================================================

class FormFieldSerializer(serializers.ModelSerializer):
    """
    Form alanlarını ve iç içe seçeneklerini yönetir.
    create/update metodları ile seçeneklerin de kaydedilmesini sağlar.
    """
    options = FormFieldOptionSerializer(many=True, required=False)

    class Meta:
        model = FormField
        fields = [
            "id", "form", "label", "field_type",
            "is_required", "is_master", "order",
            "options",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        form_field = super().create(validated_data)
        for opt in options_data:
            FormFieldOption.objects.create(form_field=form_field, **opt)
        return form_field

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)
        form_field = super().update(instance, validated_data)

        if options_data is not None:
            instance.options.all().delete()
            for opt in options_data:
                FormFieldOption.objects.create(form_field=instance, **opt)
        return form_field

class FormSerializer(serializers.ModelSerializer):
    """
    Ana Form şeması için serializer. 
    Form alanlarını iç içe (nested) ve salt okunur olarak içerir.
    """
    fields = FormFieldSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by = SimpleUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    versions = serializers.StringRelatedField(many=True, read_only=True) 

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description', 'department', 'department_name', 
            'created_by', 'fields', 
            'status', 'status_display', 'parent_form', 'version', 'versions',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 
            'department_name', 'status_display', 'versions'
        ]

# ==============================================================================
# 3. FORM GÖNDERİMİ (SUBMISSION) SERIALIZER'LARI
# ==============================================================================

class SubmissionValueSerializer(serializers.ModelSerializer):
    """
    Bir gönderimdeki tek bir alanın değerini temsil eder.
    Çoklu seçim verilerini JSON'dan listeye çevirir.
    """
    form_field_label = serializers.CharField(source='form_field.label', read_only=True)

    class Meta:
        model = SubmissionValue
        fields = ['id', 'form_field', 'form_field_label', 'value']
        read_only_fields = ['id', 'form_field_label']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Çoklu seçim alanlarının string olarak saklanan JSON verisini frontend için listeye çevir.
        if instance.form_field.field_type == 'multiselect' and isinstance(representation['value'], str):
            try:
                representation['value'] = json.loads(representation['value'])
            except json.JSONDecodeError:
                representation['value'] = [] # Hatalı JSON durumunda boş liste döndür.
        return representation

class FormSubmissionSerializer(serializers.ModelSerializer):
    """
    Form gönderimlerini ve iç içe değerlerini yöneten ana serializer.
    Hem normal listeleme hem de 'history' action'ı için kullanılır.
    """
    # DÜZELTME: values alanı 'read_only=True' olarak ayarlandı.
    # Bu, DRF'in yazma (create/update) işlemlerinde bu alanı kendi doğrulamasından geçirmesini engeller.
    # Yazma mantığı tamamen aşağıdaki 'create' metodu tarafından yönetilecektir.
    values = SubmissionValueSerializer(many=True, read_only=True)
    
    created_by = SimpleUserSerializer(read_only=True)
    versions = serializers.StringRelatedField(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form', 'created_by', 'values', 'created_at', 'updated_at', 
            'parent_submission', 'version', 'is_active', 'versions', 
            'is_owner'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 'versions', 
            'is_owner'
        ]

    def get_is_owner(self, obj):
        """İsteği yapan kullanıcının bu gönderinin sahibi olup olmadığını kontrol eder."""
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return obj.created_by == request.user

    def create(self, validated_data):
        """
        Yeni bir form gönderimi oluşturur.
        Frontend'den gelen 'values' verisini işler.
        """
        values_data = self.context['request'].data.get('values', [])
        form_instance = validated_data.get('form')

        form_submission = FormSubmission.objects.create(
            form=form_instance,
            created_by=self.context['request'].user
        )

        field_types = {field.id: field.field_type for field in form_instance.fields.all()}

        for value_data in values_data:
            field_id = value_data.get('form_field')
            value = value_data.get('value')
            
            value_to_save = value
            # Çoklu seçim ise ve gelen veri liste ise, veritabanına JSON string olarak kaydet.
            if field_types.get(field_id) == 'multiselect' and isinstance(value, list):
                value_to_save = json.dumps(value, ensure_ascii=False)
            elif value is not None:
                value_to_save = str(value)
            else:
                value_to_save = ''

            if field_id:
                SubmissionValue.objects.create(
                    submission=form_submission,
                    form_field_id=field_id,
                    value=value_to_save
                )
        
        return form_submission