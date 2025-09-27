# backend/openorderdocsum/admin.py
from django.contrib import admin
from .models.openorderdeail import OpenOrderDetail
from .models.docsum import DocumentSummary

class OpenOrderDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OpenOrderDetail._meta.fields if field.name != "id"]
    search_fields = ['belge_no', 'musteri_ad', 'satici']
    list_filter = ['satis_tipi', 'belge_tarih', 'belge_durum']
    date_hierarchy = 'belge_tarih'



class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ['belge_no', 'musteri_ad', 'satici', 'belge_tarih', 'teslim_tarih', 'belge_onay', 'belge_durum', 'sevk_adres', 'musteri_kod', 'satis_tipi', 'net_tutar_ypb', 'acik_net_tutar_ypb', 'acik_net_tutar_spb', 'girsberger_net_tutar_ypb', 'mamul_net_tutar_ypb', 'ticari_net_tutar_ypb', 'nakliye_net_tutar_ypb', 'montaj_net_tutar_ypb', 'belge_iskonto_oran_display']
    search_fields = ['belge_no', 'musteri_ad']
    list_filter = ['satis_tipi', 'belge_tarih', 'belge_durum']
    date_hierarchy = 'belge_tarih'

    def belge_iskonto_oran_display(self, obj):
        return f"{obj.belge_iskonto_oran:.2f}%"
    belge_iskonto_oran_display.short_description = "Belge İskonto Oranı"  # Sütun başlığını ayarlar


admin.site.register(OpenOrderDetail, OpenOrderDetailAdmin)
admin.site.register(DocumentSummary, DocumentSummaryAdmin)

