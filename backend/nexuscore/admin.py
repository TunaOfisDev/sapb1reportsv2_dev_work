# path: /var/w ww/sapb1reportsv2/backend/nexuscore/admin.py

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# ### YENİ: ReportTemplate modelini de import ediyoruz ###
from .models import DynamicDBConnection, VirtualTable, ReportTemplate

# --- 1. DynamicDBConnection Admin ---

class DynamicDBConnectionResource(resources.ModelResource):
    class Meta:
        model = DynamicDBConnection
        # Güvenlik nedeniyle hassas `config_json` alanını export dışı bırakıyoruz.
        exclude = ('config_json',)

@admin.register(DynamicDBConnection)
class DynamicDBConnectionAdmin(ImportExportModelAdmin):
    resource_class = DynamicDBConnectionResource
    list_display = ('title', 'db_type', 'is_active', 'owner', 'updated_at')
    list_filter = ('db_type', 'is_active')
    search_fields = ('title', 'owner__email')
    raw_id_fields = ('owner',)
    list_per_page = 20
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('owner', 'title', 'db_type', 'is_active')
        }),
        ('Yapılandırma (Şifreli Veri)', {
            'description': "Hassas bağlantı bilgileri bu alanda şifrelenerek saklanır.",
            'fields': ('config_json',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# --- 2. VirtualTable Admin ---

class VirtualTableResource(resources.ModelResource):
    class Meta:
        model = VirtualTable

@admin.register(VirtualTable)
class VirtualTableAdmin(ImportExportModelAdmin):
    resource_class = VirtualTableResource
    list_display = ('title', 'connection', 'owner', 'sharing_status', 'updated_at')
    list_filter = ('sharing_status', 'connection__db_type', 'owner')
    search_fields = ('title', 'sql_query', 'owner__email')
    raw_id_fields = ('owner', 'connection')
    list_per_page = 20

    fieldsets = (
        ('Sanal Tablo Bilgileri', {
            'fields': ('title', 'owner', 'connection', 'sharing_status')
        }),
        ('Sorgu ve Meta Veri', {
            'fields': ('sql_query', 'column_metadata')
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'column_metadata')

# --- 3. ReportTemplate Admin (YENİ) ---

class ReportTemplateResource(resources.ModelResource):
    class Meta:
        model = ReportTemplate
        
@admin.register(ReportTemplate)
class ReportTemplateAdmin(ImportExportModelAdmin):
    """
    ReportTemplate modelinin admin panelindeki görünümünü ve davranışlarını yönetir.
    """
    resource_class = ReportTemplateResource
    list_display = ('title', 'source_virtual_table', 'owner', 'sharing_status', 'updated_at')
    list_filter = ('sharing_status', 'owner', 'source_virtual_table__connection__db_type')
    search_fields = ('title', 'description', 'owner__email')
    raw_id_fields = ('owner', 'source_virtual_table')
    list_per_page = 20
    
    fieldsets = (
        ('Rapor Bilgileri', {
            'fields': ('title', 'description', 'owner', 'source_virtual_table', 'sharing_status')
        }),
        ('Rapor Yapılandırması', {
            'description': "Kullanıcının Playground'da oluşturduğu rapor ayarları (kolonlar, sıralama vb.).",
            'fields': ('configuration_json',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')