# path: backend/stockcardintegration/admin.py

from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models.models import StockCard
from .models.helptext import FieldHelpText


@admin.register(StockCard)
class StockCardAdmin(admin.ModelAdmin):
    """
    Stok Kartı Entegrasyonu için kurumsal yönetim paneli.
    - Oluşturan ve güncelleyen kullanıcı bilgisi görüntülenir.
    - SAP HANA durumu renklendirilerek öne çıkarılır.
    - Kritik alanlar salt okunur yapılmıştır.
    - Silme işlemi yasaktır.
    """

    list_display = (
        "id",
        "item_code",
        "item_name",
        "items_group_code",
        "price",
        "currency",
        "hana_status_colored",
        "created_by_email",
        "updated_by_email",
        "last_synced_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("item_code", "item_name", "hana_status", "created_by__email")
    list_filter = ("hana_status", "items_group_code", "created_at", "created_by")
    ordering = ("-updated_at",)
    readonly_fields = (
        "hana_status",
        "last_synced_at",
        "created_at",
        "updated_at",
        "extra_data",
        "created_by",
        "updated_by",
    )

    def created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else "-"
    created_by_email.short_description = "Oluşturan Kullanıcı"

    def updated_by_email(self, obj):
        return obj.updated_by.email if obj.updated_by else "-"
    updated_by_email.short_description = "Güncelleyen Kullanıcı"

    def hana_status_colored(self, obj):
        status_colors = {
            "pending": "orange",
            "processing": "blue",
            "completed": "green",
            "failed": "red",
        }
        color = status_colors.get(obj.hana_status, "black")
        return mark_safe(f'<b style="color:{color}">{obj.hana_status.upper()}</b>')
    hana_status_colored.short_description = "SAP Durumu"

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("created_by", "updated_by")


class FieldHelpTextResource(resources.ModelResource):
    class Meta:
        model = FieldHelpText
        fields = ("id", "field_name", "label", "description", "created_at", "updated_at")
        export_order = fields
        import_id_fields = ("field_name",)


@admin.register(FieldHelpText)
class FieldHelpTextAdmin(ImportExportModelAdmin):
    list_display = ("id", "field_name", "label", "short_description", "created_at", "updated_at")
    search_fields = ("field_name", "label", "description")
    ordering = ("id",)  # 🔧 Burada sıralama artık id’ye göre
    resource_class = FieldHelpTextResource
    exclude = ("created_by", "updated_by")

    def short_description(self, obj):
        return (obj.description[:75] + "...") if len(obj.description) > 75 else obj.description
    short_description.short_description = "Açıklama (kısa)"
