# path: backend/nexuscore/models/data_app.py

from django.db import models
from django.conf import settings
from .dynamic_connection import DynamicDBConnection
from .virtual_table import VirtualTable, SharingStatus

class DataApp(models.Model):
    """
    Çoklu VirtualTable nesnelerini bir araya getiren, Qlik-Sense benzeri 
    bir 'Uygulama' veya 'Veri Modeli' konteyneridir. 
    Analizler bu bütünleşik model üzerinden yapılır.
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Uygulama Başlığı"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Açıklama"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_apps',
        verbose_name="Sahip"
    )
    
    # KRİTİK KISITLAMA: Bir uygulama tek bir veri kaynağına aittir.
    # Bu, tüm tabloların aynı veritabanında olduğunu ve SQL JOIN'lerinin 
    # yapılabileceğini garanti eder.
    connection = models.ForeignKey(
        DynamicDBConnection,
        on_delete=models.CASCADE, # Kaynak silinirse, uygulama da silinir.
        related_name='data_apps',
        verbose_name="Veri Kaynağı"
    )

    # Bu uygulama hangi sanal tabloları (veri kümelerini) içeriyor?
    virtual_tables = models.ManyToManyField(
        VirtualTable,
        related_name="data_apps",
        verbose_name="İçerilen Sanal Tablolar",
        help_text="Bu uygulamada kullanılacak veri kümeleri."
    )
    
    sharing_status = models.CharField(
        max_length=20,
        choices=SharingStatus.choices,
        default=SharingStatus.PRIVATE,
        verbose_name="Paylaşım Durumu"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Kaydetmeden önce, eklenecek tüm virtual_table'ların
        # bu app'in ana bağlantısıyla eşleştiğini doğrulamak GEREKİR.
        # Bu mantık Serializer veya save() metodunda uygulanmalıdır.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Veri Uygulaması"
        verbose_name_plural = "Veri Uygulamaları"
        unique_together = ('owner', 'title')
        ordering = ['-updated_at']