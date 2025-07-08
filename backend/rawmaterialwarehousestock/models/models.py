# backend/rawmaterialwarehousestock/models/models.py
from django.db import models
from .base import TimeStampedModel

class RawMaterialWarehouseStock(TimeStampedModel):
    depo_kodu = models.CharField(max_length=50, db_index=True, verbose_name="Depo Kodu")
    kalem_grup_ad = models.CharField(max_length=255, verbose_name="Kalem Grup Adı")
    stok_kalem = models.BooleanField(default=False, verbose_name="Stok Kalem")
    satis_kalem = models.BooleanField(default=False, verbose_name="Satış Kalem")
    satinalma_kalem = models.BooleanField(default=False, verbose_name="Satınalma Kalem")
    yapay_kalem = models.BooleanField(default=False, verbose_name="Yapay Kalem")
    kalem_kod = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Kalem Kod")
    kalem_tanim = models.CharField(max_length=255, verbose_name="Kalem Tanım")
    stok_olcu_birim = models.CharField(max_length=50, verbose_name="Stok Ölçü Birim")
    depo_stok = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Depo Stok")
    siparis_edilen_miktar = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Sipariş Edilen Miktar")
    son_satinalma_fiyat = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Son Satınalma Fiyat")
    son_satinalma_fatura_tarih = models.DateField(default="1900-01-01", verbose_name="Son Satınalma Fatura Tarihi")
    verilen_siparisler = models.TextField(default='Yok', verbose_name="Verilen Siparişler")
    secili = models.BooleanField(default=False, verbose_name="Seçili")
    hide_zero_stock = models.BooleanField(default=False, verbose_name="Sıfır Stoklu Satırları Gizle")

    class Meta:
        verbose_name = "Hammadde Depo Stok Durumu"
        verbose_name_plural = "Hammadde Depo Stok Durumları"
        ordering = ['kalem_kod']  # Kalem koduna göre sıralama

    def __str__(self):
        return f"{self.kalem_kod} - {self.kalem_tanim}"
