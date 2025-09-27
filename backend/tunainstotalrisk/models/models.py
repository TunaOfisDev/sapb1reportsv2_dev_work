# File: backend/tunainstotalrisk/models/models.py

from django.db import models
from .base import BaseModel

class TunainsTotalRiskReport(BaseModel):
    """Tunain's özel toplam risk raporu.

    Bu model, `totalrisk` uygulamasından tamamen izole bir tabloya (``tunainstotalrisk_report``)
    yazılır. Böylece aynı veritabanında veri çakışması yaşamaz. Ayrıca `source` alanı sayesinde
    kayıtların nereden geldiği de netleşir.
    """

    # --- Ana alanlar -------------------------------------------------------
    satici = models.CharField(max_length=255, verbose_name="Satıcı", null=True, blank=True)
    grup = models.CharField(max_length=50, verbose_name="Grup")
    muhatap_kod = models.CharField(max_length=50, verbose_name="Muhatap Kod")
    avans_kod = models.CharField(max_length=50, blank=True, null=True, verbose_name="Avans Kod")
    muhatap_ad = models.CharField(max_length=255, verbose_name="Muhatap Adı")

    bakiye = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Bakiye")
    acik_teslimat = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Açık Teslimat")
    acik_siparis = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Açık Sipariş")
    avans_bakiye = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Avans Bakiye", null=True, blank=True)
    toplam_risk = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Toplam Risk")

    # --- İzolasyon ve debug için ekstra alan --------------------------------
    source = models.CharField(
        max_length=32,
        editable=False,
        default="tunains",
        help_text="Kaydın hangi micro‑servisten geldiğini belirtir"
    )

    class Meta:
        verbose_name = "Tunains Toplam Risk Raporu"
        verbose_name_plural = "Tunains Toplam Risk Raporları"
        db_table = "tunainstotalrisk_report"          # Benzersiz tablo adı
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(fields=["muhatap_kod"], name="uniq_tunains_muhatap"),
        ]

    def __str__(self):
        return f"{self.muhatap_kod} – {self.toplam_risk}"
