# productconfigv2/api/serializers/variant_serializers.py

from rest_framework import serializers
from ...models import Variant, VariantSelection


class VariantSelectionSerializer(serializers.ModelSerializer):
    spec_type = serializers.StringRelatedField()
    option = serializers.StringRelatedField()

    class Meta:
        model = VariantSelection
        fields = ["id", "spec_type", "option"]


class VariantSerializer(serializers.ModelSerializer):
    selections = VariantSelectionSerializer(many=True, read_only=True)

    class Meta:
        model = Variant
        fields = [
            "id", "product", "new_variant_code", "new_variant_description", "image",
            "total_price", "currency", "is_generated", "selections"
        ]