# backend/logocustomercollection/models/base.py
#
# 1) TimeStampedModel        –  created_at / updated_at alanları (tüm özet tablolarda işe yarar)
# 2) DecimalFieldMixin       –  ondalıklı hesaplar için ortak yardımcı
# 3) LogoDbMixin (opsiyonel) –  managed=False + app_label tek noktada tanımla
#
#  NOT: Ekstra .objects manager tanımlamadık; DATABASE_ROUTERS
#        → “logocustomercollection” app’ini zaten ‘logodb’ alias’ına yönlendiriyor.

from django.db import models
from decimal import Decimal


class TimeStampedModel(models.Model):
    """
    Otomatik oluşturulma & güncellenme zaman damgası.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        abstract = True


class DecimalFieldMixin:
    """
    Decimal uyumlu sayısal işlemler için yardımcı metot.
    """
    @staticmethod
    def format_decimal(value):
        if value is None:
            return Decimal("0.00")
        if not isinstance(value, Decimal):
            return Decimal(str(value))
        return value


class LogoDbMixin(models.Model):
    """
    Bu uygulamadaki unmanaged tablolar / view-ler için ortak ayarlar.
    Router ‘logodb’ alias’ına yönlendirdiğinden ekstra manager gerekmez.
    """
    class Meta:
        abstract = True
        managed = False
        app_label = "logocustomercollection"
