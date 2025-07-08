# backend/productconfig/models/product_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel
from .category import Category

class ProductModel(BaseModel):
    """
    Ürün Modeli, belirli bir kategori altında bulunan ve belirli özelliklere sahip ürünleri temsil eder.
    """
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Ürün Modeli Adı")
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="product_models", 
        verbose_name=_("Kategori"), 
        blank=True, 
        null=True
    )
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name=_("Taban Fiyat")
    )
    is_configurable = models.BooleanField(
        default=True,
        verbose_name=_("Yapılandırılabilir mi?"),
        help_text=_("Ürün modelinin konfigüre edilebilir olup olmadığı")
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Fiyat"),
        help_text=_("Ürünün alabileceği minimum fiyat")
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maksimum Fiyat"),
        help_text=_("Ürünün alabileceği maksimum fiyat")
    )

    class Meta:
        verbose_name = "04-Ürün Modeli"
        verbose_name_plural = "04-Ürün Modelleri"
        ordering = ['category', 'name']
        unique_together = ['category', 'name']  # Aynı kategori altında aynı isimde model olamaz


    def __str__(self):
        return f"{self.category.name} - {self.name}" if self.category else f"{self.name}"


    