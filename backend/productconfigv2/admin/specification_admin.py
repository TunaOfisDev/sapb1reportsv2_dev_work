# productconfigv2/admin/specification_admin.py

from django.contrib import admin
from django.http import JsonResponse
from ..models import (
    SpecificationType, SpecOption,
    SpecificationOption
)
from ..admin.base_admin import BaseAdmin
from ..resources import (
    SpecificationTypeResource,
    SpecOptionResource
)


class SpecOptionInline(admin.TabularInline):
    model = SpecOption
    extra = 0
    fields = ("name", "variant_code", "variant_description", "price_delta", "is_default", "display_order")
    ordering = ("display_order",)


@admin.register(SpecificationType)
class SpecificationTypeAdmin(BaseAdmin):
    resource_class = SpecificationTypeResource

    list_display = ("name", "group", "variant_order", "display_order", "is_active")
    search_fields = ("name", "group")
    list_filter = ("group", "is_required", "allow_multiple", "is_active")
    inlines = [SpecOptionInline]


@admin.register(SpecOption)
class SpecOptionAdmin(BaseAdmin):
    resource_class = SpecOptionResource

    list_display = ("name", "spec_type", "price_delta", "is_default", "is_active")
    search_fields = ("name", "spec_type__name")
    list_filter = ("spec_type", "is_default", "is_active")
    autocomplete_fields = ["spec_type"]

    def changelist_view(self, request, extra_context=None):
        # Format=json parametresi varsa JSON yanıt döndür
        if request.GET.get("format") == "json":
            spec_type_id = request.GET.get("spec_type__id__exact")
            if spec_type_id:
                queryset = SpecOption.objects.filter(
                    spec_type_id=spec_type_id,
                    is_active=True
                ).order_by("display_order")
                
                data = {
                    "results": [
                        {"id": option.id, "name": str(option.name)}
                        for option in queryset
                    ]
                }
                return JsonResponse(data)
        
        # Normal görünüm için standart işlemi yap
        return super().changelist_view(request, extra_context)


@admin.register(SpecificationOption)
class SpecificationOptionAdmin(BaseAdmin):
    list_display = ("product", "spec_type", "option", "is_default", "is_active")
    list_filter = ("product", "spec_type", "is_default", "is_active")
    search_fields = ("product__name", "option__name")
    autocomplete_fields = ["product", "spec_type", "option"]

