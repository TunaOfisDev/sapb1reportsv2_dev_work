# backend/rawmaterialwarehousestock/models/base.py
from django.db import models

class TimeStampedModel(models.Model):
    """
    Otomatik olarak oluşturulma ve güncellenme tarihlerini 
    sağlayan soyut temel model sınıfı.
    """
    created = models.DateTimeField(auto_now_add=True)  # Oluşturulma tarihi
    modified = models.DateTimeField(auto_now=True)  # Güncellenme tarihi

    class Meta:
        abstract = True  # Bu modelin veritabanında tablo olarak oluşturulmamasını sağlar

class NamedModel(models.Model):
    """
    'name' alanını sağlayan soyut temel model sınıfı.
    """
    name = models.CharField(max_length=255, unique=True)  # Benzersiz ad alanı

    class Meta:
        abstract = True  # Bu modelin veritabanında tablo olarak oluşturulmamasını sağlar

class DescriptionModel(models.Model):
    """
    'description' alanını sağlayan soyut temel model sınıfı.
    """
    description = models.TextField(blank=True, null=True)  # Açıklama alanı

    class Meta:
        abstract = True  # Bu modelin veritabanında tablo olarak oluşturulmamasını sağlar
