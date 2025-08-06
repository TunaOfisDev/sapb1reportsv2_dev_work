# path: backend/formforgeapi/api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
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
    # Bu alan, `form_field` ID'si üzerinden ilgili alanın `label`'ını otomatik olarak çeker.
    form_field_label = serializers.CharField(source='form_field.label', read_only=True)

    class Meta:
        model = SubmissionValue
        fields = ['id', 'form_field', 'form_field_label', 'value'] # Sadeleştirilmiş alanlar
        read_only_fields = ['id', 'form_field_label']

# GÜNCELLEME 2: Frontend'e zengin veri sağlamak için güncellendi.
class FormSubmissionSerializer(serializers.ModelSerializer):
    # `values` alanı artık güncellenmiş `SubmissionValueSerializer`'ı kullanacak.
    values = SubmissionValueSerializer(many=True)
    
    # `created_by` alanını ID yerine kullanıcı objesi olarak döndürmek için.
    # Bu sayede frontend hem ID'ye (user.id) hem de username'e (user.username) erişebilir.
    created_by = SimpleUserSerializer(read_only=True)

    class Meta:
        model = FormSubmission
        fields = ['id', 'form', 'created_by', 'values', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        # 'created_by' bilgisi view'dan context ile geldiği için `validated_data`'dan çıkarılır.
        values_data = validated_data.pop('values')
        
        # `perform_create` metodunu view'da kullandığımız için 'created_by' ataması burada gereksiz.
        # Eğer view'da atama yapılmıyorsa bu satır kalmalı:
        # validated_data['created_by'] = self.context['request'].user
        
        form_submission = FormSubmission.objects.create(**validated_data)
        for value_data in values_data:
            SubmissionValue.objects.create(submission=form_submission, **value_data)
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