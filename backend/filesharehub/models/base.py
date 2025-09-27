# backend/filesharehub/models/base.py
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """
    Her model için ortak alanlar içerir.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Bu model miras alınacak, doğrudan bir tablo olarak kullanılmayacak.
