# backend/salesbudgeteur/models/salesbudget_model.py

from django.db import models
from .base import BaseModel


class SalesBudgetEURModel(BaseModel):
    """
    Satıcı bazında EUR cinsinden satış, hedef, iptal, elle kapanan tutarlar ve JSON sipariş listesi içerir.
    """
    satici = models.CharField(max_length=150, db_index=True, verbose_name="Satıcı")
    yil = models.PositiveSmallIntegerField(verbose_name="Yıl")

    # Yıllık toplamlar
    toplam_gercek_eur = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    toplam_hedef_eur = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    toplam_iptal_eur = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    toplam_elle_kapanan_eur = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    kapali_sip_list = models.TextField(blank=True, null=True, verbose_name="Kapalı/İptal Siparişler JSON")

    class Meta:
        verbose_name = "Satış Bütçesi (EUR)"
        verbose_name_plural = "Satış Bütçeleri (EUR)"
        unique_together = ("satici", "yil")

    def __str__(self):
        return f"{self.satici} ({self.yil})"


class MonthlySalesBudgetEUR(BaseModel):
    """
    Aylık bazda satış ve hedef tutarlarını temsil eder.
    """
    parent = models.ForeignKey(
        SalesBudgetEURModel,
        on_delete=models.CASCADE,
        related_name="aylik_veriler"
    )

    ay = models.PositiveSmallIntegerField(verbose_name="Ay (1-12)")
    gercek_tutar = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    hedef_tutar = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Aylık Satış Verisi (EUR)"
        verbose_name_plural = "Aylık Satış Verileri (EUR)"
        unique_together = ("parent", "ay")

    def __str__(self):
        return f"{self.parent.satici} {self.ay}.Ay"
