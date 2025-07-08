# backend/hanadbintegration/admin.py

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models.models import HANADBIntegration


@admin.register(HANADBIntegration)
class HANADBIntegrationAdmin(admin.ModelAdmin):
    """
    HANA DB Entegrasyonları için gelişmiş yönetim paneli.
    - `list_display` ile özet bilgiler.
    - `search_fields` ile hızlı arama.
    - `list_filter` ile filtreleme.
    - `readonly_fields` ile koruma.
    - Renklendirilmiş durum göstergesi.
    """

    list_display = (
        "id",
        "integration_name",
        "integration_type",
        "hana_status_colored",
        "last_synced_at",
        "created_at",
        "updated_at"
    )
    search_fields = ("integration_name", "integration_type", "hana_status")
    list_filter = ("hana_status", "integration_type", "created_at")
    ordering = ("-updated_at",)
    readonly_fields = ("hana_status", "last_synced_at", "created_at", "updated_at")

    def hana_status_colored(self, obj):
        """
        HANA DB Entegrasyon Durumunu renklendirerek gösterir.
        """
        status_colors = {
            "pending": "orange",
            "processing": "blue",
            "completed": "green",
            "failed": "red",
        }
        color = status_colors.get(obj.hana_status, "black")
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{obj.hana_status.upper()}</span>')

    hana_status_colored.short_description = "HANA Durumu"
