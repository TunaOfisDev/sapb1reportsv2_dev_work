# productconfigv2/api/serializers/rule_serializers.py

from rest_framework import serializers
from ...models import Rule


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = [
            "id", "product_family", "rule_type", "name",
            "conditions", "actions"
        ]