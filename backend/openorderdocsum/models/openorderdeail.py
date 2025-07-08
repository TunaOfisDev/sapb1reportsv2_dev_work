# backend/openorderdocsum/models/openorderdeail.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class OpenOrderDetail(BaseModel):
    uniq_detail_no = models.CharField(max_length=100, unique=True, verbose_name="Benzersiz Detay Numarası")
    belge_no = models.CharField(max_length=50, verbose_name="Belge Numarası")
    satici = models.CharField(max_length=100, verbose_name="Satıcı", blank=True, null=True)
    belge_tarih = models.DateField(verbose_name="Belge Tarihi", blank=True, null=True)
    teslim_tarih = models.DateField(verbose_name="Teslim Tarihi", blank=True, null=True)
    belge_onay = models.CharField(max_length=50, verbose_name="Belge Onay", blank=True, null=True)
    belge_durum = models.CharField(max_length=50, verbose_name="Belge Durumu", blank=True, null=True)
    sevk_adres = models.CharField(max_length=254, verbose_name="Sevk Adres", blank=True, null=True)
    musteri_kod = models.CharField(max_length=50, verbose_name="Müşteri Kodu")
    musteri_ad = models.CharField(max_length=100, verbose_name="Müşteri Adı", blank=True, null=True)
    satis_tipi = models.CharField(max_length=50, verbose_name="Satış Tipi", blank=True, null=True)
    kalem_grup = models.CharField(max_length=100, verbose_name="Kalem Grubu", blank=True, null=True)
    satir_durum = models.CharField(max_length=50, verbose_name="Satır Durumu")
    kalem_kod = models.CharField(max_length=50, verbose_name="Kalem Kodu")
    kalem_tanimi = models.CharField(max_length=200, verbose_name="Kalem Tanımı")
    birim = models.CharField(max_length=50, verbose_name="Birim")
    siparis_miktari = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sipariş Miktarı", default=0.0)
    sevk_miktari = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sevk Miktarı", default=0.0)
    kalan_miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kalan Miktar", default=0.0)
    liste_fiyat_dpb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Liste Fiyatı DPB", default=0.0)
    detay_kur = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Detay Kur", default=1.0)
    detay_doviz = models.CharField(max_length=10, verbose_name="Detay Döviz")
    iskonto_oran = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="İskonto Oranı", default=0.0)
    net_fiyat_dpb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Net Fiyat DPB", default=0.0)
    net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Net Tutar YPB", default=0.0)
    acik_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Açık Net Tutar YPB", default=0.0)
    acik_net_tutar_spb = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Açık Net Tutar SPB", default=0.0)
    girsberger_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Girsberger Net Tutar YPB", default=0.0)
    mamul_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Mamul Net Tutar YPB", default=0.0)
    ticari_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ticari Net Tutar YPB", default=0.0)
    nakliye_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Nakliye Net Tutar YPB", default=0.0)
    montaj_net_tutar_ypb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montaj Net Tutar YPB", default=0.0)

    
    class Meta:
        verbose_name = "Açık Sipariş Detayı"
        verbose_name_plural = "Açık Sipariş Detayları"

    def __str__(self):
        return f"{self.belge_no} - {self.musteri_ad}"
