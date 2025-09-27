# backend/activities/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models.models import Activity

class ActivityResource(resources.ModelResource):
    class Meta:
        model = Activity
        import_id_fields = ('numara',)
        fields = ('numara', 'baslangic_tarihi', 'bitis_tarihi', 'baslama_saati', 'bitis_saati', 'sure', 'isleyen', 'tayin_eden', 'aktivite', 'tur', 'konu', 'muhatap_kod', 'muhatap_ad', 'durum', 'aciklama', 'icerik')

class ActivityAdmin(ImportExportModelAdmin):
    resource_class = ActivityResource
    list_display = ('numara', 'baslangic_tarihi', 'bitis_tarihi', 'baslama_saati', 'bitis_saati', 'sure', 'isleyen', 'tayin_eden', 'aktivite', 'tur', 'konu', 'muhatap_kod', 'muhatap_ad', 'durum', 'aciklama', 'icerik')
    list_filter = ('baslangic_tarihi', 'aktivite', 'durum')
    search_fields = ('numara', 'isleyen', 'muhatap_ad', 'aciklama')
    ordering = ('baslangic_tarihi',)

    # Ekstra özellikler eklemek isterseniz, form veya fieldsets gibi özellikler burada tanımlanabilir.
    fieldsets = (
        (None, {'fields': ('numara', 'baslangic_tarihi', 'bitis_tarihi', 'baslama_saati', 'bitis_saati', 'sure')}),
        ('Detaylar', {'fields': ('isleyen', 'tayin_eden', 'aktivite', 'tur', 'konu', 'muhatap_kod', 'muhatap_ad', 'durum', 'aciklama', 'icerik')}),
    )

admin.site.register(Activity, ActivityAdmin)
