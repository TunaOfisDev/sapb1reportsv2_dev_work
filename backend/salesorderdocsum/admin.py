# backend/salesorderdocsum/admin.py
from django.contrib import admin
from .models.salesorderdetail import SalesOrderDetail
from .models.docsum import DocumentSummary

class SalesOrderDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SalesOrderDetail._meta.fields if field.name != "id"]
    search_fields = ['belge_no', 'musteri_ad', 'satici']
    list_filter = ['satis_tipi', 'belge_tarih', 'belge_durum']
    date_hierarchy = 'belge_tarih'



class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ['belge_no', 'musteri_ad', 'satici', 'belge_tarih', 'teslim_tarih', 'belge_onay', 'belge_durum', 
                    'belge_aciklamasi','sevk_adres', 'musteri_kod', 'satis_tipi', 'net_tutar_ypb', 'net_tutar_spb', 'acik_net_tutar_ypb', 
                    'acik_net_tutar_spb', 'belge_iskonto_oran_display']
    search_fields = ['belge_no', 'musteri_ad']
    list_filter = ['satis_tipi', 'belge_tarih', 'belge_durum']
    date_hierarchy = 'belge_tarih'

    def belge_iskonto_oran_display(self, obj):
        return f"{obj.belge_iskonto_oran:.2f}%"
    belge_iskonto_oran_display.short_description = "Belge İskonto Oranı"  # Sütun başlığını ayarlar


admin.site.register(SalesOrderDetail, SalesOrderDetailAdmin)
admin.site.register(DocumentSummary, DocumentSummaryAdmin)

