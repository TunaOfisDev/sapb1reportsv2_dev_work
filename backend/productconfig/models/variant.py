# backend/productconfig/models/variant.py 
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel
from .option import Option
from .product_model import ProductModel
from .brand import Brand
from .category import Category
from .question import Question
from .product_group import ProductGroup

class Variant(BaseModel):
    """
    Varyant modeli, ürün yapılandırması sırasında oluşturulan varyant kodlarını,
    tanımlarını ve toplam fiyatı temsil eder. Kullanıcının seçtiği seçeneklere göre
    dinamik olarak oluşur.
    """
    class VariantStatus(models.TextChoices):
        DRAFT = 'draft', _('Taslak')
        IN_PROGRESS = 'in_progress', _('Devam Ediyor')
        COMPLETED = 'completed', _('Tamamlandı')
        ARCHIVED = 'archived', _('Arşivlendi')

    project_name = models.TextField(verbose_name=_("Proje Adı"), blank=True)
    variant_code = models.CharField(max_length=255, verbose_name=_("Varyant Kodu"), default="")
    variant_description = models.TextField(verbose_name=_("Varyant Tanımı"), blank=True, default="")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Toplam Fiyat (EUR)"))
    options = models.ManyToManyField(Option, related_name="variants", blank=True, verbose_name=_("Seçenekler"))
    answered_questions = models.ManyToManyField(Question, related_name="answered_variants", blank=True, verbose_name=_("Yanıtlanan Sorular"))
    text_answers = models.JSONField(default=dict, blank=True, verbose_name=_("Metin Cevaplar"))
    status = models.CharField(max_length=20, choices=VariantStatus.choices, default=VariantStatus.DRAFT, verbose_name=_("Durum"))
    product_model = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='variants', verbose_name=_("Ürün Modeli"))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='variants', verbose_name=_("Marka"))
    product_group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='variants', verbose_name=_("Ürün Grubu"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='variants', verbose_name=_("Kategori"))
    applicable_brands = models.ManyToManyField(Brand, blank=True, related_name="applicable_variants", verbose_name=_("Uygulanabilir Markalar"))
    applicable_categories = models.ManyToManyField(Category, blank=True, related_name="applicable_variants", verbose_name=_("Uygulanabilir Kategoriler"))
    notes = models.TextField(blank=True, verbose_name=_("Notlar"))
    old_component_codes = models.JSONField(default=list, blank=True, verbose_name="Eski Bileşen Kodları")
    last_modified_date = models.DateTimeField(auto_now=True, verbose_name=_("Son Değişiklik Tarihi"))

    # Yeni SAP HANA Alanları
    sap_item_code = models.CharField(max_length=255, blank=True, verbose_name=_("SAP Item Code"))
    sap_item_description = models.TextField(blank=True, verbose_name=_("SAP Item Description"))
    sap_U_eski_bilesen_kod = models.CharField(max_length=255, blank=True, verbose_name=_("SAP Eski Bileşen Kodu"))
    sap_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("SAP Price"))
    sap_currency = models.CharField(max_length=10, blank=True, verbose_name=_("SAP Currency"))


    class Meta:
        verbose_name = "11-Varyant"
        verbose_name_plural = "11-Varyantlar"
        ordering = ['variant_code']

        
    def __str__(self):
        return f"{self.variant_code} - {self.variant_description[:30]}..."