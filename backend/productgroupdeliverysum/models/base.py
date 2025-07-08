# backend/productgroupdeliverysum/models/base.py
from django.db import models

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)  # Otomatik artan ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Bu modeli soyut yapıyoruz, doğrudan kullanılmayacak.
