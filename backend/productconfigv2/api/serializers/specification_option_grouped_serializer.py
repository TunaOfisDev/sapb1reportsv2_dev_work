# backend/productconfigv2/api/serializers/specification_option_grouped_serializer.py

from rest_framework import serializers
from ...models import SpecOption


class SpecOptionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecOption
        fields = [
            'id',
            'name',
            'variant_code',
            'variant_description',
            'price_delta',
        ]


class SpecificationOptionGroupedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_required = serializers.BooleanField()
    allow_multiple = serializers.BooleanField()
    variant_order = serializers.IntegerField()
    options = SpecOptionNestedSerializer(many=True)
