# productconfigv2/models/product_family.py

from django.db import models
from .base import BaseModel


class ProductFamily(BaseModel):
    name = models.CharField(max_length=100, verbose_name="Aile Adı")
    image = models.ImageField(upload_to="product_family/", null=True, blank=True, verbose_name="Görsel")

    class Meta:
        verbose_name = "02- Ürün Ailesi"
        verbose_name_plural = "02- Ürün Aileleri"

    def __str__(self):
        return self.name

