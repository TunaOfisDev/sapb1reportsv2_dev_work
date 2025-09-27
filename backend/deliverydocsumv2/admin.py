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
            'bugun', 'bugun_minus_1', 'bugun_minus_2', 'bugun_minus_3', 'bugun_minus_4',
            'bu_ay_toplam', 'bu_ay_minus_1_toplam', 'yillik_toplam', 'acik_irsaliye_belge_no_tarih_tutar',
            'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi', 'bugun_ilgili_siparis_numaralari',
            'bugun_minus_1_ilgili_siparis_numaralari', 'bugun_minus_2_ilgili_siparis_numaralari', 
            'bugun_minus_3_ilgili_siparis_numaralari', 'bugun_minus_4_ilgili_siparis_numaralari', 
            'bu_ay_ilgili_siparis_numaralari', 'bu_ay_minus_1_ilgili_siparis_numaralari',
            'created_at', 'updated_at'
        )
        export_order = fields

class DeliveryDocSummaryAdmin(ImportExportModelAdmin):
    resource_class = DeliveryDocSummaryResource
    list_display = (
        'cari_kod', 'cari_adi', 'temsilci', 'cari_grup',
        'bugun', 'bugun_minus_1', 'bugun_minus_2', 'bugun_minus_3', 'bugun_minus_4',
        'bu_ay_toplam', 'bu_ay_minus_1_toplam', 'yillik_toplam', 'acik_irsaliye_belge_no_tarih_tutar',
        'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi', 'bugun_ilgili_siparis_numaralari',
        'bugun_minus_1_ilgili_siparis_numaralari', 'bugun_minus_2_ilgili_siparis_numaralari', 
        'bugun_minus_3_ilgili_siparis_numaralari', 'bugun_minus_4_ilgili_siparis_numaralari', 
        'bu_ay_ilgili_siparis_numaralari', 'bu_ay_minus_1_ilgili_siparis_numaralari',
        'created_at', 'updated_at'
    )
    search_fields = ('cari_kod', 'cari_adi',)
    list_filter = ('temsilci', 'cari_grup', 'created_at', 'updated_at',)
    ordering = ('-created_at',)

admin.site.register(DeliveryDocSummary, DeliveryDocSummaryAdmin)
