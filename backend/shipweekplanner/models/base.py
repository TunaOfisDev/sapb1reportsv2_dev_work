# backend/shipweekplanner/models/base.py
from django.db import models

class BaseModel(models.Model):
    """
    Tüm modeller için ortak alanların ve davranışların yer aldığı temel model.
    Artık UUID yerine sıralı tam sayı ID kullanıyor.
    """
    id = models.AutoField(primary_key=True)  # Otomatik artan tamsayı ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # Bu model, doğrudan veritabanında bir tablo oluşturmaz. Diğer modeller tarafından miras alınır.

class TimestampedModel(BaseModel):
    """
    Tüm modeller için oluşturulma ve güncellenme zamanlarını tutan model.
    Bu model, BaseModel'i miras alır ve her modelde tekrar eden created_at ve updated_at alanlarını içerir.
    """
    class Meta:
        abstract = True