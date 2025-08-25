# path: /var/www/sapb1reportsv2/backend/nexuscore/admin.py

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import DynamicDBConnection, VirtualTable

# --- 1. DynamicDBConnection için Kaynak ve Admin Yapılandırması ---

class DynamicDBConnectionResource(resources.ModelResource):
    """
    DynamicDBConnection modeli için hangi alanların nasıl import/export edileceğini tanımlar.
    """
    class Meta:
        model = DynamicDBConnection
        # GÜVENLİK UYARISI: `json_config` alanı, hassas bilgiler (şifreler) içerdiği için
        # KESİNLİKLE dışarı aktarılmamalıdır. Bu yüzden 'fields' listesine dahil etmiyoruz.
        fields = ('id', 'title', 'db_type', 'is_active', 'created_at', 'updated_at')
        export_order = fields # Dışa aktarım sırası da aynı olsun.

@admin.register(DynamicDBConnection)
class DynamicDBConnectionAdmin(ImportExportModelAdmin):
    """
    DynamicDBConnection modelinin admin panelindeki görünümünü ve davranışlarını yönetir.
    Import/Export butonlarını ekler.
    """
    resource_class = DynamicDBConnectionResource
    list_display = ('title', 'db_type', 'is_active', 'updated_at')
    list_filter = ('db_type', 'is_active')
    search_fields = ('title',)
    
    # Detay sayfasındaki alanları daha düzenli göstermek için fieldsets kullanalım.
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'db_type', 'is_active')
        }),
        ('Yapılandırma (Hassas Veri)', {
            'description': "Bu alana girilen şifreler veritabanında şifrelenerek saklanır.",
            'fields': ('json_config',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Bu bölümü varsayılan olarak kapalı tutar.
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# --- 2. VirtualTable için Kaynak ve Admin Yapılandırması ---

class VirtualTableResource(resources.ModelResource):
    """
    VirtualTable modeli için import/export kurallarını tanımlar.
    """
    class Meta:
        model = VirtualTable

@admin.register(VirtualTable)
class VirtualTableAdmin(ImportExportModelAdmin):
    """
    VirtualTable modelinin admin panelindeki görünümünü ve davranışlarını yönetir.
    """
    resource_class = VirtualTableResource
    list_display = ('title', 'connection', 'owner', 'sharing_status', 'updated_at')
    list_filter = ('sharing_status', 'connection__db_type', 'owner')
    search_fields = ('title', 'sql_query', 'owner__email')
    
    # Çok sayıda kullanıcı veya bağlantı olduğunda standart dropdown'lar yavaşlar.
    # `raw_id_fields`, daha performanslı bir seçim arayüzü sunar.
    raw_id_fields = ('owner', 'connection')

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
    readonly_fields = ('created_at', 'updated_at')
