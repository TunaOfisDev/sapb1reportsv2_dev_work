# backend/orderarchive/admin/order_archive_admin.py

from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin
from ..models.order_archive_model import OrderDetail
from ..resources.order_archive_resource import OrderDetailResource

@admin.register(OrderDetail)
class OrderDetailAdmin(ImportExportModelAdmin, ExportMixin):
    """
    Admin panelinde OrderDetail modelini görüntüler ve import/export işlemlerini destekler.
    """
    resource_class = OrderDetailResource

    # Admin panelinde görünecek tüm alanlar
    list_display = (
        "seller",
        "order_number",
        "order_date",
        "year",
        "month",
        "delivery_date",
        "country",
        "city",
        "customer_code",
        "customer_name",
        "document_description",
        "color_code",
        "detail_description",
        "line_number",
        "item_code",
        "item_description",
        "quantity",
        "unit_price",
        "vat_percentage",
        "vat_amount",
        "discount_rate",
        "discount_amount",
        "currency",
        "exchange_rate",
        "currency_price",
        "currency_movement_amount",
    )

    # Admin panelinde filtreleme için kullanılacak alanlar
    list_filter = ("seller", "order_date", "delivery_date", "currency", "country")

    # Arama yapılacak alanlar
    search_fields = ("order_number", "customer_name", "item_code", "item_description")

    # Alanların düzenlenebilir olması için belirli alanlar
    list_editable = ("quantity", "unit_price", "vat_percentage", "discount_rate")
