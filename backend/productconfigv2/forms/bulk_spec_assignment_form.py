# backend/productconfigv2/forms/bulk_spec_assignment_form.py

from django import forms
from productconfigv2.models import Product, SpecificationType


class BulkSpecificationAssignmentForm(forms.Form):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Ürünler",
        help_text="Toplu işlem yapılacak ürünleri seçiniz."
    )

    spec_types = forms.ModelMultipleChoiceField(
        queryset=SpecificationType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Özellik Tipleri",
        help_text="Hangi özellik tiplerinin atanacağını seçiniz."
    )

    is_required = forms.BooleanField(
        required=False,
        initial=True,
        label="Zorunlu Mu?",
        help_text="Seçilen özellik tipi ürün için zorunlu olarak mı işaretlensin?"
    )

    allow_multiple = forms.BooleanField(
        required=False,
        initial=False,
        label="Çoklu Seçim İzinli Mi?",
        help_text="Bu özellik tipi için çoklu seçim yapılmasına izin verilsin mi?"
    )

    variant_order_start = forms.IntegerField(
        required=False,
        initial=1,
        label="Başlangıç Sırası",
        help_text="İsteğe bağlı: Her özellik tipi için varyant sırasını bu sayıyla başlat."
    )

    def save(self):
        from productconfigv2.models import ProductSpecification

        cleaned = self.cleaned_data
        products = cleaned["products"]
        spec_types = cleaned["spec_types"]
        is_required = cleaned["is_required"]
        allow_multiple = cleaned["allow_multiple"]
        start_order = cleaned.get("variant_order_start") or 1

        for product in products:
            for index, spec_type in enumerate(spec_types, start=start_order):
                ProductSpecification.objects.get_or_create(
                    product=product,
                    spec_type=spec_type,
                    defaults={
                        "is_required": is_required,
                        "allow_multiple": allow_multiple,
                        "variant_order": index,
                        "display_order": index
                    }
                )
