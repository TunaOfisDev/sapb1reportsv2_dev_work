# backend/logocustomerbalance/models/models.py
from django.db import models
from .base import BaseModel

class CustomerBalance(BaseModel):
    cari_kodu = models.CharField(max_length=50, db_index=True)
    cari_aciklamasi = models.CharField(max_length=255)
    bakiye_borc = models.FloatField()
    bakiye_alacak = models.FloatField()

    def __str__(self):
        return f"{self.cari_kodu} - {self.cari_aciklamasi}"

    class Meta:
        indexes = [
            models.Index(fields=['cari_kodu']),
        ]
        db_table = 'customer_balance'
        verbose_name = 'Customer Balance'
        verbose_name_plural = 'Customer Balances'

