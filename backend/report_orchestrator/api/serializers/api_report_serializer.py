# backend/report_orchestrator/api/serializers/api_report_serializer.py

from rest_framework import serializers
from report_orchestrator.models.api_report_model import APIReportModel


class APIReportSerializer(serializers.ModelSerializer):
    """
    APIReportModel verisini serialize eder.
    Bu serializer hem listeleme hem detay gösterim hem de güncelleme amaçlı kullanılabilir.
    """

    status_label = serializers.SerializerMethodField()
    mode_label = serializers.SerializerMethodField()

    class Meta:
        model = APIReportModel
        fields = [
            "id",
            "api_name",
            "mode",
            "mode_label",
            "trigger_url",
            "data_pull_url",
 
            "wait_seconds",
            "rule_json",
            "result_json",
            "last_error_message",
            "last_run_at",
            "is_active",
            "status_label",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "result_json",
            "last_error_message",
            "last_run_at",
            "created_at",
            "updated_at",
            "status_label",
            "mode_label"
        ]

    def get_status_label(self, obj):
        if not obj.is_active:
            return "Pasif (Çalışmıyor)"
        elif obj.last_error_message:
            return "Son çalışmada hata var"
        elif obj.last_run_at:
            return f"Son çalıştı: {obj.last_run_at.strftime('%d.%m.%Y %H:%M')}"
        return "Hazır"

    def get_mode_label(self, obj):
        return dict(obj.MODE_CHOICES).get(obj.mode, "Tanımsız mod")

