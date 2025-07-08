# productconfigv2/api/serializers/product_serializers.py

from rest_framework import serializers
from ...models import ProductFamily, Product


class ProductFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFamily
        fields = ["id", "name", "image"]


class ProductSerializer(serializers.ModelSerializer):
    family = ProductFamilySerializer(read_only=True)
    family_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductFamily.objects.all(), write_only=True, source="family"
    )

    class Meta:
        model = Product
        fields = [
            "id", "code", "name", "image",
            "variant_code", "variant_description",
            "base_price", "currency", "variant_order",
            "family", "family_id"
        ]
