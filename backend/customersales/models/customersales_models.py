# backend/customersales/models/customersales_models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel

# CustomerSalesReportPreset modeli ve ilgili tüm kodlar buradan silindi.

# DÜZELTME: Model artık standart models.Model yerine projenin BaseModel'ından miras alıyor.
class CustomerSalesRawData(BaseModel):
    """
    HANA'dan çekilen ham müşteri satış verilerini saklamak için kullanılan model.
    BaseModel'dan miras alarak created_at, updated_at ve is_active alanlarını kazanır.
    """
    satici = models.CharField(_("Satıcı"), max_length=255)
    satis_tipi = models.CharField(_("Satış Tipi"), max_length=50)
    cari_grup = models.CharField(_("Cari Grup"), max_length=100)
    musteri_kodu = models.CharField(_("Müşteri Kodu"), max_length=50)
    musteri_adi = models.CharField(_("Müşteri Adı"), max_length=255)
    toplam_net_spb_eur = models.DecimalField(_("Toplam Net SPB EUR"), max_digits=19, decimal_places=2)
    ocak = models.DecimalField(_("Ocak"), max_digits=19, decimal_places=2, default=0)
    subat = models.DecimalField(_("Şubat"), max_digits=19, decimal_places=2, default=0)
    mart = models.DecimalField(_("Mart"), max_digits=19, decimal_places=2, default=0)
    nisan = models.DecimalField(_("Nisan"), max_digits=19, decimal_places=2, default=0)
    mayis = models.DecimalField(_("Mayıs"), max_digits=19, decimal_places=2, default=0)
    haziran = models.DecimalField(_("Haziran"), max_digits=19, decimal_places=2, default=0)
    temmuz = models.DecimalField(_("Temmuz"), max_digits=19, decimal_places=2, default=0)
    agustos = models.DecimalField(_("Ağustos"), max_digits=19, decimal_places=2, default=0)
    eylul = models.DecimalField(_("Eylül"), max_digits=19, decimal_places=2, default=0)
    ekim = models.DecimalField(_("Ekim"), max_digits=19, decimal_places=2, default=0)
    kasim = models.DecimalField(_("Kasım"), max_digits=19, decimal_places=2, default=0)
    aralik = models.DecimalField(_("Aralık"), max_digits=19, decimal_places=2, default=0)
    
    # DÜZELTME: Bu alan BaseModel'dan gelen 'updated_at' ile aynı işi yaptığı için kaldırıldı.
    # last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Müşteri Satış Ham Verisi")
        verbose_name_plural = _("Müşteri Satış Ham Verileri")
        indexes = [
            models.Index(fields=['satici']),
            models.Index(fields=['satis_tipi']),
            models.Index(fields=['cari_grup']),
        ]

    def __str__(self):
        return f"{self.musteri_adi} - {self.toplam_net_spb_eur} EUR"