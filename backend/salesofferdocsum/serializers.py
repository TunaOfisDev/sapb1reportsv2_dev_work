# backend/salesofferdocsum/serializers.py
from rest_framework import serializers
from .models.salesofferdetail import SalesOfferDetail
from .models.docsum import DocumentSummary

class SalesOfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOfferDetail
        fields = '__all__'

    def create(self, validated_data):
        return SalesOfferDetail.objects.create(**validated_data)

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
        return DocumentSummary.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


