# backend/hanaservicelayer/models/base.py

from django.db import models
from django.utils.timezone import now

class BaseModel(models.Model):
    """
    Tüm modellerin temel yapısı.
    - Tüm modeller için ortak alanlar içerir.
    - Otomatik artan ID kullanılır.
    """
    id = models.AutoField(primary_key=True)  # UUID yerine klasik ID kullanıldı
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Bu model sadece miras alınmak için kullanılacak
