# backend/bomcostmanager/admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models.bomcomponent_models import BOMComponent, BOMRecord
from .models.bomproduct_models import BOMProduct

@admin.register(BOMComponent)
class BOMComponentAdmin(ImportExportModelAdmin):
    list_display = (
        "main_item", "sub_item", "component_item_code", "component_item_name",
        "quantity", "level", "type_description", "last_purchase_price", "currency",
        "rate", "last_purchase_price_upb", "price_source", "doc_date", "component_cost_upb",
        "sales_price", "sales_currency", "price_list_name", "item_group_name",
        "new_last_purchase_price", "new_currency", "labor_multiplier",
        "overhead_multiplier", "license_multiplier", "commission_multiplier",
        "updated_cost"
    )
    search_fields = ("main_item", "component_item_code", "component_item_name")
    list_filter = ("level", "currency", "price_source", "item_group_name")


@admin.register(BOMRecord)
class BOMRecordAdmin(ImportExportModelAdmin):
    list_display = (
        "project_name", "description", "created_by", "created_at", "updated_at"
    )
    search_fields = ("project_name", "created_by")
    list_filter = ("project_name",)


@admin.register(BOMProduct)
class BOMProductAdmin(ImportExportModelAdmin):
    list_display = (
        "item_code", "item_name", "default_wh", "invnt_item", "sell_item",
        "purch_item", "sales_price_list", "sales_price", "currency",
        "bom_create_date", "bom_update_date", "created_user_code",
        "updated_user_code", "last_fetched_at"
    )
    search_fields = ("item_code", "item_name")
    list_filter = ("currency", "invnt_item", "sell_item", "purch_item")
