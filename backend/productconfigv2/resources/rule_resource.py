# productconfigv2/resources/rule_resource.py

from import_export import fields
from import_export.widgets import ForeignKeyWidget
from ..models import Rule, ProductFamily
from ..resources.base_resource import BaseResource


class RuleResource(BaseResource):
    product_family_code = fields.Field(
        column_name="product_family_code",
        attribute="product_family",
        widget=ForeignKeyWidget(ProductFamily, field="code")
    )

    class Meta:
        model = Rule
        fields = (
            "id", "name", "rule_type",
            "product_family_code", "conditions", "actions",
            "created_at", "updated_at", "is_active"
        )
        export_order = fields
