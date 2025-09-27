# productconfigv2/models/spec_option.py

from django.db import models
from .base import BaseModel
from .specification_type import SpecificationType


class SpecOption(BaseModel):
    spec_type = models.ForeignKey(SpecificationType, on_delete=models.CASCADE, related_name="options", verbose_name="Bağlı Olduğu Özellik Tipi")
    name = models.CharField(max_length=100, verbose_name="Seçenek Adı")
    image = models.ImageField(upload_to="spec_options/", null=True, blank=True, verbose_name="Görsel")

    variant_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Varyant Kod Parçası")
    variant_description = models.CharField(max_length=100, null=True, blank=True, verbose_name="Varyant Açıklama Parçası")

    reference_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Referans Fiyat Kodu (55'li Kod Parçası)"
    )

    price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Fiyat Etkisi")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan mı?")
    display_order = models.PositiveIntegerField(default=1, verbose_name="Görsel Sıra")

    class Meta:
        verbose_name = "05- Özellik Seçeneği"
        verbose_name_plural = "05- Özellik Seçenekleri"
        ordering = ["display_order"]

    def __str__(self):
        return self.name
