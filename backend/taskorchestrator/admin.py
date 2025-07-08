# backend/taskorchestrator/admin.py

from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin  # 🔁 İçe/dışa aktarım desteği
from .models.task_definition import TaskDefinition
from .models.scheduled_task import ScheduledTask


@admin.register(TaskDefinition)
class TaskDefinitionAdmin(ImportExportModelAdmin):  # ⬅️ Burada değişti
    list_display = ("name", "function_path", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "function_path", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("name", "function_path", "description", "is_active")
        }),
        ("Zaman Bilgisi", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(ImportExportModelAdmin):  # ⬅️ Burada da değişti
    list_display = (
        "name", "task", "enabled", "colored_crontab", "last_run_at", "created_at"
    )
    list_filter = ("enabled", "crontab")
    search_fields = ("name", "task__name")
    ordering = ("-enabled", "name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("name", "task", "crontab", "parameters", "enabled", "notes")
        }),
        ("Zaman Bilgisi", {
            "fields": ("last_run_at", "created_at", "updated_at"),
        }),
    )

    def colored_crontab(self, obj):
        return format_html(
            '<span style="color: #2b6cb0;">{}</span>',
            obj.crontab.__str__()
        )
    colored_crontab.short_description = "Crontab"
