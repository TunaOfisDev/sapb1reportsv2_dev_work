# backend/salesorderdetail/admin.py
from django.contrib import admin
from .models.models import SalesOrderMaster, SalesOrderDetail

class SalesOrderDetailInline(admin.TabularInline):
    model = SalesOrderDetail
    extra = 0  # Ekstra boş satır sayısı
    fields = [
        'kalem_grup', 'satir_status', 'satir_no', 'depo_kod', 'kalem_kod',
        'kalem_tanimi', 'birim', 'sip_miktar', 'sevk_miktar', 'kalan_miktar',
        'liste_fiyat_dpb', 'detay_kur', 'detay_doviz', 'iskonto_oran',
        'net_fiyat_dpb', 'brut_tutar_dpb', 'net_tutar_dpb', 'isk_tutar_dpb',
        'kdv_tutar_dpb', 'kdvli_net_tutar_dpb', 'liste_fiyat_ypb',
        'brut_tutar_ypb', 'isk_tutar_ypb', 'net_tutar_ypb', 'kdv_oran',
        'kdv_tutar_ypb', 'kdvli_net_tutar_ypb'
    ]
    readonly_fields = ['satir_no']

class SalesOrderMasterAdmin(admin.ModelAdmin):
    list_display = [
        'master_unique_id','sip_no', 'musteri_kod', 'musteri_ad', 'satici', 'belge_tur',
        'belge_tarihi', 'belge_status', 'belge_kur', 'belge_doviz'
    ]
    search_fields = ['musteri_kod', 'musteri_ad', 'satici', 'unique_id','sip_no']
    list_filter = ['belge_tur', 'belge_status', 'satici', 'belge_doviz', 'sip_no']
    inlines = [SalesOrderDetailInline]

admin.site.register(SalesOrderMaster, SalesOrderMasterAdmin)

class SalesOrderDetailAdmin(admin.ModelAdmin):
    list_display = [
        'detay_unique_id',
        'kalem_grup', 'satir_no', 'kalem_kod', 'kalem_tanimi',
        'sip_miktar', 'net_fiyat_dpb', 'brut_tutar_dpb', 'net_tutar_dpb',
        'kdv_tutar_dpb', 'liste_fiyat_ypb', 'net_tutar_ypb', 'kdv_tutar_ypb'
    ]
    search_fields = ['kalem_kod', 'kalem_tanimi', 'master__musteri_ad']
    list_filter = ['kalem_grup', 'satir_status', 'depo_kod', 'detay_doviz']

admin.site.register(SalesOrderDetail, SalesOrderDetailAdmin)

