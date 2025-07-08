# backend/logo_supplier_receivables_aging/admin.py

from django.contrib import admin
from .models.models import SupplierRawTransaction
from .models.closinginvoice import SupplierAgingSummary


@admin.register(SupplierRawTransaction)
class SupplierRawTransactionAdmin(admin.ModelAdmin):
    list_display = ("cari_kod", "cari_ad", "ay", "yil", "borc", "alacak", "created_at")
    list_filter = ("yil", "ay", "cari_kod")
    search_fields = ("cari_kod", "cari_ad")
    ordering = ("-yil", "-ay")


@admin.register(SupplierAgingSummary)
class SupplierAgingSummaryAdmin(admin.ModelAdmin):
    list_display = ("cari_kod", "cari_ad", "guncel_bakiye", "created_at")
    search_fields = ("cari_kod", "cari_ad")
    ordering = ("cari_kod",)
