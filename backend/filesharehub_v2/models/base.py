# backend/filesharehub_v2/models/base.py
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    Otomatik olarak oluşturulma ve güncellenme zamanlarını tutar.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class NamedModel(models.Model):
    """
    İsim alanı taşıyan soyut model.
    """
    name = models.CharField(max_length=255, db_index=True)

    class Meta:
        abstract = True
