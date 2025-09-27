# backend/deliverydocsum/models/models.py
from django.db import models
from .base import BaseModel

class DeliveryDocSummary(BaseModel):
    cari_kod = models.CharField(max_length=20, unique=True)
    cari_adi = models.CharField(max_length=255, blank=True, null=True)
    temsilci = models.CharField(max_length=255, blank=True, null=True)
    cari_grup = models.CharField(max_length=255, blank=True, null=True)
    
    gunluk_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    dun_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    onceki_gun_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    aylik_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    yillik_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    acik_sevkiyat_toplami = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    acik_siparis_toplami = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    irsaliye_sayisi = models.IntegerField(default=0)
    gunluk_ilgili_siparis_numaralari = models.CharField(max_length=500, default='0')
    dun_ilgili_siparis_numaralari = models.CharField(max_length=500, default='0')
    onceki_gun_ilgili_siparis_numaralari = models.CharField(max_length=500, default='0')

    class Meta:
        verbose_name = "Delivery Document Summary"
        verbose_name_plural = "Delivery Document Summaries"

    def __str__(self):
        return f"{self.cari_kod} - {self.cari_adi}"
