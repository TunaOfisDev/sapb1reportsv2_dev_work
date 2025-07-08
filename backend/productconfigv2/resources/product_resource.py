# productconfigv2/resources/product_resource.py

from import_export import fields
from import_export.widgets import ForeignKeyWidget
from ..models import Product, ProductFamily
from ..resources.base_resource import BaseResource


class ProductFamilyResource(BaseResource):
    class Meta:
        model = ProductFamily
        fields = ("id", "name", "image", "created_at", "updated_at", "is_active")
        export_order = fields


class ProductResource(BaseResource):
    family_name = fields.Field(
        column_name="family_name",
        attribute="family",
        widget=ForeignKeyWidget(ProductFamily, field="name")
    )

    class Meta:
        model = Product
        fields = (
            "id", "code", "name", "image",
            "variant_code", "variant_description",
            "base_price", "currency", "variant_order",
            "family_name", "created_at", "updated_at", "is_active"
        )
        export_order = fields
