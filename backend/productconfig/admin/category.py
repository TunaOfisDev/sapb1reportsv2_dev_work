# dosya path yolu: backend/productconfig/admin/category.py
from django.contrib import admin
from ..models import Category
from .base import GenericAdmin

@admin.register(Category)
class CategoryAdmin(GenericAdmin):
    list_display = ['name', 'brand', 'product_group', 'id']
    list_filter = ['brand', 'product_group']
    search_fields = ['name', 'brand__name', 'product_group__name']
