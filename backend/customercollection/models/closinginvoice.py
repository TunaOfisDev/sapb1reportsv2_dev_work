# bbackend/customercollection/models/closinginvoice.py
from django.db import models
from .base import BaseModel
from django.db.models import JSONField
from .models import CustomerCollection
from decimal import Decimal

class ClosingInvoice(models.Model):
    cari_kod = models.CharField(max_length=100, unique=True)
    cari_ad = models.CharField(max_length=255, blank=True, null=True)
    satici = models.CharField(max_length=255, null=True, blank=True)
    grup = models.CharField(max_length=50, blank=True, null=True)
    odemekosulu = models.CharField(max_length=255, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=19, decimal_places=2)
    monthly_balances = JSONField(null=True)

    def __str__(self):
        return f"{self.cari_kod} - {self.cari_ad}"

    def compute_monthly_balances(self):
        carry_over = Decimal(0)
        for month, balance in self.monthly_balances.items():
            month_balance = carry_over + Decimal(balance)  # Balance değerini Decimal'e dönüştürün
            carry_over = month_balance if month_balance > 0 else Decimal(0)
            self.monthly_balances[month] = float(month_balance if month_balance <= 0 else 0)
        self.save()

    def save(self, *args, **kwargs):
        customer_collection = CustomerCollection.objects.filter(cari_kod=self.cari_kod).first()
        if customer_collection:
            self.cari_ad = customer_collection.cari_ad
            self.satici = customer_collection.satici
            self.grup = customer_collection.grup  
            self.odemekosulu = customer_collection.odemekosulu

        super(ClosingInvoice, self).save(*args, **kwargs)
