# backend/deliverydocsum/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models.models import DeliveryDocSummary

class DeliveryDocSummaryResource(resources.ModelResource):
    class Meta:
        model = DeliveryDocSummary
        fields = (
            'id', 'cari_kod', 'cari_adi', 'temsilci', 'cari_grup',
            'gunluk_toplam', 'dun_toplam', 'onceki_gun_toplam', 'aylik_toplam', 'yillik_toplam',
            'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi',
            'gunluk_ilgili_siparis_numaralari', 'dun_ilgili_siparis_numaralari', 'onceki_gun_ilgili_siparis_numaralari',
            'created_at', 'updated_at'
        )

class DeliveryDocSummaryAdmin(ImportExportModelAdmin):
    resource_class = DeliveryDocSummaryResource
    list_display = (
        'cari_kod', 'cari_adi', 'temsilci', 'cari_grup',
        'gunluk_toplam', 'dun_toplam', 'onceki_gun_toplam', 'aylik_toplam', 'yillik_toplam',
        'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi',
        'gunluk_ilgili_siparis_numaralari', 'dun_ilgili_siparis_numaralari', 'onceki_gun_ilgili_siparis_numaralari',
        'created_at', 'updated_at'
    )
    search_fields = ('cari_kod', 'cari_adi',)
    list_filter = ('temsilci', 'cari_grup', 'created_at', 'updated_at',)

admin.site.register(DeliveryDocSummary, DeliveryDocSummaryAdmin)
