# File: procure_compare/models/order.py
from django.db import models

class PurchaseOrder(models.Model):
    doc_entry = models.IntegerField(unique=True)
    doc_num = models.CharField(max_length=20)
    card_code = models.CharField(max_length=20)
    card_name = models.CharField(max_length=100)
    doc_date = models.DateField()
    doc_due_date = models.DateField(null=True, blank=True)
    wdd_status = models.CharField(max_length=5)
    doc_status = models.CharField(max_length=10)
    comments = models.TextField(null=True, blank=True)
    address2 = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase_orders"
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"

    def __str__(self):
        return f"{self.doc_num} - {self.card_name}"
