# backend/logosupplierbalance/api/serializers.py
from rest_framework import serializers
from ..models.models import SupplierBalance

class LogoSupplierBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierBalance
        fields = '__all__'

    def create(self, validated_data):
        return SupplierBalance.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
