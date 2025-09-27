# backend/tunainssupplierpayment/models/models.py
from django.db import models
from .base import BaseModel

class SupplierPayment(BaseModel):
    cari_kod = models.CharField(max_length=100, db_index=True)
    cari_ad = models.CharField(max_length=200, db_index=True)
    belge_tarih = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    belge_no = models.IntegerField(db_index=True)
    iban = models.TextField(blank=True, null=True)
    odemekosulu = models.CharField(max_length=100)
    borc = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    alacak = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    is_buffer = models.BooleanField(default=False, db_index=True)  # Yeni alan: buffer verisi mi?
    
    class Meta:
        ordering = ['belge_tarih']
        indexes = [
            models.Index(fields=['cari_kod', 'belge_tarih']),
            models.Index(fields=['cari_kod', 'belge_no']),
            models.Index(fields=['borc', 'alacak']),
            models.Index(fields=['is_buffer', 'belge_tarih'])  # Yeni index
        ]
        
    def __str__(self):
        return f"{self.cari_kod} - {self.cari_ad}"
