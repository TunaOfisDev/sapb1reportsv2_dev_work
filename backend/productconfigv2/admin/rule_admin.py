# productconfigv2/admin/rule_admin.py

from django.contrib import admin
from ..models import Rule
from ..admin.base_admin import BaseAdmin
from ..resources import RuleResource
from ..forms.rule_definition_form import RuleDefinitionForm  # Formu içeri alıyoruz


@admin.register(Rule)
class RuleAdmin(BaseAdmin):
    resource_class = RuleResource
    form = RuleDefinitionForm  # Formu admin ile bağladık

    list_display = ("name", "rule_type", "product_family", "is_active", "created_at")
    search_fields = ("name", "product_family__name")
    list_filter = ("rule_type", "product_family", "is_active")
    autocomplete_fields = ["product_family"]

    fieldsets = (
        (None, {
            "fields": ("name", "rule_type", "product_family", "is_active")
        }),
        ("JSON Kuralları", {
            "fields": ("conditions", "actions"),
            
        }),
    )

