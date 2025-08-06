# path: backend/formforgeapi/api/serializers.py
from rest_framework import serializers
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue, FormFieldOption

# Gereksiz ve hatalı FormFieldSerializer tanımını siliyoruz veya yorum satırı yapıyoruz.
# class FormFieldSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = FormField
#        fields = ['id', 'form', 'label', 'field_type', 'is_required', 'is_master', 'order', 'created_at', 'updated_at']
#        read_only_fields = ['created_at', 'updated_at']

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

# Bu, artık FormField için tek ve doğru serializer tanımıdır.
class FormFieldSerializer(serializers.ModelSerializer):
    options = FormFieldOptionSerializer(many=True, required=False)

    class Meta:
        model = FormField
        fields = [
            "id", "form", "label", "field_type",
            "is_required", "is_master", "order",
            "options",           # 👈 Seçenekler artık kalıcı olarak burada!
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    # create / update içinde nested options yönetimi
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
            # Basit strateji: mevcut seçenekleri sil, yenilerini ekle
            instance.options.all().delete()
            for opt in options_data:
                FormFieldOption.objects.create(form_field=instance, **opt)
        return form_field

class SubmissionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionValue
        # 'submission' alanı nested serializer'da zorunlu olmamalı
        fields = ['id', 'submission', 'form_field', 'value', 'created_at', 'updated_at']
        read_only_fields = ['id', 'submission', 'created_at', 'updated_at']

class FormSubmissionSerializer(serializers.ModelSerializer):
    values = SubmissionValueSerializer(many=True)

    class Meta:
        model = FormSubmission
        fields = ['id', 'form', 'created_by', 'values', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        values_data = validated_data.pop('values')
        # request.user'ı almak için `created_by`'ı validated_data'ya ekle
        validated_data['created_by'] = self.context['request'].user
        form_submission = FormSubmission.objects.create(**validated_data)
        for value_data in values_data:
            # submission değeri otomatik olarak atanıyor
            SubmissionValue.objects.create(submission=form_submission, **value_data)
        return form_submission

class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    # YENİ: status alanını okunabilir formatta almak için
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # YENİ: Versiyonları iç içe göstermek için
    versions = serializers.StringRelatedField(many=True) 

    class Meta:
        model = Form
        fields = [
            'id', 'title', 'description', 'department', 'department_name', 
            'created_by', 'created_by_username', 'fields', 
            'status', 'status_display', 'parent_form', 'version', 'versions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_username']