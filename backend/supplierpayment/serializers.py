# backend/supplierpayment/serializers.py
from rest_framework import serializers
from .models.models import SupplierPayment
from .models.closinginvoice import ClosingInvoice
import json

class SupplierPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierPayment
        fields = '__all__'

    def create(self, validated_data):
        return SupplierPayment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

class ClosingInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosingInvoice
        fields = '__all__'

    def create(self, validated_data):
        return ClosingInvoice.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Eğer monthly_balances bir string ise, JSON'a çevir
        if isinstance(representation['monthly_balances'], str):
            representation['monthly_balances'] = json.loads(representation['monthly_balances'])
        return representation

