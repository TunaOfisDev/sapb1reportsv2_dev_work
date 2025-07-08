# backend/salesofferdocsum/admin.py
from django.contrib import admin
from .models.salesofferdetail import SalesOfferDetail
from .models.docsum import DocumentSummary

class SalesOfferDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SalesOfferDetail._meta.fields if field.name != "id"]
    search_fields = ['belge_no', 'musteri_ad', 'satici']
    list_filter = ['satis_tipi', 'belge_tarih', 'belge_durum']
    date_hierarchy = 'belge_tarih'



class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ['belge_no', 'musteri_ad', 'satici', 'belge_tarih', 'teslim_tarih', 'belge_onay', 'belge_durum', 'iptal_edilen', 'elle_kapatilan', 'siparise_aktarilan', 
                    'belge_aciklamasi', 'sevk_adres', 'musteri_kod', 'satis_tipi', 'brut_tutar_spb', 'net_tutar_spb', 'net_tutar_ypb', 'belge_iskonto_oran_display', 
                    'created_at', 'updated_at']
    search_fields = ['belge_no', 'musteri_ad']
    list_filter = ['satis_tipi', 'belge_tarih', 'belge_durum']
    date_hierarchy = 'belge_tarih'

    def belge_iskonto_oran_display(self, obj):
        return f"{obj.belge_iskonto_oran:.2f}%"
    belge_iskonto_oran_display.short_description = "Belge İskonto Oranı"  # Sütun başlığını ayarlar


admin.site.register(SalesOfferDetail, SalesOfferDetailAdmin)
admin.site.register(DocumentSummary, DocumentSummaryAdmin)

