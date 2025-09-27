# productconfigv2/admin/product_admin.py

from django.contrib import admin
from django.shortcuts import render, redirect
from ..models import ProductFamily, Product, ProductSpecification
from ..admin.base_admin import BaseAdmin
from ..resources import ProductFamilyResource, ProductResource
from ..forms.bulk_spec_assignment_form import BulkSpecificationAssignmentForm


@admin.register(ProductFamily)
class ProductFamilyAdmin(BaseAdmin):
    resource_class = ProductFamilyResource
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 0
    autocomplete_fields = ["spec_type"]


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    resource_class = ProductResource
    list_display = (
        "name", "family", "variant_code", "variant_description",
        "base_price", "currency", "is_active"
    )
    search_fields = ("name", "family__name")
    list_filter = ("family", "currency", "is_active")
    autocomplete_fields = ["family"]
    inlines = [ProductSpecificationInline]


    actions = ["bulk_assign_specifications"]

    def bulk_assign_specifications(self, request, queryset):
        if "apply" in request.POST:
            form = BulkSpecificationAssignmentForm(request.POST)
            if form.is_valid():
                form.cleaned_data["products"] = queryset
                form.save()
                self.message_user(request, "Toplu özellik ataması başarıyla tamamlandı.")
                return redirect(request.get_full_path())
        else:
            form = BulkSpecificationAssignmentForm(initial={"products": queryset})

        return render(request, "admin/productconfigv2/bulk_spec_assignment_action.html", {
            "form": form,
            "title": "Seçilen Ürünlere Toplu Özellik Atama"
        })
    bulk_assign_specifications.short_description = "Toplu Özellik Tipi Ata"