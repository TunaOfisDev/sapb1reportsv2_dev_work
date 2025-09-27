# dosya path yolu: backend/productconfig/admin/product_group.py

from django.contrib import admin
from import_export.admin import ExportMixin
from ..models import ProductGroup
from .resources import GenericResource


class ProductGroupResource(GenericResource):
    """
    ProductGroup için Import-Export kaynağı.
    """
    class Meta:
        model = ProductGroup


@admin.register(ProductGroup)
class ProductGroupAdmin(ExportMixin, admin.ModelAdmin):
    """
    ProductGroup modeli için admin sınıfı.
    """
    resource_class = ProductGroupResource
    list_display = ['name', 'brand', 'id']
    list_filter = ['brand']
    search_fields = ['name', 'brand__name']
    ordering = ['brand', 'name']

    # Oluşturma ve güncelleme tarihlerini gizlemek için:
    exclude = ['created_at', 'updated_at']
