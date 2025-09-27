# productconfigv2/models/product_specification.py

from django.db import models
from .base import BaseModel
from .product import Product
from .specification_type import SpecificationType


class ProductSpecification(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_specifications", verbose_name="Ürün")
    spec_type = models.ForeignKey(SpecificationType, on_delete=models.CASCADE, related_name="product_specifications", verbose_name="Özellik Tipi")

    is_required = models.BooleanField(default=True, verbose_name="Zorunlu mu?")
    allow_multiple = models.BooleanField(default=False, verbose_name="Çoklu Seçim İzinli mi?")
    variant_order = models.PositiveIntegerField(default=1, verbose_name="Varyant Sırası (Ürün Bazlı)")
    display_order = models.PositiveIntegerField(default=1, verbose_name="Görsel Sıra (Ürün Bazlı)")

    class Meta:
        verbose_name = "06- Ürün Özellik İlişkisi"
        verbose_name_plural = "06- Ürün Özellik İlişkileri"
        unique_together = ("product", "spec_type")
        ordering = ["variant_order"]

    def __str__(self):
        return f"{self.product.code} - {self.spec_type.name}"
