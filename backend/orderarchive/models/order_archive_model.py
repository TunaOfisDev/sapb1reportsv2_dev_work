# backend/orderarchive/models/order_archive_model.py
from django.db import models

class OrderDetail(models.Model):
    seller = models.CharField(max_length=255, blank=True, null=True, verbose_name="Satıcı")
    order_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sipariş No")
    order_date = models.DateField(blank=True, null=True, verbose_name="Sipariş Tarihi")
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Teslim Tarihi")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ülke")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Şehir")
    customer_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Müşteri Kod")
    customer_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Müşteri Adı")
    document_description = models.TextField(blank=True, null=True, verbose_name="Belge Açıklama")
    color_code = models.CharField(max_length=120, blank=True, null=True, verbose_name="Renk Kod")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Detay Açıklama")
    line_number = models.IntegerField(blank=True, null=True, verbose_name="Sıra No")
    item_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kalem Kod")
    item_description = models.TextField(blank=True, null=True, verbose_name="Kalem Tanım")
    quantity = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="Miktar")
    unit_price = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="Birim Fiyat")
    vat_percentage = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="KDV Yüzde")
    vat_amount = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="KDV Tutar")
    discount_rate = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="İskonto Oran")
    discount_amount = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="İskontolu Tutar")
    currency = models.CharField(max_length=20, blank=True, null=True, verbose_name="Döviz")
    exchange_rate = models.DecimalField(max_digits=25, decimal_places=6, blank=True, null=True, verbose_name="Kur")
    currency_price = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="Döviz Fiyat")
    currency_movement_amount = models.DecimalField(max_digits=25, decimal_places=4, blank=True, null=True, verbose_name="Döviz Hareket Tutar")

    def __str__(self):
        return f"Order {self.order_number or 'N/A'} - Line {self.line_number or 'N/A'}"
