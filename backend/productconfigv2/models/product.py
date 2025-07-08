# productconfigv2/models/product.py

from django.db import models
from .base import BaseModel
from .product_family import ProductFamily


class Product(BaseModel):
    family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE, related_name="products", verbose_name="Ürün Ailesi")
    code = models.CharField(max_length=30, unique=True, verbose_name="Ürün Kodu")
    name = models.CharField(max_length=100, verbose_name="Ürün Adı")
    image = models.ImageField(upload_to="products/", null=True, blank=True, verbose_name="Ürün Görseli")

    variant_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Varyant Kod Şablonu")
    variant_description = models.CharField(max_length=200, null=True, blank=True, verbose_name="Varyant Açıklama Şablonu")

    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Temel Fiyat")
    currency = models.CharField(max_length=10, default="EUR", verbose_name="Para Birimi")
    variant_order = models.PositiveIntegerField(default=1, verbose_name="Varyant Sırası")

    class Meta:
        verbose_name = "03- Ürün"
        verbose_name_plural = "03- Ürünler"

    def __str__(self):
        return f"{self.code} - {self.name}"
