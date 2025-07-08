# backend/filesharehub/admin.py

from django.contrib import admin
from .models.models import Directory, FileRecord

class DirectoryAdmin(admin.ModelAdmin):
    """
    Directory modelini admin panelinde yönetmek için ayarlar.
    """
    list_display = ('path', 'last_scanned', 'created_at', 'updated_at')  # Görüntülenecek alanlar
    search_fields = ('path',)  # Arama yapılacak alanlar
    readonly_fields = ('last_scanned', 'created_at', 'updated_at')  # Değiştirilemeyen alanlar
    list_filter = ('last_scanned',)  # Filtreleme seçenekleri

    def has_add_permission(self, request):
        """
        Kullanıcıların admin paneli üzerinden yeni Directory kaydı ekleyip ekleyemeyeceğini belirler.
        """
        return False  # Dizinler sistem tarafından oluşturulmalı, admin panelinden eklenmemeli

class FileRecordAdmin(admin.ModelAdmin):
    """
    FileRecord modelini admin panelinde yönetmek için ayarlar.
    """
    list_display = ('filename', 'file_path', 'size', 'last_modified', 'directory', 'created_at', 'updated_at')  # Görüntülenecek alanlar
    search_fields = ('filename', 'file_path')  # Arama yapılacak alanlar
    readonly_fields = ('file_path', 'size', 'last_modified', 'created_at', 'updated_at')  # Değiştirilemeyen alanlar
    list_filter = ('directory', 'last_modified')  # Filtreleme seçenekleri

    def has_add_permission(self, request):
        """
        Kullanıcıların admin paneli üzerinden yeni FileRecord kaydı ekleyip ekleyemeyeceğini belirler.
        """
        return False  # Dosyalar sistem tarafından taranıp eklenmeli, admin panelinden eklenmemeli

    def has_delete_permission(self, request, obj=None):
        """
        Dosya kayıtlarının admin paneli üzerinden silinmesini kontrol eder.
        """
        return True  # Admin panelinden silinebilir

# Modelleri admin paneline kaydet
admin.site.register(Directory, DirectoryAdmin)
admin.site.register(FileRecord, FileRecordAdmin)
