# backend/logocustomerbalance/admin.py
from django.contrib import admin
from .models.models import CustomerBalance

class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ('cari_kodu', 'cari_aciklamasi', 'bakiye_borc','bakiye_alacak', 'created_at', 'updated_at')
    search_fields = ('cari_kodu', 'cari_aciklamasi')
    list_filter = ('cari_kodu', 'cari_aciklamasi')
    ordering = ('cari_kodu',)

admin.site.register(CustomerBalance, CustomerBalanceAdmin)

