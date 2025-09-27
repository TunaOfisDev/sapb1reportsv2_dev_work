# backend/salesbudgeteur/admin.py

from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources

from salesbudgeteur.models.salesbudget_model import (
    SalesBudgetEURModel,
    MonthlySalesBudgetEUR
)


class SalesBudgetEURResource(resources.ModelResource):
    class Meta:
        model = SalesBudgetEURModel
        fields = (
            "id", "satici", "yil",
            "toplam_gercek_eur", "toplam_hedef_eur",
            "toplam_iptal_eur", "toplam_elle_kapanan_eur",
            "kapali_sip_list", "created_at", "updated_at"
        )


@admin.register(SalesBudgetEURModel)
class SalesBudgetEURAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "satici", "yil",
        "toplam_gercek_eur", "toplam_hedef_eur",
        "toplam_iptal_eur", "toplam_elle_kapanan_eur"
    )
    search_fields = ("satici",)
    list_filter = ("yil",)
    readonly_fields = ("created_at", "updated_at")
    resource_class = SalesBudgetEURResource


class MonthlySalesBudgetEURInline(admin.TabularInline):
    model = MonthlySalesBudgetEUR
    extra = 0


@admin.register(MonthlySalesBudgetEUR)
class MonthlySalesBudgetEURAdmin(admin.ModelAdmin):
    list_display = ("get_satici", "ay", "gercek_tutar", "hedef_tutar")
    list_filter = ("ay", "parent__satici")
    search_fields = ("parent__satici",)

    def get_satici(self, obj):
        return obj.parent.satici
    get_satici.short_description = "Satıcı"
