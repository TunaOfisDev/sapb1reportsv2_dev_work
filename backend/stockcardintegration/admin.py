# path: backend/stockcardintegration/admin.py

from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models.models import StockCard
from .models.helptext import FieldHelpText
from .models.productpricelist_models import ProductPriceList  # ✅ EKLENDİ

@admin.register(StockCard)
class StockCardAdmin(admin.ModelAdmin):
    """
    Stok Kartı Entegrasyonu için kurumsal yönetim paneli.
    - Oluşturan ve güncelleyen kullanıcı bilgisi görüntülenir.
    - SAP HANA durumu renklendirilerek öne çıkarılır.
    - Kritik alanlar salt okunur yapılmıştır.
    - Silme işlemi yalnızca sistem yöneticilerine (superuser) açıktır.
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

    # Yalnızca superuser'a görünmesi için özel aksiyon
    actions = ["delete_all_stock_cards"]

    # ─────────────  Yardımcı Gösterim Fonksiyonları  ─────────────
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

    # ─────────────  Yetki ve Aksiyon Kontrolleri  ─────────────
    def has_delete_permission(self, request, obj=None):
        """Silme yetkisi sadece superuser'a verilir."""
        return request.user.is_superuser

    def get_actions(self, request):
        """Normal kullanıcılar için tüm silme aksiyonlarını gizle."""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop("delete_selected", None)
            actions.pop("delete_all_stock_cards", None)
        return actions

    @admin.action(description="Tüm Stok Kartlarını Sil")
    def delete_all_stock_cards(self, request, queryset):
        """Tüm StockCard kayıtlarını topluca sil (yalnızca superuser)."""
        if not request.user.is_superuser:
            self.message_user(request, "Bu aksiyona izniniz yok.", level=messages.ERROR)
            return
        StockCard.objects.all().delete()
        self.message_user(request, "Tüm stok kartları silindi.", level=messages.SUCCESS)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("created_by", "updated_by")


# ────────────────────────────────────────────────────────────────
# FieldHelpText yapılandırması
# ────────────────────────────────────────────────────────────────

class FieldHelpTextResource(resources.ModelResource):
    class Meta:
        model = FieldHelpText
        fields = ("id", "field_name", "label", "description", "created_at", "updated_at")
        export_order = fields
        import_id_fields = ("field_name",)


@admin.register(FieldHelpText)
class FieldHelpTextAdmin(ImportExportModelAdmin):
    """
    Alan yardım metinlerini içe/dışa aktarmak için yönetim paneli.
    """
    list_display = ("id", "field_name", "label", "short_description", "created_at", "updated_at")
    search_fields = ("field_name", "label", "description")
    ordering = ("id",)
    resource_class = FieldHelpTextResource
    exclude = ("created_by", "updated_by")

    def short_description(self, obj):
        return (obj.description[:75] + "...") if len(obj.description) > 75 else obj.description
    short_description.short_description = "Açıklama (kısa)"


# ────────────────────────────────────────────────────────────────
# ProductPriceList admin görünümü
# ────────────────────────────────────────────────────────────────
@admin.register(ProductPriceList)
class ProductPriceListAdmin(admin.ModelAdmin):
    """
    SAP HANA'dan gelen ürün fiyat listesini sade şekilde gösterir.
    - Değişiklik izni açık, silme kapalı (isteğe bağlı güncellenebilir)
    - Arama ve filtre destekli
    - Eski bileşen kodu varsa listede öne çıkarılır
    """
    list_display = (
        "item_code",
        "item_name",
        "price_list_name",
        "price",
        "currency",
        "old_component_code",
        "updated_at",
    )
    search_fields = ("item_code", "item_name", "old_component_code")
    list_filter = ("price_list_name", "currency")
    ordering = ("item_code",)
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False  # İstersen True yapabilirsin

# ────────────────────────────────────────────────────────────────
# FieldHelpText admin (aynı şekilde bırakıldı)
# ────────────────────────────────────────────────────────────────
class FieldHelpTextResource(resources.ModelResource):
    class Meta:
        model = FieldHelpText
        fields = ("id", "field_name", "label", "description", "created_at", "updated_at")
        export_order = fields
        import_id_fields = ("field_name",)


