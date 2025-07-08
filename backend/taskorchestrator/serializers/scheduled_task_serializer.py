# backend/taskorchestrator/serializers/scheduled_task_serializer.py

from rest_framework import serializers
from inspect import signature
from django.utils.module_loading import import_string
from taskorchestrator.models.task_definition import TaskDefinition
from taskorchestrator.models.scheduled_task import ScheduledTask

class ScheduledTaskSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    crontab_schedule = serializers.CharField(source='crontab.__str__', read_only=True)

    class Meta:
        model = ScheduledTask
        fields = [
            "id",
            "name",
            "task",           # FK (ID)
            "task_name",      # Readable task name
            "crontab",        # FK (ID)
            "crontab_schedule",  # Readable cron
            "parameters",
            "enabled",
            "last_run_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_run_at", "created_at", "updated_at"]

    def validate_parameters(self, value):
        """
        • JSON dict olup olmadığını kontrol eder  
        • İlgili TaskDefinition fonksiyon imzasındaki parametre adlarıyla eşleştirir  
        – eşleşmeyen anahtar varsa ValidationError fırlatır
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Görev parametreleri JSON nesnesi (dict) olmalıdır."
            )

        # --- Fonksiyon yolu (function_path) tespiti ---------------------------
        func_path = None

        # • POST/PUT sırasında gelen task FK’si
        task_id = self.initial_data.get("task")
        if task_id:
            try:
                func_path = TaskDefinition.objects.get(pk=task_id).function_path
            except TaskDefinition.DoesNotExist:
                pass

        # • Mevcut instance güncelleniyorsa
        if not func_path and self.instance:
            func_path = self.instance.task.function_path
        # ----------------------------------------------------------------------

        # --- İmza kontrolü -----------------------------------------------------
        if func_path:
            try:
                valid_keys = set(signature(import_string(func_path)).parameters.keys())
                invalid   = set(value.keys()) - valid_keys
                if invalid:
                    raise serializers.ValidationError(
                        f"Parametre adı/ları uyuşmuyor: {', '.join(invalid)}. "
                        f"Beklenen anahtarlar: {', '.join(valid_keys) or '—'}"
                    )
            except Exception:
                # import veya signature hatası olursa doğrulamayı zorlamıyoruz
                pass
        # ----------------------------------------------------------------------

        return value
