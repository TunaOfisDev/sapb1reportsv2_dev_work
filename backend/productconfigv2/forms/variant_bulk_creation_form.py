# backend/productconfigv2/forms/variant_bulk_creation_form.py

from django import forms
from ..models import Product
from ..services.variant_service import batch_create_variants


class VariantBulkCreationForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Ürün",
        help_text="Varyantlarını oluşturmak istediğiniz ürünü seçin."
    )

    generate_all = forms.BooleanField(
        required=False,
        initial=True,
        label="Tüm olasılıkları üret",
        help_text="Seçili ürün için mümkün olan tüm varyant kombinasyonlarını oluşturur."
    )

    is_generated_flag = forms.BooleanField(
        required=False,
        initial=True,
        label="Otomatik Oluşturulmuş olarak işaretle",
        help_text="Oluşturulan varyantlara 'is_generated=True' bayrağı eklenir."
    )

    def save(self):
        product = self.cleaned_data["product"]
        generate_all = self.cleaned_data.get("generate_all", True)
        is_generated = self.cleaned_data.get("is_generated_flag", True)

        created_variants = batch_create_variants(
            product=product,
            generate_all=generate_all,
            is_generated=is_generated
        )

        return created_variants
