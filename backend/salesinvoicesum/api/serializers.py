# backend/salesinvoicesum/api/serializers.py
from rest_framework import serializers
from ..models.sales_invoice_sum_model import SalesInvoiceSum

class SalesInvoiceSumSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoiceSum
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        instance, created = SalesInvoiceSum.objects.update_or_create(
            customer_code=validated_data.get('customer_code', None),
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class SalesInvoiceSumFormattedSerializer(serializers.ModelSerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = SalesInvoiceSum
        fields = '__all__'

    def get_updated_at(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y')
