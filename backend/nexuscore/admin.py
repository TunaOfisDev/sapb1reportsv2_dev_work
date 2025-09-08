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
    AppRelationship
)

# --- 1. DynamicDBConnection Admin ---
# (Bu sınıf değişmedi, olduğu gibi kalıyor)
class DynamicDBConnectionResource(resources.ModelResource):
    class Meta:
        model = DynamicDBConnection
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
# (Bu sınıf değişmedi, olduğu gibi kalıyor)
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
# Bu, DataApp oluşturma sayfasının İÇİNDE ilişkileri eklememizi sağlar.

class AppRelationshipInline(admin.TabularInline):
    """
    DataApp admin paneli içinde JOIN ilişkilerini yönetmek için inline arayüz.
    """
    model = AppRelationship
    fk_name = 'app'
    extra = 1 # Varsayılan olarak 1 yeni boş satır göster
    verbose_name = "Veri Modeli İlişkisi"
    verbose_name_plural = "Veri Modeli İlişkileri (JOINs)"
    
    # Binlerce sanal tablo olabileceği için dropdown yerine arama kutusu kullanalım.
    # Bu, VirtualTableAdmin'de 'search_fields' tanımlı olduğu için çalışır.
    autocomplete_fields = ['left_table', 'right_table']


# --- 4. YENİ: DataApp Admin ---
# Yeni DataApp modelimizi yönetmek için admin arayüzü

@admin.register(DataApp)
class DataAppAdmin(ImportExportModelAdmin):
    """
    DataApp (Veri Uygulaması) modelinin admin arayüzü.
    İlişkiler (Relationships) bu arayüzün içinde inline olarak yönetilir.
    """
    list_display = ('title', 'connection', 'owner', 'sharing_status', 'updated_at')
    list_filter = ('sharing_status', 'connection__db_type', 'owner')
    search_fields = ('title', 'description', 'owner__email')
    
    # Bağlantılar için raw_id veya autocomplete kullanalım
    raw_id_fields = ('owner', 'connection')
    
    # ManyToMany alanı için bu widget, 'raw_id'den çok daha kullanışlıdır
    filter_horizontal = ('virtual_tables',)
    
    # İlişki yöneticisini bu sayfaya dahil et
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
# CRASH HATASINI GİDEREN DEĞİŞİKLİKLER BURADA

class ReportTemplateResource(resources.ModelResource):
    class Meta:
        model = ReportTemplate
        
@admin.register(ReportTemplate)
class ReportTemplateAdmin(ImportExportModelAdmin):
    """
    ReportTemplate modelinin admin panelindeki görünümünü yönetir.
    Artık 'source_data_app' alanına referans verecek şekilde güncellendi.
    """
    resource_class = ReportTemplateResource
    
    # --- DÜZELTME 1: list_display ---
    list_display = ('title', 'source_data_app', 'owner', 'sharing_status', 'updated_at')
    
    # --- DÜZELTME 2: list_filter ---
    # Yeni ilişki yolu: source_data_app -> connection -> db_type
    list_filter = ('sharing_status', 'owner', 'source_data_app__connection__db_type')
    
    search_fields = ('title', 'description', 'owner__email')
    
    # --- DÜZELTME 3: raw_id_fields ---
    raw_id_fields = ('owner', 'source_data_app')
    
    list_per_page = 20
    
    fieldsets = (
        ('Rapor Bilgileri', {
            # --- DÜZELTME 4: fieldsets ---
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