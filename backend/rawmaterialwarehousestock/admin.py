# backend/rawmaterialwarehousestock/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models.models import RawMaterialWarehouseStock

class RawMaterialWarehouseStockResource(resources.ModelResource):
    """
    Hammadde Depo Stok modeline ait kaynak sınıfı, 
    içe ve dışa aktarma işlemlerini yönetir.
    """
    class Meta:
        model = RawMaterialWarehouseStock
        fields = (
            'depo_kodu', 'kalem_grup_ad', 'stok_kalem', 'satis_kalem', 'satinalma_kalem',
            'yapay_kalem', 'kalem_kod', 'kalem_tanim', 'stok_olcu_birim', 'depo_stok',
            'siparis_edilen_miktar', 'son_satinalma_fiyat', 'son_satinalma_fatura_tarih',
            'verilen_siparisler','secili', 'created', 'modified'
        )

class RawMaterialWarehouseStockAdmin(ImportExportModelAdmin):
    """
    Hammadde Depo Stok modelini yönetmek için gelişmiş admin sınıfı.
    """
    resource_class = RawMaterialWarehouseStockResource
    list_display = (
        'depo_kodu', 'kalem_grup_ad', 'stok_kalem', 'satis_kalem', 'satinalma_kalem',
        'yapay_kalem', 'kalem_kod', 'kalem_tanim', 'stok_olcu_birim', 'depo_stok',
        'siparis_edilen_miktar', 'son_satinalma_fiyat', 'son_satinalma_fatura_tarih',
        'verilen_siparisler', 'created', 'modified'
    )
    search_fields = ['kalem_kod', 'kalem_tanim']
    list_filter = ['depo_kodu', 'kalem_grup_ad', 'created', 'modified']
    ordering = ['kalem_kod']
    list_per_page = 500  # Sayfa başına 500 satır göster

admin.site.register(RawMaterialWarehouseStock, RawMaterialWarehouseStockAdmin)