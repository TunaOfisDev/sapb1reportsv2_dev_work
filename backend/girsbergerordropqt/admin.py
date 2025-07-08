# backend/girsbergerordropqt/admin.py
from django.contrib import admin
from .models.models import OrdrDetailOpqt

class OrdrDetailOpqtAdmin(admin.ModelAdmin):
    list_display = [
        'uniq_detail_no', 'belge_no', 'satici', 'belge_tarih', 'teslim_tarih', 'musteri_kod', 
        'musteri_ad', 'satis_tipi', 'satir_status', 'kalem_kod', 'kalem_tanimi', 'sip_miktar', 
        'salma_teklif_tedarikci_kod', 'salma_teklif_tedarikci_ad', 'salma_teklif_no', 
        'salma_teklif_kaynak_detay_no', 'salma_teklif_kalem_no', 'salma_teklif_miktar', 
        'created_at', 'updated_at'
    ]
    search_fields = ['uniq_detail_no', 'belge_no', 'satici', 'musteri_kod',]
    list_filter = ['satir_status', 'satis_tipi',]

admin.site.register(OrdrDetailOpqt, OrdrDetailOpqtAdmin)
