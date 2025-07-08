# productconfigv2/api/serializers/specification_serializers.py

from rest_framework import serializers
from ...models import (
    SpecificationType, SpecOption,
    ProductSpecification, SpecificationOption
)


class SpecOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecOption
        fields = [
            "id", "name", "variant_code", "variant_description", "image",
            "price_delta", "is_default", "display_order"
        ]


class SpecificationTypeSerializer(serializers.ModelSerializer):
    options = SpecOptionSerializer(many=True, read_only=True)

    class Meta:
        model = SpecificationType
        fields = [
            "id", "name", "group",
            "is_required", "allow_multiple",
            "variant_order", "display_order", "multiplier",
            "options"
        ]


class ProductSpecificationSerializer(serializers.ModelSerializer):
    spec_type = SpecificationTypeSerializer(read_only=True)

    class Meta:
        model = ProductSpecification
        fields = ["id", "spec_type", "is_required", "allow_multiple", "variant_order", "display_order"]


class SpecificationOptionSerializer(serializers.ModelSerializer):
    option = SpecOptionSerializer()

    class Meta:
        model = SpecificationOption
        fields = ["id", "spec_type", "option", "is_default", "display_order"]
