# backend/salesorder/models/customersalesorder.py
from django.db import models
from .base import BaseModel

class CustomerSalesOrder(BaseModel):
    grup = models.CharField(max_length=25, verbose_name="Grup")
    musteri_kod = models.CharField(max_length=255, unique=True, verbose_name="Müşteri Kodu")
    musteri_ad = models.CharField(max_length=255, verbose_name="Müşteri Adı")
    yil = models.IntegerField(verbose_name="Yıl", null=True, blank=True)
    ocak = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Ocak")
    subat = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Şubat")
    mart = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Mart")
    nisan = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Nisan")
    mayis = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Mayıs")
    haziran = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Haziran")
    temmuz = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Temmuz")
    agustos = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Ağustos")
    eylul = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Eylül")
    ekim = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Ekim")
    kasim = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Kasım")
    aralik = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Aralık")
    yillik_toplam = models.DecimalField(max_digits=16, decimal_places=2, default=0, verbose_name="Yıllık Toplam")

    def save(self, *args, **kwargs):
            if self.grup:  # grup alanı boş değilse
                self.grup = self.grup.upper()  # grup değerini büyük harfe çevir
            super(CustomerSalesOrder, self).save(*args, **kwargs)  # Ana save fonksiyonunu çağır

    class Meta:
        verbose_name = "Müşteri Satış Siparişi"
        verbose_name_plural = "Müşteri Satış Siparişleri"

    def __str__(self):
        return f"{self.musteri_kod} - {self.musteri_ad} - {self.yil if self.yil else 'Yıl Bilgisi Yok'}"

