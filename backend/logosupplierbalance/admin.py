# backend/logosupplierbalance/admin.py
from django.contrib import admin
from .models.models import SupplierBalance

class SupplierBalanceAdmin(admin.ModelAdmin):
    list_display = ('cari_kodu', 'cari_aciklamasi', 'bakiye_borc','bakiye_alacak', 'created_at', 'updated_at')
    search_fields = ('cari_kodu', 'cari_aciklamasi')
    list_filter = ('cari_kodu', 'cari_aciklamasi')
    ordering = ('cari_kodu',)

admin.site.register(SupplierBalance, SupplierBalanceAdmin)

