# backend/productconfigv2/api/serializers/variant_serializers.py
from rest_framework import serializers
from ...models import Variant, VariantSelection 
from django.contrib.auth import get_user_model

User = get_user_model()

class VariantSelectionSerializer(serializers.ModelSerializer):
    spec_type = serializers.StringRelatedField()
    option = serializers.StringRelatedField()

    class Meta:
        model = VariantSelection
        fields = ["id", "spec_type", "option"]


class VariantSerializer(serializers.ModelSerializer):
    selections = VariantSelectionSerializer(many=True, read_only=True)
    created_by_username = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Variant
        fields = [
            "id", 
            "product",
            "product_name",
            "project_name", 
            "reference_code", 
            "new_variant_code", 
            "new_variant_description", 
            "image",
            "total_price", 
            "currency", 
            "is_generated",
            "created_at",
            "created_by_username",
            "selections"
        ]

    def get_created_by_username(self, obj):
        if obj.created_by and obj.created_by.email:
            return obj.created_by.email.split('@')[0]
        return "Bilinmiyor"