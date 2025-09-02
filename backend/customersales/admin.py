# backend/customersales/admin.py

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# DÜZELTME: Artık var olmayan 'CustomerSalesReportPreset' import'u kaldırıldı.
from .models import CustomerSalesRawData

# 'CustomerSalesReportPreset' ile ilgili Resource sınıfı kaldırıldı.

class CustomerSalesRawDataResource(resources.ModelResource):
    """
    CustomerSalesRawData modeli için içeri/dışarı aktarma kurallarını tanımlar.
    """
    class Meta:
        model = CustomerSalesRawData
        fields = [field.name for field in model._meta.fields if field.name != "id"]
        # 'id' alanı genellikle otomatik arttığı için import sırasında sorun çıkarabilir.
        # Bu nedenle dışarı aktarma alanlarından çıkarılabilir.
        import_id_fields = ('musteri_kodu',) # Benzersiz bir alana göre import yapalım

# 'CustomerSalesReportPreset' ile ilgili Admin sınıfı kaldırıldı.

@admin.register(CustomerSalesRawData)
class CustomerSalesRawDataAdmin(ImportExportModelAdmin):
    """
    HANA'dan çekilen Ham Satış Verileri için admin arayüzü.
    """
    resource_class = CustomerSalesRawDataResource
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    list_display = (
        'musteri_adi',
        'satici',
        'satis_tipi',
        'toplam_net_spb_eur',
        'created_at', # BaseModel'dan gelen alanı gösterelim
        'updated_at', # BaseModel'dan gelen alanı gösterelim
    )
    list_filter = ('satici', 'satis_tipi', 'cari_grup')
    search_fields = ('musteri_adi', 'musteri_kodu', 'satici')
    list_per_page = 50
    date_hierarchy = 'created_at' # BaseModel'dan gelen alanı kullanalım