
# backend/report_orchestrator/admin/api_execution_log_admin.py
from django.contrib import admin
from django.utils.html import format_html
from report_orchestrator.models.api_execution_log import APIExecutionLog


@admin.register(APIExecutionLog)
class APIExecutionLogAdmin(admin.ModelAdmin):
    list_display = (
        'api_name_display',
        'status_colored',
        'run_date',
        'run_time',
        'duration_seconds',
        'short_error'
    )
    list_filter = ('status', 'api__api_name', 'run_date')
    search_fields = ('api__api_name', 'error_message')
    readonly_fields = ('api', 'status', 'error_message', 'run_date', 'run_time', 'duration_seconds')
    ordering = ('-run_time',)

    def api_name_display(self, obj):
        return obj.api.api_name
    api_name_display.short_description = "API Adı"

    def status_colored(self, obj):
        color = 'green' if obj.status == 'SUCCESS' else 'red'
        return format_html(f'<b style="color:{color}">{obj.status}</b>')
    status_colored.short_description = "Durum"

    def short_error(self, obj):
        if obj.error_message:
            return (obj.error_message[:75] + '...') if len(obj.error_message) > 75 else obj.error_message
        return "-"
    short_error.short_description = "Hata Mesajı"

    from django.utils.html import format_html
