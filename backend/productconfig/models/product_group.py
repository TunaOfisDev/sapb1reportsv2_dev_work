# backend/productconfig/models/product_group.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel
from .brand import Brand

class ProductGroup(BaseModel):
    """
    Ürün Grubu modeli, belirli bir marka altında gruplandırılmış ürün kategorilerini temsil eder.
    """
    name = models.CharField(
        max_length=255, 
        verbose_name=_("Ürün Grubu Adı")
    )
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE, 
        related_name="product_groups", 
        verbose_name=_("Marka")
    )

    class Meta:
        verbose_name = "02-Ürün Grubu"
        verbose_name_plural = "02-Ürün Grupları"
        ordering = ['brand', 'name']
        unique_together = ['brand', 'name']  # Aynı marka altında aynı isimde grup olamaz


    def __str__(self):
        return f"{self.brand.name} - {self.name}"