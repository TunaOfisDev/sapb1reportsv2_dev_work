# productconfigv2/forms/product_config_import_form.py

from django import forms
from django.core.validators import FileExtensionValidator
from ..models import ProductFamily, Product

class ProductConfigImportForm(forms.Form):
    """
    Ürün konfigürasyon verilerini Excel dosyasından içe aktarmak için form.
    """
    excel_file = forms.FileField(
        label="Excel Dosyası",
        help_text="Ürün konfigürasyon verilerini içeren Excel dosyası (.xlsx)",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx'])]
    )
    
    product_family = forms.ModelChoiceField(
        label="Ürün Ailesi",
        queryset=ProductFamily.objects.filter(is_active=True),
        help_text="Konfigürasyonun ait olduğu ürün ailesi"
    )
    
    product_name = forms.CharField(
        label="Ürün Adı",
        max_length=255,
        help_text="Oluşturulacak ürünün adı"
    )
    
    product_code = forms.CharField(
        label="Ürün Kodu",
        max_length=50,
        help_text="Ürünün benzersiz kodu (örn. 55.BW.TEKIL)"
    )
    
    variant_code = forms.CharField(
        label="Varyant Kodu",
        max_length=50,
        help_text="Ürünün varyant kodu (örn. BW, EM)"
    )
    
    variant_description = forms.CharField(
        label="Varyant Açıklaması",
        max_length=255,
        help_text="Ürün varyantının açıklaması"
    )
    
    base_price = forms.DecimalField(
        label="Baz Fiyat",
        max_digits=12,
        decimal_places=2,
        help_text="Ürünün temel fiyatı"
    )
    
    currency = forms.ChoiceField(
        label="Para Birimi",
        choices=[('TL', 'TL'), ('USD', 'USD'), ('EUR', 'EUR')],
        initial='TL',
        help_text="Fiyat para birimi"
    )
    
    variant_order = forms.IntegerField(
        label="Varyant Sırası",
        initial=1,
        help_text="Varyantın sıralama değeri"
    )
    
    group_name = forms.CharField(
        label="Grup Adı",
        max_length=100,
        help_text="Özellik gruplarının ait olacağı grup adı (örn. BEEWORK, EMOTION)"
    )
    
    create_new_product = forms.BooleanField(
        label="Yeni Ürün Oluştur",
        required=False,
        initial=True,
        help_text="İşaretliyse yeni ürün oluşturulur, değilse mevcut ürün güncellenir."
    )
    
    existing_product = forms.ModelChoiceField(
        label="Mevcut Ürün",
        queryset=Product.objects.filter(is_active=True),
        required=False,
        help_text="Güncellenecek mevcut ürün (Yeni Ürün Oluştur işaretli değilse)"
    )