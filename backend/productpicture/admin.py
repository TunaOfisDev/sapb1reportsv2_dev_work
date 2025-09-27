# backend/productpicture/admin.py
from django.contrib import admin
from .models.productpicture_models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'item_name', 'group_name', 'price', 'currency', 'picture_name')
    search_fields = ['item_code', 'item_name', 'group_name']
    list_filter = ('group_name', 'currency')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is not None when editing an existing object
            return ['item_code', 'picture_name']
        return []

admin.site.register(Product, ProductAdmin)
