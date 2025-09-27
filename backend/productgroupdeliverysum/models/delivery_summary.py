# backend/productgroupdeliverysum/models/delivery_summary.py
from django.db import models
from .base import BaseModel

class DeliverySummary(BaseModel):
    yil = models.CharField(max_length=4)  # Yıl (String olarak tutuluyor)
    yil_ay = models.CharField(max_length=7)  # Yıl-Ay formatında (YYYY-MM)
    
    teslimat_tutar = models.DecimalField(max_digits=20, decimal_places=2)  # Teslimat Tutarı
    teslimat_girsberger = models.DecimalField(max_digits=20, decimal_places=2)  # Girsberger Teslimat Tutarı
    teslimat_mamul = models.DecimalField(max_digits=20, decimal_places=2)  # Mamul Teslimat Tutarı
    teslimat_ticari = models.DecimalField(max_digits=20, decimal_places=2)  # Ticari Teslimat Tutarı
    teslimat_nakliye = models.DecimalField(max_digits=20, decimal_places=2)  # Nakliye Teslimat Tutarı
    teslimat_montaj = models.DecimalField(max_digits=20, decimal_places=2)  # Montaj Teslimat Tutarı

    class Meta:
        unique_together = ('yil', 'yil_ay')  # Aynı yıl-ay kombinasyonunu önlemek için
        verbose_name = 'Teslimat Özeti'
        verbose_name_plural = 'Teslimat Özetleri'
    
    def __str__(self):
        return f"{self.yil_ay} - {self.teslimat_tutar} TL"
