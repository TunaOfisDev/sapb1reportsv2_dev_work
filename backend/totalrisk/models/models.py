# backend/totalrisk/models/models.py
from django.db import models
from .base import BaseModel

class TotalRiskReport(BaseModel):
    satici = models.CharField(max_length=255, verbose_name="Satıcı", null=True, blank=True)
    grup = models.CharField(max_length=50, verbose_name="Grup")
    muhatap_kod = models.CharField(max_length=50, unique=True, verbose_name="Muhatap Kod")
    avans_kod = models.CharField(max_length=50, blank=True, null=True, verbose_name="Avans Kod")
    muhatap_ad = models.CharField(max_length=255, verbose_name="Muhatap Adı")
    bakiye = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Bakiye")
    acik_teslimat = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Açık Teslimat")
    acik_siparis = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Açık Sipariş")
    avans_bakiye = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Avans Bakiye", null=True, blank=True)
    toplam_risk = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Toplam Risk")

    def save(self, *args, **kwargs):
        super(TotalRiskReport, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Toplam Risk Raporu"
        verbose_name_plural = "Toplam Risk Raporları"

