# backend/customercollection/admin.py
from django.contrib import admin
from .models.models import CustomerCollection
from .models.closinginvoice import ClosingInvoice

@admin.register(CustomerCollection)
class CustomerCollectionAdmin(admin.ModelAdmin):
    list_display = ['cari_kod', 'cari_ad', 'satici', 'grup', 'belge_tarih', 'vade_tarih', 'belge_no', 'odemekod', 'odemekosulu', 'borc', 'alacak']
    list_filter = ['cari_kod', 'grup', 'belge_tarih', 'vade_tarih']
    search_fields = ['cari_kod', 'cari_ad', 'belge_no']
    ordering = ['belge_tarih', 'cari_kod']



@admin.register(ClosingInvoice)
class ClosingInvoiceAdmin(admin.ModelAdmin):
    list_display = ['cari_kod', 'cari_ad', 'satici', 'grup', 'odemekosulu', 'current_balance', 'monthly_balances']
    list_filter = ['cari_kod', 'grup']
    search_fields = ['cari_kod', 'cari_ad']
    ordering = ['cari_kod']
