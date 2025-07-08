# backend/openorderdocsum/models/docsum.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class DocumentSummary(BaseModel):
    belge_no = models.CharField(max_length=50, unique=True, verbose_name="Belge Numarası", db_index=True)
    satici = models.CharField(max_length=100, verbose_name="Satıcı", blank=True, null=True)
    belge_tarih = models.DateField(verbose_name="Belge Tarihi", blank=True, null=True)
    teslim_tarih = models.DateField(verbose_name="Teslim Tarihi", blank=True, null=True)
    belge_onay = models.CharField(max_length=50, verbose_name="Belge Onayı", blank=True, null=True)
    belge_durum = models.CharField(max_length=50, verbose_name="Belge Durumu", blank=True, null=True)
    belge_aciklamasi = models.CharField(max_length=254, verbose_name="Belge Aciklamasi", blank=True, null=True)
    sevk_adres = models.CharField(max_length=254, verbose_name="Sevk Adres", blank=True, null=True)
    musteri_kod = models.CharField(max_length=50, verbose_name="Müşteri Kodu", db_index=True)
    musteri_ad = models.CharField(max_length=100, verbose_name="Müşteri Adı", blank=True, null=True)
    satis_tipi = models.CharField(max_length=50, verbose_name="Satış Tipi", blank=True, null=True)
    net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Net Tutar YPB")
    net_tutar_spb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Net Tutar SPB")
    acik_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Açık Net Tutar YPB")
    acik_net_tutar_spb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Açık Net Tutar SPB")
    brut_tutar_spb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="Brut Tutar SPB", default=0.0)

    class Meta:
        verbose_name = "Belge Özeti"
        verbose_name_plural = "Belge Özetleri"

    def __str__(self):
        return f"{self.belge_no} - {self.musteri_ad}"

    @property
    def belge_iskonto_oran(self):
        brut_tutar = self.brut_tutar_spb
        if brut_tutar > 0:
            return ((self.net_tutar_spb / brut_tutar - 1) * 100) * -1
        return 0
