# productconfigv2/admin/variant_admin.py

from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import Variant, VariantSelection
from ..admin.base_admin import BaseAdmin
from ..resources import VariantResource
from ..forms.variant_bulk_creation_form import VariantBulkCreationForm
# GEREKLİ SERVİSİ İMPORT EDİYORUZ
from ..services.variant_service import update_variant_price_from_sap


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
        "project_name",
        "reference_code",
        "new_variant_code",
        "new_variant_description", 
        "product", 
        "total_price", 
        "is_active", 
        "created_at"
    )

    list_filter = (
        "product", 
        "project_name",
        "is_generated", 
        "is_active",
        "created_at"
    )
    
    search_fields = (
        "project_name",
        "reference_code", 
        "new_variant_code", 
        "new_variant_description", 
        "product__code", 
        "product__name"
    )
    
    autocomplete_fields = ["product"]
    inlines = [VariantSelectionInline]
    # actions listesi doğru
    actions = ["update_prices_from_sap", "generate_variants_action"]
    
    class Media:
        js = ("productconfigv2/js/variant_chained_select.js",)

    # YENİ EKLENEN VE EKSİK OLAN AKSİYON FONKSİYONU
    # -----------------------------------------------------------------
    @admin.action(description="Seçili varyantların fiyatını SAP'den güncelle")
    def update_prices_from_sap(self, request, queryset):
        success_count = 0
        fail_count = 0
        
        for variant in queryset:
            # Servis fonksiyonunu her bir varyant için çağır
            success, message = update_variant_price_from_sap(variant.id)
            if success:
                success_count += 1
            else:
                fail_count += 1
                # Başarısız olanları kullanıcıya mesaj olarak bildir
                messages.warning(request, f"{variant.new_variant_code}: {message}")
        
        # İşlem sonunda genel bir başarı mesajı göster
        if success_count > 0:
            messages.success(request, f"{success_count} varyantın fiyatı SAP'den başarıyla güncellendi.")
        if fail_count > 0:
            # Eğer hata varsa, genel bir hata mesajı da göster
            messages.error(request, f"{fail_count} varyantın fiyatı güncellenemedi. Detaylar için uyarılara bakın.")
    # -----------------------------------------------------------------


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