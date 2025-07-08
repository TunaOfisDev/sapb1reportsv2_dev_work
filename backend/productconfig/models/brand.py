 # backend/productconfig/models/brand.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel

class Brand(BaseModel):
    """
    Marka modeli, ürün grupları ve kategorileri için üst seviye organizasyon sağlar.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("Marka Adı")
    )

    class Meta:
        verbose_name = "01-Marka"
        verbose_name_plural = "01-Markalar"
        ordering = ['name']


    def __str__(self):
        return self.name

    