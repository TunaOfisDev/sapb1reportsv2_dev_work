from django.db import models
from .base import BaseModel
from django.utils import timezone
from datetime import datetime, date

class ShipmentOrder(BaseModel):
    OPEN = 'Acik'
    CLOSED = 'Kapali'

    ORDER_STATUS_CHOICES = [
        (OPEN, 'Acik'),
        (CLOSED, 'Kapali'),
    ]

    order_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="SiparisNo")
    customer_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="MusteriAd")
    order_date = models.DateField(default=timezone.now, blank=True, null=True, verbose_name="SiparisTarihi")
    shipment_date = models.DateField(blank=True, null=True, verbose_name="SevkTarihi")
    planned_dates = models.JSONField(default=list, blank=True, null=True, verbose_name="PlanlananTarihler")
    planned_date_real = models.DateField(blank=True, null=True, verbose_name="GercekPlanlananTarih")
    planned_date_mirror = models.DateField(blank=True, null=True, verbose_name="PlanlananTarih")
    planned_date_week = models.IntegerField(blank=True, null=True, verbose_name="PlanHaftasi")
    sales_person = models.CharField(max_length=255, blank=True, null=True, verbose_name="Satici")
    shipment_details = models.TextField(blank=True, null=True, verbose_name="SevkDetaylari")
    shipment_notes = models.TextField(blank=True, null=True, verbose_name="SevkNotlari")
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default=OPEN, verbose_name="Statu")
    selected_color = models.CharField(max_length=7, blank=True, null=True, verbose_name="Seçilen Renk")

    def admin_save(self, *args, **kwargs):
        """
        Admin paneli için kullanılan özel save metodu.
        """
        try:
            # planned_dates listesini kontrol et ve oluştur
            if self.planned_dates is None:
                self.planned_dates = []

            # Eğer planned_date_mirror varsa ve tarih ise, string'e çevir ve listeye ekle
            if self.planned_date_mirror:
                if isinstance(self.planned_date_mirror, (date, datetime)):
                    mirror_date_str = self.planned_date_mirror.strftime("%d.%m.%Y")
                else:
                    mirror_date_str = str(self.planned_date_mirror)
                
                if mirror_date_str not in self.planned_dates:
                    self.planned_dates.append(mirror_date_str)
                self.planned_date_mirror = None

            # planned_dates listesindeki son tarihi planned_date_real'e aktar
            if self.planned_dates:
                last_date_str = self.planned_dates[-1]
                if isinstance(last_date_str, str):
                    try:
                        self.planned_date_real = datetime.strptime(last_date_str, "%d.%m.%Y").date()
                    except ValueError:
                        try:
                            self.planned_date_real = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                        except ValueError:
                            self.planned_date_real = None

            # Hafta numarasını hesapla
            if self.planned_date_real and isinstance(self.planned_date_real, date):
                self.planned_date_week = self.planned_date_real.isocalendar()[1]
            else:
                self.planned_date_week = None

            # Sipariş durumunu güncelle
            if self.shipment_date:
                self.order_status = self.CLOSED
            else:
                self.order_status = self.OPEN

            super(ShipmentOrder, self).save(*args, **kwargs)
        except Exception as e:
            print(f"Error in admin_save: {str(e)}")
            raise


    def save(self, *args, **kwargs):
        """
        Frontend işlemleri için çalışan orijinal save metodu.
        """
        # Frontend'ten gelen verilerle çalışır, format dönüştürmez
        if self.planned_dates:
            self.planned_dates = [
                d.isoformat() if isinstance(d, (date, datetime)) else str(d)
                for d in self.planned_dates if d is not None
            ]

        # planned_date_mirror'u planned_dates listesine ekliyoruz
        if self.planned_date_mirror:
            if self.planned_dates is None:
                self.planned_dates = []
            mirror_date_str = self.planned_date_mirror.isoformat() if isinstance(self.planned_date_mirror, (date, datetime)) else str(self.planned_date_mirror)
            if mirror_date_str not in self.planned_dates:
                self.planned_dates.append(mirror_date_str)
            self.planned_date_mirror = None

        # planned_dates'deki son tarih planned_date_real olarak ayarlanacak
        if self.planned_dates:
            self.planned_date_real = datetime.strptime(self.planned_dates[-1], "%Y-%m-%d").date()

        # planned_date_real'den hafta numarasını hesapla
        if self.planned_date_real:
            self.planned_date_week = self.planned_date_real.isocalendar()[1]

        # Eğer shipment_date varsa sipariş kapalı olur
        if self.shipment_date:
            self.order_status = self.CLOSED
        else:
            self.order_status = self.OPEN

        super(ShipmentOrder, self).save(*args, **kwargs)
