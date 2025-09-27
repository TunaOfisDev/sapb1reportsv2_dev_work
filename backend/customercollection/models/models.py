# backend/customercollection/models/models.py
from django.db import models
from .base import BaseModel

class CustomerCollection(BaseModel):
    cari_kod = models.CharField(max_length=100)
    cari_ad = models.CharField(max_length=255)
    satici = models.CharField(max_length=255, null=True, blank=True)
    grup = models.CharField(max_length=50)
    belge_tarih = models.CharField(max_length=10, blank=True, null=True)
    vade_tarih = models.CharField(max_length=10, blank=True, null=True)
    belge_no = models.IntegerField()
    odemekod = models.IntegerField()
    odemekosulu = models.CharField(max_length=255)
    borc = models.DecimalField(max_digits=19, decimal_places=2)
    alacak = models.DecimalField(max_digits=19, decimal_places=2)
    
    class Meta:
        ordering = ['belge_tarih']
        
    def __str__(self):
        return f"{self.cari_kod} - {self.cari_ad}"
