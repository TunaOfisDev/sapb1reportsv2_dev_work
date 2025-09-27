# backend/logocustomercollection/models/closinginvoice.py

from django.db import models
from django.contrib.postgres.indexes import GinIndex
from decimal import Decimal
from collections import OrderedDict

from .base import TimeStampedModel, DecimalFieldMixin, LogoDbMixin
from .models import LogoCustomerCollectionTransaction


class LogoCustomerCollectionAgingSummary(TimeStampedModel, DecimalFieldMixin, LogoDbMixin):
    """
    Her müşteri için 'öncesi' ve son 4 aya ait kalan borçların özetini tutar.
    Tüm dönemsel kalanlar JSON formatında liste olarak tutulur:
    [["Öncesi", 0.0], ["Nis25", 0.0], ...]
    """

    cari_kod = models.CharField(max_length=64, verbose_name="Cari Kod", unique=True, db_index=True)
    cari_ad = models.CharField(max_length=255, verbose_name="Cari Ad", db_index=True)
    guncel_bakiye = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
        verbose_name="Güncel Bakiye", db_index=True
    )
    aylik_kalan_borc = models.JSONField(null=True, verbose_name="Aylık Kalan Borçlar")

    class Meta:
        verbose_name = "Müşteri Özet Yaşlandırma"
        verbose_name_plural = "Müşteri Özet Yaşlandırmalar"
        indexes = [
            GinIndex(fields=["aylik_kalan_borc"], name="lcc_aylik_kalan_borc_gin"),
            models.Index(fields=["guncel_bakiye", "cari_kod"], name="lcc_guncel_bakiye_cari_kod_idx"),
        ]

    def __str__(self):
        return f"{self.cari_kod} | Güncel Bakiye: {self.guncel_bakiye:,.2f}"

    def save(self, *args, **kwargs):
        """
        Kaydetmeden önce cari_ad bilgisini LogoCustomerCollectionTransaction üzerinden eşle.
        """
        raw = LogoCustomerCollectionTransaction.objects.filter(cari_kod=self.cari_kod).first()
        if raw:
            self.cari_ad = raw.cari_ad
        if self.aylik_kalan_borc is None:
            self.aylik_kalan_borc = []
        super().save(*args, **kwargs)

    @property
    def sorted_aylik_kalan_borc(self):
        """
        Aylık kalan borçları sıralı OrderedDict olarak döndür.
        """
        if not self.aylik_kalan_borc:
            return OrderedDict()
        return OrderedDict(self.aylik_kalan_borc)
