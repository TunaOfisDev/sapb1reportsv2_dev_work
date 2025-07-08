# dosya path yolu: backend/productconfig/admin/brand.py
from django.contrib import admin
from ..models import Brand
from .base import GenericAdmin

@admin.register(Brand)
class BrandAdmin(GenericAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']
