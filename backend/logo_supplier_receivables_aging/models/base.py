# backend/logo_supplier_receivables_aging/models/base.py
from django.db import models
from decimal import Decimal

class TimeStampedModel(models.Model):
    """
    Soyut zaman damgası modeli. Diğer modellere miras verilerek
    oluşturulma ve güncellenme tarihleri otomatik tutulur.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        abstract = True


class DecimalFieldMixin:
    """
    Decimal uyumlu alan hesaplamaları için yardımcı metotlar.
    """
    @staticmethod
    def format_decimal(value):
        if value is None:
            return Decimal("0.00")
        if not isinstance(value, Decimal):
            return Decimal(str(value))
        return value
