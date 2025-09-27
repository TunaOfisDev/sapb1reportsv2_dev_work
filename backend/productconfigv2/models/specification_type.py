# productconfigv2/models/specification_type.py

from django.db import models
from .base import BaseModel


class SpecificationType(BaseModel):
    name = models.CharField(max_length=100, verbose_name="Özellik Tipi Adı")
    group = models.CharField(max_length=100, blank=True, null=True, verbose_name="Özellik Grubu")

    is_required = models.BooleanField(default=True, verbose_name="Zorunlu mu?")
    allow_multiple = models.BooleanField(default=False, verbose_name="Çoklu Seçim İzinli mi?")

    variant_order = models.PositiveIntegerField(default=1, verbose_name="Varyant Sırası")
    display_order = models.PositiveIntegerField(default=1, verbose_name="Görsel Sıra")
    multiplier = models.DecimalField(max_digits=6, decimal_places=2, default=1.00, verbose_name="Fiyat Çarpanı")

    class Meta:
        verbose_name = "04- Özellik Tipi"
        verbose_name_plural = "04- Özellik Tipleri"
        ordering = ["display_order"]

    def __str__(self):
        return self.name

