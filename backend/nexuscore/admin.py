# path: /var/www/sapb1reportsv2/backend/nexuscore/admin.py

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# ### GÜNCELLEME: Tüm modellerimizi import ediyoruz ###
from .models import (
    DynamicDBConnection, 
    VirtualTable, 
    ReportTemplate, 
    DataApp, 
    AppRelationship,
    DBTypeMapping # YENİ: Dinamik eşleştirme modelimizi ekliyoruz
)

# --- 1. DynamicDBConnection Admin ---
class DynamicDBConnectionResource(resources.ModelResource):
    class Meta:
        model = DynamicDBConnection
        exclude = ('config_json',)

@admin.register(DynamicDBConnection)
class DynamicDBConnectionAdmin(ImportExportModelAdmin):
    resource_class = DynamicDBConnectionResource
    list_display = ('id','title', 'db_type', 'is_active', 'owner', 'updated_at')
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


# --- 3. YENİ: DataApp İlişkileri için Inline Admin ---
class AppRelationshipInline(admin.TabularInline):
    """
    DataApp admin paneli içinde JOIN ilişkilerini yönetmek için inline arayüz.
    """
    model = AppRelationship
    fk_name = 'app'
    extra = 1
    verbose_name = "Veri Modeli İlişkisi"
    verbose_name_plural = "Veri Modeli İlişkileri (JOINs)"
    autocomplete_fields = ['left_table', 'right_table']


# --- 4. YENİ: DataApp Admin ---
@admin.register(DataApp)
class DataAppAdmin(ImportExportModelAdmin):
    """
    DataApp (Veri Uygulaması) modelinin admin arayüzü.
    """
    list_display = ('title', 'connection', 'owner', 'sharing_status', 'updated_at')
    list_filter = ('sharing_status', 'connection__db_type', 'owner')
    search_fields = ('title', 'description', 'owner__email')
    raw_id_fields = ('owner', 'connection')
    filter_horizontal = ('virtual_tables',)
    inlines = [AppRelationshipInline]
    
    fieldsets = (
        ('Uygulama Bilgileri', {
            'fields': ('title', 'description', 'owner', 'connection', 'sharing_status')
        }),
        ('Uygulama Veri Seti (Sanal Tablolar)', {
            'description': "Bu uygulamada kullanılacak TÜM sanal tabloları seçin.",
            'fields': ('virtual_tables',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# --- 5. GÜNCELLENMİŞ: ReportTemplate Admin ---
class ReportTemplateResource(resources.ModelResource):
    class Meta:
        model = ReportTemplate
        
@admin.register(ReportTemplate)
class ReportTemplateAdmin(ImportExportModelAdmin):
    """
    ReportTemplate modelinin admin panelindeki görünümünü yönetir.
    """
    resource_class = ReportTemplateResource
    list_display = ('title', 'source_data_app', 'owner', 'sharing_status', 'updated_at')
    list_filter = ('sharing_status', 'owner', 'source_data_app__connection__db_type')
    search_fields = ('title', 'description', 'owner__email')
    raw_id_fields = ('owner', 'source_data_app')
    list_per_page = 20
    
    fieldsets = (
        ('Rapor Bilgileri', {
            'fields': ('title', 'description', 'owner', 'source_data_app', 'sharing_status')
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


# --- 6. YENİ VE NİHAİ ÇÖZÜM: DBTypeMapping Admin ---
@admin.register(DBTypeMapping)
class DBTypeMappingAdmin(ImportExportModelAdmin):
    """
    Dinamik olarak keşfedilen veritabanı tiplerinin yönetim paneli.
    Yöneticiler, eşleşmeyen 'other' tiplerini buradan düzeltebilir.
    """
    list_display = ('db_type', 'source_type', 'general_category')
    list_filter = ('db_type', 'general_category')
    search_fields = ('db_type', 'source_type')
    list_per_page = 20
    # general_category'nin manuel olarak güncellenebilmesini sağlıyoruz
    list_editable = ['general_category']
    # Sadece db_type ve source_type'ın okunabilir olmasını sağlıyoruz
    readonly_fields = ('db_type', 'source_type')