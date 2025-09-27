# backend/activities/models/models.py
from django.db import models
from .base import BaseModel


class Activity(BaseModel):
    numara = models.IntegerField(primary_key=True)

    # HANA'daki ilk kayıt zamanı
    create_datetime = models.DateTimeField(null=True, blank=True)

    baslangic_tarihi = models.DateField(blank=True, null=True)
    bitis_tarihi     = models.DateField(blank=True, null=True)
    baslama_saati    = models.TimeField(blank=True, null=True)
    bitis_saati      = models.TimeField(blank=True, null=True)

    sure        = models.CharField(max_length=50,  blank=True, null=True)
    isleyen     = models.CharField(max_length=100)
    tayin_eden  = models.CharField(max_length=100)
    aktivite    = models.CharField(max_length=50,  blank=True, null=True)
    tur         = models.CharField(max_length=50,  blank=True, null=True)
    konu        = models.CharField(max_length=100, blank=True, null=True)
    muhatap_kod = models.CharField(max_length=20, blank=True, null=True)
    muhatap_ad  = models.CharField(max_length=100, blank=True, null=True)
    durum       = models.CharField(max_length=100, blank=True, null=True)
    aciklama    = models.TextField(blank=True, null=True)
    icerik      = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Aktivite"
        verbose_name_plural = "Aktiviteler"
        ordering = ["-create_datetime", "-numara"]



    