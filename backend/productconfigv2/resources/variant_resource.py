# productconfigv2/resources/variant_resource.py

from import_export import fields
from import_export.widgets import ForeignKeyWidget
from ..models import Variant, Product
from ..resources.base_resource import BaseResource


class VariantResource(BaseResource):
    product_code = fields.Field(
        column_name="product_code",
        attribute="product",
        widget=ForeignKeyWidget(Product, field="code")
    )

    class Meta:
        model = Variant
        fields = (
            "id", "product_code", "new_variant_code", "new_variant_description", "image",
            "total_price", "currency", "is_generated",
            "created_at", "updated_at", "is_active"
        )
        export_order = fields

