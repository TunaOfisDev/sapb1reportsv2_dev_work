# path: backend/formforgeapi/api/serializers.py
import json # json modülünü import ediyoruz
from rest_framework import serializers
from django.contrib.auth import get_user_model
# FormField modelini import etmemiz gerekiyor
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue, FormFieldOption

# Kullanıcı bilgilerini (ID ve username) göstermek için basit bir serializer
# Bu, created_by alanını sadece bir ID yerine bir obje olarak döndürmemizi sağlar.
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email'] # Frontend'de ihtiyaç duyabileceğiniz alanlar

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class FormFieldOptionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(allow_blank=False, allow_null=False)

    class Meta:
        model  = FormFieldOption
        fields = ["id", "label", "order"]
        read_only_fields = ["id"]

    def validate_label(self, value):
        if not value.strip():
            raise serializers.ValidationError("Boş olamaz")
        return value.strip()

class FormFieldSerializer(serializers.ModelSerializer):
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

# --- GÜNCELLENEN BÖLÜM BAŞLANGICI ---

# GÜNCELLEME 1: "Görüntüle" modalı için alan etiketini ekliyoruz.
class SubmissionValueSerializer(serializers.ModelSerializer):
    form_field_label = serializers.CharField(source='form_field.label', read_only=True)

    class Meta:
        model = SubmissionValue
        fields = ['id', 'form_field', 'form_field_label', 'value']
        read_only_fields = ['id', 'form_field_label']

    # GÜNCELLEME: Veriyi frontend'e gönderirken JSON'ı listeye çevir
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Eğer alan çoklu seçim ise ve değer bir string ise, onu JSON'dan Python listesine çevirmeyi dene.
        if instance.form_field.field_type == FormField.FieldTypes.MULTI_SELECT and isinstance(representation['value'], str):
            try:
                representation['value'] = json.loads(representation['value'])
            except json.JSONDecodeError:
                # Hatalı veya boş bir string ise, boş bir liste olarak göster
                representation['value'] = []
        return representation

# GÜNCELLEME 2: Frontend'e zengin veri sağlamak için güncellendi.
class FormSubmissionSerializer(serializers.ModelSerializer):
    values = SubmissionValueSerializer(many=True, required=False)
    created_by = SimpleUserSerializer(read_only=True)
    versions = serializers.StringRelatedField(many=True, read_only=True)
    
    # Bu alan, isteği yapan kullanıcının bu gönderinin sahibi olup olmadığını belirtir.
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmission
        fields = [
            'id', 'form', 'created_by', 'values', 'created_at', 'updated_at', 
            'parent_submission', 'version', 'is_active', 'versions', 
            'is_owner'  # 'is_owner' alanı eklendi
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 'versions', 
            'is_owner'  # 'is_owner' alanı eklendi
        ]

    def get_is_owner(self, obj):
        """
        Serializer'a `is_owner` alanının değerini döndüren metod.
        Gönderiyi oluşturan kişi (obj.created_by) ile isteği yapan kişi (request.user) aynı mı diye kontrol eder.
        """
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return obj.created_by == request.user

    def create(self, validated_data):
        """
        Yeni bir form gönderimi oluşturur ve çoklu seçim alanlarını doğru bir şekilde işler.
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
            
            if field_types.get(field_id) == FormField.FieldTypes.MULTI_SELECT and isinstance(value, list):
                value_to_save = json.dumps(value, ensure_ascii=False)
            else:
                value_to_save = str(value) if value is not None else ''

            if field_id:
                SubmissionValue.objects.create(
                    submission=form_submission,
                    form_field_id=field_id,
                    value=value_to_save
                )
        
        return form_submission


# --- GÜNCELLENEN BÖLÜM SONU ---


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    # GÜNCELLEME 3: Form listesinde de oluşturan kullanıcıyı zengin formatta gösterelim.
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
        # `created_by` artık bir obje olduğu için `read_only_fields`'da kalmalı.
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 
                            'department_name', 'status_display', 'versions']