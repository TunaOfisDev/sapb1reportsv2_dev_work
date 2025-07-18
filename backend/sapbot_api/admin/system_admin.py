# backend/sapbot_api/admin/system_admin.py
"""
SAPBot API - Sistem modelleri için Django Admin tanımları
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from ..models.system import (
    SystemConfiguration,
    SystemMetrics,
    SystemLog,
    SystemHealth,
    APIQuota,
    SystemNotification,
    MaintenanceWindow,
)

# Temel / mix-in sınıflar
from .base_admin import (
    BaseModelAdmin,
    ExportableModelAdmin,
    BulkActionModelAdmin,
    OptimizedQuerysetMixin,
    HealthCheckMixin,
    ColoredBooleanMixin,
    JSONFieldMixin,
    TimestampMixin,
    StatisticsMixin,
    LinkMixin,
    admin_action_required_permission,
)

# ---------------------------------------------------------------------------
# 1) SystemConfiguration
# ---------------------------------------------------------------------------


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(
    ExportableModelAdmin,
    BulkActionModelAdmin,
    OptimizedQuerysetMixin,
    JSONFieldMixin,
    ColoredBooleanMixin,
    TimestampMixin,
):
    """Sistem konfigürasyonu admin"""

    list_display = (
        "key",
        "display_value",
        "config_type",
        "category",
        "colored_is_sensitive",
        "is_editable",
        "formatted_updated_at",
        "updated_by",
    )
    list_filter = ("config_type", "category", "is_sensitive", "is_editable", "updated_at")
    search_fields = ("key", "value", "description")
    readonly_fields = ("created_at", "updated_at", "updated_by")
    fieldsets = (
        (
            "Konfigürasyon",
            {
                "fields": (
                    "key",
                    "config_type",
                    "value",
                    "category",
                    "description",
                )
            },
        ),
        (
            "Ek Özellikler",
            {
                "fields": (
                    "is_sensitive",
                    "is_editable",
                    "default_value",
                    "validation_regex",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Sistem",
            {
                "fields": ("id", "created_at", "updated_at", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def display_value(self, obj):
        """Hassas değerleri maskele."""
        if obj.is_sensitive and not self.has_full_value_permission:
            return "•••"
        # JSON & Liste verilerini kısalt
        if obj.config_type in ("json", "list"):
            prettied = self.formatted_json(obj, "value")
            return prettied or "-"
        val = obj.get_typed_value()
        return str(val)[:120]  # uzun değerleri kes
    display_value.short_description = "Değer"

    # ---- Renklendirmeler & izinler ----------------------------------------
    def colored_is_sensitive(self, obj):
        return self.colored_boolean(obj, "is_sensitive")
    colored_is_sensitive.short_description = "Hassas?"

    # ---- İzin kontrolleri --------------------------------------------------
    @property
    def has_full_value_permission(self):
        request = getattr(self, "_request", None)
        return request and request.user.is_superuser

    # request nesnesine erişebilmek için
    def get_queryset(self, request):
        self._request = request  # küçük hile
        return super().get_queryset(request)

    # ---- Özel aksiyon: Varsayılana sıfırla -------------------------------
    @admin_action_required_permission("sapbot_api.change_systemconfiguration")
    def reset_to_default(self, request, queryset):
        reset = 0
        for obj in queryset:
            if obj.default_value:
                obj.value = obj.default_value
                obj.save(update_fields=["value", "updated_at"])
                reset += 1
        self.message_user(request, f"{reset} konfigürasyon varsayılana döndürüldü.")
    reset_to_default.short_description = "Seçilenleri varsayılana döndür"

    actions = ExportableModelAdmin.actions + ["reset_to_default"]


# ---------------------------------------------------------------------------
# 2) SystemMetrics
# ---------------------------------------------------------------------------


@admin.register(SystemMetrics)
class SystemMetricsAdmin(
    BaseModelAdmin,
    TimestampMixin,
    OptimizedQuerysetMixin,
):
    list_display = (
        "metric_name",
        "metric_type",
        "value",
        "labels_short",
        "formatted_created_at",
    )
    list_filter = ("metric_type", "metric_name")
    search_fields = ("metric_name",)
    readonly_fields = BaseModelAdmin.readonly_fields + ("labels_pretty", "value")

    def labels_short(self, obj):
        if not obj.labels:
            return "-"
        lbl = ", ".join(f"{k}={v}" for k, v in obj.labels.items())
        return lbl[:80] + ("…" if len(lbl) > 80 else "")
    labels_short.short_description = "Etiketler"

    def labels_pretty(self, obj):
        return self.formatted_json(obj, "labels")
    labels_pretty.short_description = "Etiketler"


# ---------------------------------------------------------------------------
# 3) SystemLog
# ---------------------------------------------------------------------------


@admin.register(SystemLog)
class SystemLogAdmin(
    ExportableModelAdmin,
    OptimizedQuerysetMixin,
    TimestampMixin,
    StatisticsMixin,
):
    list_display = (
        "level",
        "short_message",
        "module",
        "function",
        "line_number",
        "user",
        "formatted_created_at",
    )
    list_filter = ("level", "module", "user", "created_at")
    search_fields = ("message", "module", "function", "user__username", "ip_address")
    readonly_fields = (
        "level",
        "message",
        "module",
        "function",
        "line_number",
        "user",
        "session_id",
        "ip_address",
        "user_agent",
        "extra_data_pretty",
        "created_at",
    )
    ordering = ("-created_at",)

    def short_message(self, obj):
        return obj.message[:120] + ("…" if len(obj.message) > 120 else "")
    short_message.short_description = "Mesaj"

    def extra_data_pretty(self, obj):
        return self.formatted_json(obj, "extra_data")
    extra_data_pretty.short_description = "Ek Veriler"


# ---------------------------------------------------------------------------
# 4) SystemHealth
# ---------------------------------------------------------------------------


@admin.register(SystemHealth)
class SystemHealthAdmin(
    HealthCheckMixin,
    ExportableModelAdmin,
    TimestampMixin,
    OptimizedQuerysetMixin,
):
    list_display = (
        "component",
        "status_colored",
        "response_time",
        "system_health_status",
        "formatted_created_at",
    )
    list_filter = ("status", "component", "created_at")
    search_fields = ("component",)
    readonly_fields = BaseModelAdmin.readonly_fields + (
        "details_pretty",
        "response_time",
    )

    def status_colored(self, obj):
        color_map = {
            "healthy": "green",
            "warning": "orange",
            "critical": "red",
            "down": "gray",
        }
        color = color_map.get(obj.status, "gray")
        return format_html('<b style="color:{};">{}</b>', color, obj.status.upper())
    status_colored.short_description = "Durum"

    def details_pretty(self, obj):
        return self.formatted_json(obj, "details")
    details_pretty.short_description = "Detaylar"


# ---------------------------------------------------------------------------
# 5) APIQuota
# ---------------------------------------------------------------------------


@admin.register(APIQuota)
class APIQuotaAdmin(
    BulkActionModelAdmin,
    ExportableModelAdmin,
    TimestampMixin,
    ColoredBooleanMixin,
):
    list_display = (
        "endpoint",
        "user",
        "quota_type",
        "limit_count",
        "current_count",
        "usage_bar",
        "reset_at",
        "is_exceeded_colored",
    )
    list_filter = ("quota_type", "endpoint", "reset_at")
    search_fields = ("endpoint", "user__username", "api_key")
    readonly_fields = BaseModelAdmin.readonly_fields + ("usage_bar",)

    def usage_bar(self, obj):
        pct = obj.usage_percentage
        bar = f'<div style="width:120px;border:1px solid #ccc;">' \
              f'<div style="width:{pct:.0f}%;background:#4caf50;height:8px;"></div></div>'
        return format_html("{} %{:.0f}", bar, pct)
    usage_bar.short_description = "Kullanım"

    def is_exceeded_colored(self, obj):
        return self.colored_boolean(obj, "is_exceeded")
    is_exceeded_colored.short_description = "Aşıldı mı?"


# ---------------------------------------------------------------------------
# 6) SystemNotification
# ---------------------------------------------------------------------------


@admin.register(SystemNotification)
class SystemNotificationAdmin(
    ExportableModelAdmin,
    BulkActionModelAdmin,
    ColoredBooleanMixin,
    TimestampMixin,
    OptimizedQuerysetMixin,
    LinkMixin,
):
    list_display = (
        "title",
        "notification_type",
        "priority",
        "colored_is_read",
        "expires_at",
        "action_link",
        "formatted_created_at",
    )
    list_filter = ("notification_type", "priority", "is_read", "expires_at")
    search_fields = ("title", "message")
    readonly_fields = ("created_at", "updated_at")

    def colored_is_read(self, obj):
        return self.colored_boolean(obj, "is_read")
    colored_is_read.short_description = "Okundu?"

    def action_link(self, obj):
        return self.external_link(obj, "action_url", obj.action_text or "Git »")
    action_link.short_description = "Eylem"

    # Toplu işlemler
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} bildirim okundu olarak işaretlendi.")
    mark_as_read.short_description = "Seçilenleri okundu işaretle"

    actions = ExportableModelAdmin.actions + ["mark_as_read"]


# ---------------------------------------------------------------------------
# 7) MaintenanceWindow
# ---------------------------------------------------------------------------


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(
    ExportableModelAdmin,
    BulkActionModelAdmin,
    ColoredBooleanMixin,
    TimestampMixin,
    OptimizedQuerysetMixin,
):
    list_display = (
        "title",
        "status_colored",
        "start_time",
        "end_time",
        "affects_api_bool",
        "affects_chat_bool",
        "affects_upload_bool",
        "created_by",
    )
    list_filter = ("status", "start_time", "affects_api", "affects_chat")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")

    # ---- Renklendirmeler ---------------------------------------------------
    def status_colored(self, obj):
        color = {
            "scheduled": "blue",
            "in_progress": "orange",
            "completed": "green",
            "cancelled": "red",
        }.get(obj.status, "gray")
        return format_html('<b style="color:{};">{}</b>', color, obj.get_status_display())
    status_colored.short_description = "Durum"

    def affects_api_bool(self, obj):
        return self.colored_boolean(obj, "affects_api")
    affects_api_bool.short_description = "API"

    def affects_chat_bool(self, obj):
        return self.colored_boolean(obj, "affects_chat")
    affects_chat_bool.short_description = "Chat"

    def affects_upload_bool(self, obj):
        return self.colored_boolean(obj, "affects_upload")
    affects_upload_bool.short_description = "Upload"


# ---------------------------------------------------------------------------
# Admin site genel başlık vb. ayarları
# ---------------------------------------------------------------------------

from .base_admin import customize_admin_site

customize_admin_site()

