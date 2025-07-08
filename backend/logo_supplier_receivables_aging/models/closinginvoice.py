# backend/logo_supplier_receivables_aging/models/closinginvoice.py
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from decimal import Decimal
from .base import TimeStampedModel, DecimalFieldMixin
from collections import OrderedDict

class SupplierAgingSummary(TimeStampedModel, DecimalFieldMixin):
    """
    Her tedarikçi için 'öncesi' ve son 4 aya ait kalan alacakların özetini tutar.
    Tüm dönemsel kalanlar JSON formatında liste olarak tutulur: [["Öncesi", 0.0], ["Oca25", 0.0], ...]
    """

    cari_kod = models.CharField(max_length=64, verbose_name="Cari Kod", unique=True, db_index=True)
    cari_ad = models.CharField(max_length=255, verbose_name="Cari Ad", db_index=True)
    guncel_bakiye = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), verbose_name="Güncel Bakiye", db_index=True)
    aylik_kalan_alacak = models.JSONField(null=True, verbose_name="Aylık Kalan Alacaklar")

    class Meta:
        verbose_name = "Tedarikçi Özet Yaşlandırma"
        verbose_name_plural = "Tedarikçi Özet Yaşlandırmalar"
        indexes = [
            GinIndex(fields=['aylik_kalan_alacak'], name='aylik_kalan_alacak_gin'),
            models.Index(fields=['guncel_bakiye', 'cari_kod'], name='guncel_bakiye_cari_kod_idx')
        ]

    def __str__(self):
        return f"{self.cari_kod} | Güncel: {self.guncel_bakiye:,.2f}"

    def save(self, *args, **kwargs):
        """
        Kaydetmeden önce cari_ad'ı SupplierRawTransaction'dan güncelle.
        """
        from .models import SupplierRawTransaction
        raw_transaction = SupplierRawTransaction.objects.filter(cari_kod=self.cari_kod).first()
        if raw_transaction:
            self.cari_ad = raw_transaction.cari_ad
        # aylik_kalan_alacak null değilse ve boşsa, boş liste ata
        if self.aylik_kalan_alacak is None:
            self.aylik_kalan_alacak = []
        super().save(*args, **kwargs)

    @property
    def sorted_aylik_kalan_alacak(self):
        """
        Aylık kalan alacakları dict formatında sıralı döndür.
        """
        if not self.aylik_kalan_alacak:
            return OrderedDict()
        # Liste formatını dict'e çevir
        return OrderedDict(self.aylik_kalan_alacak)

    def save(self, *args, **kwargs):
        """
        Kaydetmeden önce cari_ad'ı SupplierRawTransaction'dan güncelle.
        """
        from .models import SupplierRawTransaction
        raw_transaction = SupplierRawTransaction.objects.filter(cari_kod=self.cari_kod).first()
        if raw_transaction:
            self.cari_ad = raw_transaction.cari_ad
        super().save(*args, **kwargs)