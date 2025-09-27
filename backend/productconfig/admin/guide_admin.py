# backend/productconfig/admin/guide_admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from ..models.guide import Guide

# Guide modeli için kaynak sınıfı
class GuideResource(resources.ModelResource):
    class Meta:
        model = Guide
        fields = ('id', 'title', 'category', 'description', 'steps', 'is_active', 'created_at', 'updated_at')
        export_order = ('id', 'title', 'category', 'description', 'steps', 'is_active', 'created_at', 'updated_at')

@admin.register(Guide)
class GuideAdmin(ImportExportModelAdmin):
    """
    Admin paneli için Guide modeli yönetim arayüzü.
    İçe ve dışa aktarma özellikleri XLSX formatında desteklenir.
    """
    resource_class = GuideResource
    list_display = ('id', 'title', 'category', 'description', 'steps')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'category')
    ordering = ('id',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("Kılavuz Bilgileri", {
            'fields': ('title', 'category', 'description', 'steps', 'is_active')
        }),
        ("Zaman Bilgileri", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Yalnızca mevcut nesneler için zaman bilgilerini düzenlemeye kapatır.
        """
        if obj:  # Eğer nesne mevcutsa (düzenleme sırasında)
            return self.readonly_fields + ('title',)
        return self.readonly_fields
