# backend/supplierpayment/models/closinginvoice.py
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from .base import BaseModel
from django.db.models import JSONField
from .models import SupplierPayment

class ClosingInvoice(BaseModel):
    cari_kod = models.CharField(max_length=100, unique=True, db_index=True)
    cari_ad = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    iban = models.TextField( blank=True, null=True)
    odemekosulu = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    monthly_balances = JSONField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['monthly_balances'], name='monthly_balances_gin'),
            models.Index(fields=['current_balance', 'cari_kod'], name='curr_bal_cari_kod_idx')
        ]

    def __str__(self):
        return f"{self.cari_kod} - {self.cari_ad}"

    def save(self, *args, **kwargs):
        supplier_payment = SupplierPayment.objects.filter(cari_kod=self.cari_kod).first()
        if supplier_payment:
            self.cari_ad = supplier_payment.cari_ad
            self.iban = supplier_payment.iban
            self.odemekosulu = supplier_payment.odemekosulu

        super(ClosingInvoice, self).save(*args, **kwargs)