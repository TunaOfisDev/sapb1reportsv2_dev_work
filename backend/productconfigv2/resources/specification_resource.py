# backend/productconfigv2/resources/specification_resource.py

from import_export import fields
from import_export.widgets import ForeignKeyWidget
from ..models import SpecificationType, SpecOption
from ..resources.base_resource import BaseResource

class SpecificationTypeResource(BaseResource):
    class Meta:
        model = SpecificationType
        fields = (
            "id", "name", "group",
            "is_required", "allow_multiple",
            "variant_order", "display_order", "multiplier",
            "created_at", "updated_at", "is_active"
        )
        export_order = (
            "id", "name", "group",
            "is_required", "allow_multiple",
            "variant_order", "display_order", "multiplier",
            "created_at", "updated_at", "is_active"
        )




class SpecOptionResource(BaseResource):
    spec_type_name = fields.Field(
        column_name="spec_type_name",
        attribute="spec_type",
        widget=ForeignKeyWidget(SpecificationType, field="name")
    )

    class Meta:
        model = SpecOption
        fields = (
            "id", "name", "variant_code", "variant_description",
            "reference_code", # YENİ ALAN
            "image", "price_delta", "is_default", "display_order",
            "spec_type_name", "created_at", "updated_at", "is_active"
        )
        export_order = fields # 'fields' kullanmak, export_order'ı otomatik günceller
