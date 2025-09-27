# /var/www/sapb1reportsv2/backend/deliverydocsumv2/serializers.py
from rest_framework import serializers
from .models.models import DeliveryDocSummary
from datetime import datetime

class DeliveryDocSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDocSummary
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        instance, created = DeliveryDocSummary.objects.update_or_create(
            cari_kod=validated_data.get('cari_kod', None),
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class DeliveryDocSummaryFormattedSerializer(serializers.ModelSerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryDocSummary
        fields = '__all__'

    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y')

