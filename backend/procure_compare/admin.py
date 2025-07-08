# File: backend/procure_compare/admin.py

from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources
from django.utils.html import format_html
from procure_compare.models import (
    PurchaseOrder,
    PurchaseQuote,
    PurchaseComparison,
    PurchaseApproval
)

# Export için resource tanımı
class PurchaseApprovalResource(resources.ModelResource):
    class Meta:
        model = PurchaseApproval
        fields = (
            'id',
            'belge_no',
            'uniq_detail_no',
            'action',
            'aciklama',
            'kullanici__email',
            'created_at'
        )
        export_order = fields


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("doc_num", "card_name", "doc_date", "doc_status")
    search_fields = ("doc_num", "card_code", "card_name")
    list_filter = ("doc_status", "doc_date")


@admin.register(PurchaseQuote)
class PurchaseQuoteAdmin(admin.ModelAdmin):
    list_display = ("doc_num", "card_name", "item_code", "price", "currency")
    search_fields = ("doc_num", "card_name", "item_code")
    list_filter = ("currency",)


@admin.register(PurchaseComparison)
class PurchaseComparisonAdmin(admin.ModelAdmin):
    list_display = (
        "belge_no", "uniq_detail_no", "kalem_kod", "tedarikci_ad", 
        "net_fiyat_dpb", "satir_status", "has_teklif_uyari"
    )
    search_fields = ("belge_no", "kalem_kod", "tedarikci_ad")
    list_filter = ("belge_status", "satir_status", "belge_tarih")

    @admin.display(boolean=True, description="Uyarı Var mı?")
    def has_teklif_uyari(self, obj):
        import json

        try:
            referanslar = json.loads(obj.referans_teklifler or '[]')
            referans_bos = not isinstance(referanslar, list) or len(referanslar) == 0
        except Exception:
            referans_bos = True

        teklif_json_bos = not obj.teklif_fiyatlari_json

        try:
            parsed = json.loads(obj.teklif_fiyatlari_json or '{}')
            teklif_list_bos = not isinstance(parsed, dict) or len(parsed) == 0
        except Exception:
            teklif_list_bos = True

        return referans_bos or teklif_json_bos or teklif_list_bos




@admin.register(PurchaseApproval)
class PurchaseApprovalAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = PurchaseApprovalResource
    list_display = ("belge_no", "uniq_detail_no", "action", "kullanici", "created_at")
    search_fields = ("belge_no", "uniq_detail_no", "kullanici__email", "aciklama")
    list_filter = ("action", "created_at")
    ordering = ("-created_at",)
