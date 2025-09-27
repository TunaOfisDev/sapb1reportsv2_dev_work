# dosya path yolu: backend/productconfig/admin/variant.py
from django.contrib import admin
from import_export.admin import ExportMixin
from ..models import Variant
from .resources import GenericResource

class VariantResource(GenericResource):
    """
    Variant modeli için Import-Export kaynağı.
    """
    class Meta:
        model = Variant


@admin.register(Variant)
class VariantAdmin(ExportMixin, admin.ModelAdmin):
    """
    Variant modeli için admin paneli ayarları.
    """
    resource_class = VariantResource
    list_display = [
        'id', 'project_name', 'variant_code', 'variant_description', 
        'sap_item_code', 'sap_item_description', 'sap_U_eski_bilesen_kod', 
        'sap_price', 'sap_currency', 'old_component_codes',
        'total_price', 'status', 'created_at', 'updated_at'
    ]
    list_filter = ['status', 'created_at', 'updated_at']
    filter_input_length = 25  # Filtreleme alanının genişliği ayarlanabilir
    exclude = ['created_at', 'updated_at']
    search_fields = ['project_name', 'variant_code', 'variant_description', 'sap_item_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'sap_item_code', 'sap_item_description', 
                       'sap_U_eski_bilesen_kod', 'sap_price', 'sap_currency']

    def save_model(self, request, obj, form, change):
        """
        Variant modeli kayıt işlemleri.
        """
        super().save_model(request, obj, form, change)

