# backend/tunainssupplierpayment/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models.closinginvoice import ClosingInvoice
from .models.models import SupplierPayment

class ClosingInvoiceResource(resources.ModelResource):
    class Meta:
        model = ClosingInvoice

@admin.register(ClosingInvoice)
class ClosingInvoiceAdmin(ImportExportModelAdmin):
    resource_class = ClosingInvoiceResource
    list_display = ('cari_kod', 'cari_ad', 'current_balance', 'monthly_balances', 'odemekosulu', 'iban' , 'created_at', 'updated_at')
    search_fields = ('cari_kod', 'cari_ad',)
    list_filter = ('cari_kod', 'cari_ad',)
    readonly_fields = ('monthly_balances',)

class SupplierPaymentResource(resources.ModelResource):
    class Meta:
        model = SupplierPayment

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(ImportExportModelAdmin):
    resource_class = SupplierPaymentResource
    list_display = ('cari_kod', 'cari_ad', 'belge_tarih', 'belge_no', 'iban', 'odemekosulu', 'borc', 'alacak', 'created_at', 'updated_at')
    search_fields = ('cari_kod', 'cari_ad',)
    list_filter = ('belge_tarih', 'belge_tarih',)

   


