# productconfigv2/models/variant.py

from django.db import models
from .base import BaseModel
from .product import Product


class Variant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants", verbose_name="Ürün")
    project_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="Proje Adı",
        db_index=True # Bu alanda sık arama yapılacağı için index ekliyoruz.
    )
    reference_code = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Referans Kodu (55'li)",
        db_index=True # Bu alanda arama ve filtreleme yapacaksanız performansı artırır.
    )
    new_variant_code = models.CharField(max_length=100, unique=True, verbose_name="Yeni Varyant Kodu")
    new_variant_description = models.CharField(max_length=500, verbose_name="Yeni Varyant Adı")
    image = models.ImageField(upload_to="variant_images/", null=True, blank=True, verbose_name="Görsel")

    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Fiyat")
    currency = models.CharField(max_length=10, default="EUR", verbose_name="Para Birimi")

    is_generated = models.BooleanField(default=True, verbose_name="Otomatik Oluşturuldu mu?")

    class Meta:
        verbose_name = "08- Varyant"
        verbose_name_plural = "08- Varyantlar"
        ordering = ["-created_at"]

    
    def save(self, *args, **kwargs):
        """
        Force the currency to be 'EUR' every time this variant is saved.
        """
        self.currency = "EUR"
        super().save(*args, **kwargs)
