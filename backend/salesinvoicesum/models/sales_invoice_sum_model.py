# backend/salesinvoicesum/models/sales_invoice_sum_model.py
from django.db import models
from .base import BaseModel

class SalesInvoiceSum(BaseModel):
    representative = models.CharField(max_length=255, verbose_name="Temsilci")
    customer_group = models.CharField(max_length=255, verbose_name="Cari Grup")
    customer_code = models.CharField(max_length=50, verbose_name="Cari Kod")
    customer_name = models.CharField(max_length=255, verbose_name="Cari Adi")
    debt_balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Borç Bakiyesi")
    advance_balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Avans Bakiyesi")
    today_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Bugün")
    yesterday_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Dün")
    two_days_ago_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="İki Gün Önce")
    three_days_ago_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Üc Gün Önce")
    four_days_ago_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Dört Gün Önce")
    weekly_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Hafta Toplam")
    monthly_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Bu Ay Toplam")
    last_month_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Geçen Ay Toplam")
    yearly_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Bu Yıl Toplam")
    open_orders_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Açık Sipariş Toplamı")
    open_shipments_total = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Açık Sevkiyat Toplamı")
    invoice_count = models.PositiveIntegerField(verbose_name="Fatura Sayısı")

    def __str__(self):
        return f"{self.customer_name} ({self.customer_code})"