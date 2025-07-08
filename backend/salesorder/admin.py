# backend/salesorder/admin.py
from django.contrib import admin
from .models.models import SalesOrder
from .models.customersalesorder import CustomerSalesOrder

class SalesOrderAdmin(admin.ModelAdmin):
    list_display = [
        'satici', 'belge_tur', 'onay1_status', 'onay2_status', 'belge_tarihi', 
        'teslim_tarihi', 'belge_status', 'musteri_kod', 'musteri_ad', 'belge_giris_no', 
        'sip_no', 'satis_tipi', 'belge_aciklamasi', 'sevk_adresi', 'unique_master_no', 
        'kalem_grup_kod', 'kalem_grup', 'eski_bilesen_kod', 'musteri_sip_no', 
        'musteri_sip_tarih', 'assmann_comm_no', 'assmann_pos_no', 'assmann_item_no', 
        'renk_kod', 'uretim_aciklamasi', 'satir_status', 'satir_no', 'depo_kod', 
        'kalem_kod', 'kalem_tanimi', 'birim', 'sip_miktar', 'sevk_miktar', 'kalan_miktar', 
        'liste_fiyat_dpb', 'iskonto_oran', 'net_fiyat_dpb', 'brut_tutar_dpb', 
        'net_tutar_dpb', 'isk_tutar_dpb', 'kdv_tutar_dpb', 'kdvli_net_tutar_dpb', 
        'kur', 'doviz', 'liste_fiyat_ypb', 'brut_tutar_ypb', 'isk_tutar_ypb', 
        'net_tutar_ypb', 'kdv_oran', 'kdv_tutar_ypb', 'kdvli_net_tutar_ypb',
    ]
    search_fields = ['musteri_ad', 'musteri_kod', 'sip_no']  # Örnek olarak bazı arama alanları ekledim
    list_filter = ['satici', 'belge_tur', 'belge_status', 'doviz']  # Örnek olarak bazı filtreleme alanları ekledim
    date_hierarchy = 'belge_tarihi'  # Belge tarihi üzerinden hiyerarşik tarih araması

    # Model formunda bazı alanların düzenlenebilir olmasını sağlamak için
    # Bu kısım opsiyonel ve projenizin ihtiyaçlarına göre düzenlenebilir
    readonly_fields = ['unique_master_no']  # Örnek olarak unique_master_no alanını salt okunur yaptım

admin.site.register(SalesOrder, SalesOrderAdmin)

@admin.action(description='Seçili kayıtları yayından kaldır')
def make_unpublished(modeladmin, request, queryset):
    queryset.update(yayinda_mi=False)

class CustomerSalesOrderAdmin(admin.ModelAdmin):
    list_display = ['grup','musteri_kod', 'musteri_ad',  'yillik_toplam', 'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik']
    list_display_links = ['musteri_kod', 'musteri_ad']  # Detay sayfasına yönlendirecek alanlar
    search_fields = ['musteri_kod', 'musteri_ad']
    list_filter = ['yil', 'musteri_kod']  # Filtreleme için ek alanlar
    list_per_page = 25  # Sayfa başına düşen kayıt sayısı
    ordering = ['-yil', 'musteri_kod']  # Varsayılan sıralama düzeni
    actions = [make_unpublished]  # Toplu işlem fonksiyonu

# Admin paneline modeli kaydetmek
admin.site.register(CustomerSalesOrder, CustomerSalesOrderAdmin)

