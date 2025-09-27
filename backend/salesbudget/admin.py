# backend/salesbudget/admin.py
from django.contrib import admin
from .models.models import SalesBudget

class SalesBudgetAdmin(admin.ModelAdmin):
    list_display = (
        'satici', 'toplam_gercek', 'toplam_hedef', 'yuzde_oran_display',
        'oca_gercek', 'oca_hedef', 'sub_gercek', 'sub_hedef', 
        'mar_gercek', 'mar_hedef', 'nis_gercek', 'nis_hedef', 
        'may_gercek', 'may_hedef', 'haz_gercek', 'haz_hedef',
        'tem_gercek', 'tem_hedef', 'agu_gercek', 'agu_hedef',
        'eyl_gercek', 'eyl_hedef', 'eki_gercek', 'eki_hedef',
        'kas_gercek', 'kas_hedef', 'ara_gercek', 'ara_hedef'
    )
    list_filter = ('satici',)
    search_fields = ('satici',)
    readonly_fields = ('yuzde_oran_display',)

    def yuzde_oran_display(self, obj):
        return f"{obj.yuzde_oran_hesapla():.2f}%"
    yuzde_oran_display.short_description = 'Yüzde Oran'

    fieldsets = (
        ('Genel Bilgiler', {
            'fields': ('satici',)
        }),
        ('Toplam Tutarlar', {
            'fields': ('toplam_gercek', 'toplam_hedef', 'yuzde_oran_display')
        }),
        ('Aylık Tutarlar', {
            'fields': (
                ('oca_gercek', 'oca_hedef'),
                ('sub_gercek', 'sub_hedef'),
                ('mar_gercek', 'mar_hedef'),
                ('nis_gercek', 'nis_hedef'),
                ('may_gercek', 'may_hedef'),
                ('haz_gercek', 'haz_hedef'),
                ('tem_gercek', 'tem_hedef'),
                ('agu_gercek', 'agu_hedef'),
                ('eyl_gercek', 'eyl_hedef'),
                ('eki_gercek', 'eki_hedef'),
                ('kas_gercek', 'kas_hedef'),
                ('ara_gercek', 'ara_hedef'),
            )
        }),
    )

admin.site.register(SalesBudget, SalesBudgetAdmin)
