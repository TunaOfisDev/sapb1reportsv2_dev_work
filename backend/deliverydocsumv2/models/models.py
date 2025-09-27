# backend/deliverydocsum/models/models.py
from django.db import models
from .base import BaseModel

class DeliveryDocSummary(BaseModel):
    cari_kod = models.CharField(max_length=20, unique=True)
    cari_adi = models.CharField(max_length=255, blank=True, null=True)
    temsilci = models.CharField(max_length=255, blank=True, null=True)
    cari_grup = models.CharField(max_length=255, blank=True, null=True)
    
    # hucre detayina tikladiginda showmodal acilacak alanlar
    bugun = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bugun_minus_1 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bugun_minus_2 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bugun_minus_3 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bugun_minus_4 = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bu_ay_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bu_ay_minus_1_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    acik_sevkiyat_toplami = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # show modal ile gosterilecek indexler   
    bugun_ilgili_siparis_numaralari = models.TextField(default='0')
    bugun_minus_1_ilgili_siparis_numaralari = models.TextField(default='0')
    bugun_minus_2_ilgili_siparis_numaralari = models.TextField(default='0')
    bugun_minus_3_ilgili_siparis_numaralari = models.TextField(default='0')
    bugun_minus_4_ilgili_siparis_numaralari = models.TextField(default='0')
    bu_ay_ilgili_siparis_numaralari = models.TextField(default='0')
    bu_ay_minus_1_ilgili_siparis_numaralari = models.TextField(default='0')
    acik_irsaliye_belge_no_tarih_tutar = models.TextField(default='0')
    

    yillik_toplam = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    acik_siparis_toplami = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    irsaliye_sayisi = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Delivery Document Summary"
        verbose_name_plural = "Delivery Document Summaries"

    def __str__(self):
        return f"{self.cari_kod} - {self.cari_adi}"

