# backend/systemnotebook/models/base.py

from django.db import models
from django.conf import settings

class BaseModel(models.Model):
    """
    Tüm modellerin miras alabileceği, oluşturulma tarihi ve kullanıcı bilgisini tutan soyut model.
    """
    created_at = models.DateTimeField(null=True, blank=True)  # auto_now_add kaldırıldı
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
