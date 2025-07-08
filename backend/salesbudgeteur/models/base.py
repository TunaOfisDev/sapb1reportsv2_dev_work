# backend/salesbudgeteur/models/base.py

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Kayıt oluşturulma ve güncellenme zaman bilgilerini otomatik tutar.
    """
    created_at = models.DateTimeField(verbose_name="Oluşturulma Zamanı", default=timezone.now, editable=False)
    updated_at = models.DateTimeField(verbose_name="Güncellenme Zamanı", auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """
    Ortak alanları tanımlayan soyut model sınıfı. Diğer modeller bu sınıftan türetilir.
    """
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        abstract = True
