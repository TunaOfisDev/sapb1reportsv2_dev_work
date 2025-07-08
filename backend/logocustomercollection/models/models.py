# backend/logocustomercollection/models/models.py

from django.db import models
from decimal import Decimal
from .base import LogoDbMixin  # Yeni sade base sınıf

class LogoCustomerCollectionTransaction(LogoDbMixin):
    """
    Logo ERP'den ay ve yıl bazında gelen müşteri işlem verisinin ham hali.
    Her kayıt bir cari kod, ay ve yıl için borç/alacak toplamını içerir.
    """

    cari_kod = models.CharField(max_length=64, verbose_name="Cari Kod")
    cari_ad = models.CharField(max_length=255, verbose_name="Cari Ad")
    ay = models.PositiveSmallIntegerField(verbose_name="Ay")  # 1-12
    yil = models.PositiveIntegerField(verbose_name="Yıl")
    borc = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), verbose_name="Borç")
    alacak = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), verbose_name="Alacak")

    class Meta:
        verbose_name = "Logo Müşteri Ham İşlem"
        verbose_name_plural = "Logo Müşteri Ham İşlemler"
        unique_together = ("cari_kod", "ay", "yil")
        indexes = [
            models.Index(fields=["cari_kod", "yil", "ay"], name="lcc_cari_kod_yil_ay_idx"),
        ]
        db_table = "logocustomercollection_transaction_view"  # VIEW adın buysa bu şekilde kalır

    def __str__(self):
        return f"{self.cari_kod} - {self.ay:02d}/{self.yil}"

    @property
    def bakiye(self):
        return self.borc - self.alacak
