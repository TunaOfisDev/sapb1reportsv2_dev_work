# backend/logocustomercollection/admin.py

from django.contrib import admin
from .models.models import LogoCustomerCollectionTransaction
from .models.closinginvoice import LogoCustomerCollectionAgingSummary


@admin.register(LogoCustomerCollectionTransaction)
class LogoCustomerCollectionTransactionAdmin(admin.ModelAdmin):
    list_display = ("cari_kod", "cari_ad", "ay", "yil", "borc", "alacak")
    list_filter = ("yil", "ay")
    search_fields = ("cari_kod", "cari_ad")
    ordering = ("-yil", "-ay")
    readonly_fields = ("cari_kod", "ay", "yil")  # optional: güvenli olması için


@admin.register(LogoCustomerCollectionAgingSummary)
class LogoCustomerCollectionAgingSummaryAdmin(admin.ModelAdmin):
    list_display = ("cari_kod", "cari_ad", "guncel_bakiye", "get_aylik_kalan_borc", "created_at", "updated_at" )
    search_fields = ("cari_kod", "cari_ad")
    ordering = ("cari_kod",)
    readonly_fields = ("created_at", "updated_at", "aylik_kalan_borc")

    def get_aylik_kalan_borc(self, obj):
        return obj.sorted_aylik_kalan_borc
    get_aylik_kalan_borc.short_description = "Aylık Kalan Borç"

