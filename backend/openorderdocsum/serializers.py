# backend/openorderdocsum/serializers.py
from rest_framework import serializers
from .models.openorderdeail import OpenOrderDetail
from .models.docsum import DocumentSummary

class OpenOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenOrderDetail
        fields = '__all__'

    def create(self, validated_data):
        uniq_detail_no = validated_data.get('uniq_detail_no')
        instance, created = OpenOrderDetail.objects.update_or_create(
            uniq_detail_no=uniq_detail_no,
            defaults={k: v for k, v in validated_data.items() if k != 'uniq_detail_no'}
        )
        return instance

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

class DocumentSummarySerializer(serializers.ModelSerializer):
    belge_iskonto_oran = serializers.FloatField(read_only=True)  # `source` argümanını kaldırdık

    class Meta:
        model = DocumentSummary
        fields = '__all__'  # Tüm alanları içerir

    def create(self, validated_data):
        document_number = validated_data.get('document_number')
        instance, created = DocumentSummary.objects.update_or_create(
            document_number=document_number,
            defaults={k: v for k, v in validated_data.items() if k != 'document_number'}
        )
        return instance

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

