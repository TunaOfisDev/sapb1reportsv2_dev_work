# backend/taskorchestrator/serializers/task_definition_serializer.py

from rest_framework import serializers
from taskorchestrator.models.task_definition import TaskDefinition

class TaskDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDefinition
        fields = [
            "id",
            "name",
            "function_path",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_function_path(self, value):
        """
        Görev fonksiyon yolu gerçekten import edilebilir mi?
        """
        from django.utils.module_loading import import_string
        try:
            func = import_string(value)
        except Exception as e:
            raise serializers.ValidationError(f"Fonksiyon import edilemedi: {e}")
        return value
