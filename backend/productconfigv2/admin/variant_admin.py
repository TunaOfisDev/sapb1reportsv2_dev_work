# productconfigv2/admin/variant_admin.py

from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import Variant, VariantSelection
from ..admin.base_admin import BaseAdmin
from ..resources import VariantResource
from ..forms.variant_bulk_creation_form import VariantBulkCreationForm


class VariantSelectionInline(admin.TabularInline):
    model = VariantSelection
    extra = 0
    verbose_name = "Özellik Seçimi"
    verbose_name_plural = "Varyant Özellik Seçimleri"
    autocomplete_fields = ["spec_type", "option"]

    class Media:
        js = ("productconfigv2/js/variant_chained_select.js",)



@admin.register(Variant)
class VariantAdmin(BaseAdmin):
    resource_class = VariantResource
    
    list_display = (
        "new_variant_code", "new_variant_description", "product", "total_price", "currency", "is_generated",
        "is_active", "created_at"
    )
    list_filter = ("product", "currency", "is_generated", "is_active")
    search_fields = ("new_variant_code", "new_variant_description", "product__code", "product__name")
    autocomplete_fields = ["product"]
    inlines = [VariantSelectionInline]
    actions = ["generate_variants_action"]
    
    class Media:
        js = ("productconfigv2/js/variant_chained_select.js",)

    def generate_variants_action(self, request, queryset):
        if "apply" in request.POST:
            form = VariantBulkCreationForm(request.POST)
            if form.is_valid():
                created = form.save()
                messages.success(request, f"{len(created)} varyant başarıyla oluşturuldu.")
                return redirect(request.get_full_path())
        else:
            form = VariantBulkCreationForm()

        return render(request, "admin/productconfigv2/variant_bulk_creation_form.html", {
            "form": form,
            "title": "Toplu Varyant Oluştur"
        })
    generate_variants_action.short_description = "Toplu Varyant Üretimi"

