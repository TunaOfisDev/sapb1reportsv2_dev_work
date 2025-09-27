# backend/openorderdocsum/models/docsum.py
from django.db import models
from django.db.models import Sum
from ..models.openorderdeail import OpenOrderDetail


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class DocumentSummary(BaseModel):
    belge_no = models.CharField(max_length=50, unique=True, verbose_name="Belge Numarası")
    satici = models.CharField(max_length=100, verbose_name="Satıcı", blank=True, null=True)
    belge_tarih = models.DateField(verbose_name="Belge Tarihi", blank=True, null=True)
    teslim_tarih = models.DateField(verbose_name="Teslim Tarihi", blank=True, null=True)
    belge_onay = models.CharField(max_length=50, verbose_name="Belge Onayı", blank=True, null=True)
    belge_durum = models.CharField(max_length=50, verbose_name="Belge Durumu", blank=True, null=True)
    sevk_adres = models.CharField(max_length=254, verbose_name="Sevk Adres", blank=True, null=True)
    musteri_kod = models.CharField(max_length=50, verbose_name="Müşteri Kodu")
    musteri_ad = models.CharField(max_length=100, verbose_name="Müşteri Adı", blank=True, null=True)
    satis_tipi = models.CharField(max_length=50, verbose_name="Satış Tipi", blank=True, null=True)
    net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Net Tutar YPB")
    acik_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Açık Net Tutar YPB")
    acik_net_tutar_spb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Açık Net Tutar SPB")
    girsberger_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Girsberger Net Tutar YPB")
    mamul_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Mamul Net Tutar YPB")
    ticari_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ticari Net Tutar YPB")
    nakliye_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Nakliye Net Tutar YPB")
    montaj_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montaj Net Tutar YPB")


    class Meta:
        verbose_name = "Belge Özeti"
        verbose_name_plural = "Belge Özetleri"

    def __str__(self):
        return f"{self.belge_no} - {self.musteri_ad}"

    @property
    def belge_iskonto_oran(self):
        details = OpenOrderDetail.objects.filter(belge_no=self.belge_no)
        if details.exists():
            total_net_price = details.aggregate(Sum('net_fiyat_dpb'))['net_fiyat_dpb__sum']
            total_list_price = details.aggregate(Sum('liste_fiyat_dpb'))['liste_fiyat_dpb__sum']
            if total_list_price > 0:
                return (1 - (total_net_price / total_list_price)) * 100
        return 0



