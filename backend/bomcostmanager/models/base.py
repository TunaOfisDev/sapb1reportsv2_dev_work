# backend/bomcostmanager/models/base.py
from django.db import models

class BaseModel(models.Model):
    """
    Tüm modeller için ortak alanları (oluşturulma ve güncellenme tarihleri)
    içeren soyut temel model.
    """
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        abstract = True
