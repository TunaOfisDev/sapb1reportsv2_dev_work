# backend/logocustomerbalance/serializers.py
from rest_framework import serializers
from .models.models import CustomerBalance

class LogoCustomerBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBalance
        fields = '__all__'

    def create(self, validated_data):
        return CustomerBalance.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
