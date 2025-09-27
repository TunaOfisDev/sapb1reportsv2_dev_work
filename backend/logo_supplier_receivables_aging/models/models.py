# backend/logo_supplier_receivables_aging/models/models.py

from django.db import models
from decimal import Decimal
from .base import TimeStampedModel, DecimalFieldMixin


class SupplierRawTransaction(TimeStampedModel, DecimalFieldMixin):
    """
    Logo ERP'den ay ve yıl bazında gelen tedarikçi işlem verisinin ham hali.
    Her kayıt bir cari kod, ay ve yıl için borç/alacak toplamını içerir.
    """

    cari_kod = models.CharField(max_length=64, verbose_name="Cari Kod")
    cari_ad = models.CharField(max_length=255, verbose_name="Cari Ad")
    ay = models.PositiveSmallIntegerField(verbose_name="Ay")  # 1-12
    yil = models.PositiveIntegerField(verbose_name="Yıl")
    borc = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), verbose_name="Borç")
    alacak = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), verbose_name="Alacak")

    class Meta:
        verbose_name = "Tedarikçi Ham İşlem"
        verbose_name_plural = "Tedarikçi Ham İşlemler"
        unique_together = ("cari_kod", "ay", "yil")
        indexes = [
            models.Index(fields=["cari_kod", "yil", "ay"]),
        ]

    def __str__(self):
        return f"{self.cari_kod} - {self.ay:02d}/{self.yil}"
from django.db import models

# Create your models here.
