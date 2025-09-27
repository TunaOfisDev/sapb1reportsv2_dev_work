# productconfigv2/models/specification_option.py

from django.db import models
from .base import BaseModel
from .product import Product
from .specification_type import SpecificationType
from .spec_option import SpecOption


class SpecificationOption(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specification_options", verbose_name="Ürün")
    spec_type = models.ForeignKey(SpecificationType, on_delete=models.CASCADE, related_name="specification_options", verbose_name="Özellik Tipi")
    option = models.ForeignKey(SpecOption, on_delete=models.CASCADE, related_name="specification_options", verbose_name="Seçenek")

    is_default = models.BooleanField(default=False, verbose_name="Varsayılan Seçenek mi?")
    display_order = models.PositiveIntegerField(default=1, verbose_name="Görsel Sıra")

    class Meta:
        verbose_name = "07- Ürün Özellik Seçeneği"
        verbose_name_plural = "07- Ürün Özellik Seçenekleri"
        unique_together = ("product", "spec_type", "option")
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.product.code} - {self.spec_type.name}: {self.option.name}"
