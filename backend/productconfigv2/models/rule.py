# productconfigv2/models/rule.py

from django.db import models
from .base import BaseModel
from .product_family import ProductFamily


class Rule(BaseModel):
    RULE_TYPE_CHOICES = (
        ('deny', 'Geçersiz Kıl'),
        ('allow', 'Geçerli Kıl'),
    )

    product_family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE, related_name="rules", verbose_name="Ürün Ailesi")
    rule_type = models.CharField(max_length=5, choices=RULE_TYPE_CHOICES, verbose_name="Kural Tipi")
    name = models.CharField(max_length=150, verbose_name="Kural Adı")
    

    conditions = models.JSONField(verbose_name="Koşullar")  # Örn: {"Engine": "500cc"}
    actions = models.JSONField(verbose_name="Aksiyonlar")   # Örn: {"disable": ["Carburetor=TP100"]}

    class Meta:
        verbose_name = "10- Kural"
        verbose_name_plural = "10- Kurallar"

    def __str__(self):
        return f"{self.rule_type.upper()} - {self.name}"
