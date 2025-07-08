# backend/tunainssupplieradvancebalance/models/models.py
from django.db import models
from .base import BaseModel

class TunaInsSupplierAdvanceBalance(BaseModel):
    muhatap_kod = models.CharField(max_length=50, unique=True, verbose_name="Muhatap Kod")
    muhatap_ad = models.CharField(max_length=255, verbose_name="Muhatap Adı")
    avans_bakiye = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Avans Bakiye", null=True, blank=True)
  

    def save(self, *args, **kwargs):
        super(TunaInsSupplierAdvanceBalance, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Tedarikci Avans Raporu"
        verbose_name_plural = "Tedarikci Avans Raporlari"

