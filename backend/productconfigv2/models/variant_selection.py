# productconfigv2/models/variant_selection.py

from django.db import models
from .base import BaseModel
from .variant import Variant
from .specification_type import SpecificationType
from .spec_option import SpecOption


class VariantSelection(BaseModel):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="selections", verbose_name="Varyant")
    spec_type = models.ForeignKey(SpecificationType, on_delete=models.CASCADE, verbose_name="Özellik Tipi")
    option = models.ForeignKey(SpecOption, on_delete=models.CASCADE, verbose_name="Seçilen Seçenek")

    class Meta:
        verbose_name = "09- Varyant Seçimi"
        verbose_name_plural = "09- Varyant Seçimleri"
        unique_together = ("variant", "spec_type")


    def __str__(self):
        # Burada self.variant.code yerine self.variant.new_variant_code kullanılmalı.
        return f"{self.variant.new_variant_code} → {self.spec_type.name}: {self.option.name}"
