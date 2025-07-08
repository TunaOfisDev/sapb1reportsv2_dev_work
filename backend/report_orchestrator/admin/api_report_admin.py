# path: backend/report_orchestrator/admin/api_report_admin.py

from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import  ImportExportMixin
from import_export import resources
from report_orchestrator.models.api_report_model import APIReportModel


class APIReportModelResource(resources.ModelResource):
    class Meta:
        model = APIReportModel
        exclude = ("id", "created_at", "updated_at")  # Gerekirse dahil edebilirsin
        import_id_fields = ("api_name",)
        skip_unchanged = True
        report_skipped = True


@admin.register(APIReportModel)
class APIReportModelAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = APIReportModelResource

    list_display = (
        "api_name", "mode", "is_active", "last_run_colored", "has_error", "short_rule", "short_result"
    )
    list_filter = ("mode", "is_active",)
    search_fields = ("api_name",)
    readonly_fields = ("result_json", "last_run_at", "last_error_message", "created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("api_name", "mode", "is_active")
        }),
        ("Veri Çekme Ayarları", {
            "fields": ("trigger_url", "data_pull_url", "wait_seconds")
        }),
        ("Kural ve Özet Veri", {
            "fields": ("rule_json", "result_json")
        }),
        ("İzleme", {
            "fields": ("last_run_at", "last_error_message", "created_at", "updated_at")
        }),
    )

    def last_run_colored(self, obj):
        if obj.last_run_at:
            return format_html(
                '<span style="color:green;">{}</span>',
                obj.last_run_at.strftime("%d.%m.%Y %H:%M")
            )
        return format_html('<span style="color:red;">Çalışmadı</span>')
    last_run_colored.short_description = "Son Çalışma"

    def has_error(self, obj):
        return bool(obj.last_error_message)
    has_error.boolean = True
    has_error.short_description = "Hata?"

    def short_rule(self, obj):
        if not obj.rule_json:
            return "-"
        return str(obj.rule_json)[:80] + "..."
    short_rule.short_description = "Kural Özeti"

    def short_result(self, obj):
        if not obj.result_json:
            return "-"
        return str(obj.result_json)[:80] + "..."
    short_result.short_description = "Özet Veri"
