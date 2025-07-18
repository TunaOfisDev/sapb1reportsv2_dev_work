# backend/sapbot_api/admin/user_admin.py
"""
SAPBot API – Kullanıcıyla ilgili modeller için Django-Admin tanımları
"""
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone

from ..models.user import (
    UserProfile,
    UserPreferences,
    UserSession,
    UserActivity,
    UserApiKey,
)

# Ortak admin temel sınıfları & mix-in’leri
from .base_admin import (
    BaseModelAdmin,
    ExportableModelAdmin,
    BulkActionModelAdmin,
    OptimizedQuerysetMixin,
    ColoredBooleanMixin,
    TimestampMixin,
    JSONFieldMixin,
    LinkMixin,
    admin_action_required_permission,
)

# ---------------------------------------------------------------------
# 1) UserProfile
# ---------------------------------------------------------------------


@admin.register(UserProfile)
class UserProfileAdmin(
    ExportableModelAdmin,
    BulkActionModelAdmin,
    OptimizedQuerysetMixin,
    ColoredBooleanMixin,
    TimestampMixin,
    LinkMixin,
):
    list_display = (
        "user_link",
        "display_name",
        "user_type",
        "preferred_language",
        "colored_is_beta",
        "email_notif",
        "push_notif",
        "formatted_last_activity",
    )
    list_filter = ("user_type", "preferred_language", "is_beta_user", "email_notifications", "push_notifications")
    search_fields = ("user__email", "display_name")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "last_activity")

    # ---- Özel alanları renklendir/formatla ---------------------------
    def colored_is_beta(self, obj):
        return self.colored_boolean(obj, "is_beta_user")
    colored_is_beta.short_description = "Beta?"

    def email_notif(self, obj):
        return self.colored_boolean(obj, "email_notifications")
    email_notif.short_description = "Email"

    def push_notif(self, obj):
        return self.colored_boolean(obj, "push_notifications")
    push_notif.short_description = "Push"

    def user_link(self, obj):
        return self.admin_link(obj, "user", obj.user.email)
    user_link.short_description = "Kullanıcı"

    def formatted_last_activity(self, obj):
        if obj.last_activity:
            diff = timezone.now() - obj.last_activity
            color = "green" if diff.total_seconds() < 900 else "orange"
            return format_html('<span style="color:{};">{:%Y-%m-%d %H:%M}</span>', color, obj.last_activity)
        return "-"
    formatted_last_activity.short_description = "Son Aktivite"


# ---------------------------------------------------------------------
# 2) UserPreferences
# ---------------------------------------------------------------------


@admin.register(UserPreferences)
class UserPreferencesAdmin(
    ExportableModelAdmin,
    OptimizedQuerysetMixin,
    LinkMixin,
    JSONFieldMixin,
):
    list_display = (
        "user_link",
        "theme",
        "font_size",
        "show_typing_indicator",
        "sound_enabled",
        "compact_mode",
    )
    list_filter = ("theme", "compact_mode", "show_typing_indicator", "sound_enabled")
    search_fields = ("user__email",)
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "dashboard_widgets_pretty")

    def user_link(self, obj):
        return self.admin_link(obj, "user", obj.user.email)
    user_link.short_description = "Kullanıcı"

    def dashboard_widgets_pretty(self, obj):
        return self.formatted_json(obj, "dashboard_widgets")
    dashboard_widgets_pretty.short_description = "Widget'lar"


# ---------------------------------------------------------------------
# 3) UserSession
# ---------------------------------------------------------------------


@admin.register(UserSession)
class UserSessionAdmin(
    ExportableModelAdmin,
    BulkActionModelAdmin,
    OptimizedQuerysetMixin,
    ColoredBooleanMixin,
    TimestampMixin,
    LinkMixin,
):
    list_display = (
        "user_link",
        "session_short",
        "ip_address",
        "is_active_colored",
        "formatted_last_activity",
        "expires_at",
        "location",
    )
    list_filter = ("is_active", "expires_at")
    search_fields = ("user__email", "session_key", "ip_address", "location")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "device_info_pretty")

    # ---- Display helpers --------------------------------------------
    def session_short(self, obj):
        return f"{obj.session_key[:8]}…"
    session_short.short_description = "Oturum"

    def is_active_colored(self, obj):
        return self.colored_boolean(obj, "is_active")
    is_active_colored.short_description = "Aktif?"

    def formatted_last_activity(self, obj):
        return self.formatted_updated_at(obj)
    formatted_last_activity.short_description = "Son Aktivite"

    def device_info_pretty(self, obj):
        return self.formatted_json(obj, "device_info")
    device_info_pretty.short_description = "Cihaz"

    # ---- Toplu aksiyonlar -------------------------------------------
    def terminate_sessions(self, request, queryset):
        count = queryset.update(is_active=False, expires_at=timezone.now())
        self.message_user(request, f"{count} oturum sonlandırıldı.", messages.WARNING)
    terminate_sessions.short_description = "Seçilen oturumları sonlandır"

    actions = ExportableModelAdmin.actions + ["terminate_sessions"]


# ---------------------------------------------------------------------
# 4) UserActivity
# ---------------------------------------------------------------------


@admin.register(UserActivity)
class UserActivityAdmin(
    ExportableModelAdmin,      # BaseModelAdmin’i zaten içerir
    OptimizedQuerysetMixin,
    TimestampMixin,
    LinkMixin,
    JSONFieldMixin,
):
    list_display = (
        "user_link",
        "activity_type",
        "short_description",
        "ip_address",
        "formatted_created_at",
    )
    list_filter = ("activity_type", "created_at")
    search_fields = ("user__email", "description", "ip_address")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "metadata_pretty")

    def user_link(self, obj):
        return self.admin_link(obj, "user", obj.user.email)
    user_link.short_description = "Kullanıcı"

    def short_description(self, obj):
        return (obj.description or "")[:80] + ("…" if obj.description and len(obj.description) > 80 else "")
    short_description.short_description = "Açıklama"

    def metadata_pretty(self, obj):
        return self.formatted_json(obj, "metadata")
    metadata_pretty.short_description = "Ek Bilgi"


# ---------------------------------------------------------------------
# 5) UserApiKey
# ---------------------------------------------------------------------


@admin.register(UserApiKey)
class UserApiKeyAdmin(
    ExportableModelAdmin,
    BulkActionModelAdmin,
    OptimizedQuerysetMixin,
    ColoredBooleanMixin,
    TimestampMixin,
    LinkMixin,
):
    list_display = (
        "user_link",
        "name",
        "masked_key",
        "is_active_colored",
        "rate_limit",
        "usage_count",
        "formatted_last_used",
        "expires_at",
    )
    list_filter = ("is_active", "expires_at")
    search_fields = ("user__email", "name", "key")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "usage_count", "last_used")

    # ---- Maskeleme & renkli alanlar ---------------------------------
    def masked_key(self, obj):
        if self._request.user.is_superuser:
            return obj.key
        return f"{obj.key[:6]}…{obj.key[-4:]}"
    masked_key.short_description = "API Anahtarı"

    def is_active_colored(self, obj):
        return self.colored_boolean(obj, "is_active")
    is_active_colored.short_description = "Aktif?"

    def formatted_last_used(self, obj):
        if obj.last_used:
            return format_html('<span title="{:%Y-%m-%d %H:%M:%S}">{}</span>', obj.last_used, obj.last_used.date())
        return "-"
    formatted_last_used.short_description = "Son Kullanım"

    # ---- Özel aksiyon: anahtar yenile --------------------------------
    @admin_action_required_permission("sapbot_api.change_userapikey")
    def regenerate_keys(self, request, queryset):
        regenerated = 0
        for api_key in queryset:
            api_key.generate_key()
            api_key.save(update_fields=["key", "updated_at"])
            regenerated += 1
        self.message_user(request, f"{regenerated} API anahtarı yeniden oluşturuldu.")
    regenerate_keys.short_description = "Seçilen anahtarları yeniden oluştur"

    actions = ExportableModelAdmin.actions + ["regenerate_keys"]

    # request nesnesini maskeleme için sakla
    def get_queryset(self, request):
        self._request = request
        return super().get_queryset(request)

