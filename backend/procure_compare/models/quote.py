# File: procure_compare/models/quote.py

from django.db import models


class PurchaseQuote(models.Model):
    doc_entry = models.IntegerField()
    doc_num = models.CharField(max_length=20)
    card_code = models.CharField(max_length=20)
    card_name = models.CharField(max_length=100)
    item_code = models.CharField(max_length=50)
    line_num = models.IntegerField()
    price = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=18, decimal_places=6, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase_quotes"
        verbose_name = "Purchase Quote"
        verbose_name_plural = "Purchase Quotes"
        unique_together = ('doc_num', 'item_code', 'line_num')

    def __str__(self):
        return f"{self.doc_num} - {self.item_code} ({self.card_name})"
