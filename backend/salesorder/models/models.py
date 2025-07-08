# backend/salesorder/models/models.py
from django.db import models
from .base import BaseModel

class SalesOrder(BaseModel):
    satici = models.CharField(max_length=255, verbose_name="Satıcı")
    belge_tur = models.CharField(max_length=50, verbose_name="Belge Türü")
    onay1_status = models.CharField(max_length=1, null=True, blank=True, verbose_name="Onay 1 Durumu")
    onay2_status = models.CharField(max_length=1, null=True, blank=True, verbose_name="Onay 2 Durumu")
    belge_tarihi = models.DateField(verbose_name="Belge Tarihi")
    teslim_tarihi = models.DateField(verbose_name="Teslim Tarihi")
    belge_status = models.CharField(max_length=1, verbose_name="Belge Durumu")
    musteri_kod = models.CharField(max_length=50, verbose_name="Müşteri Kodu")
    musteri_ad = models.CharField(max_length=255, verbose_name="Müşteri Adı")
    belge_giris_no = models.IntegerField(verbose_name="Belge Giriş No")
    sip_no = models.CharField(max_length=50, verbose_name="Sipariş No")
    satis_tipi = models.CharField(max_length=50, verbose_name="Satış Tipi")
    belge_aciklamasi = models.TextField(null=True, blank=True, verbose_name="Belge Açıklaması")
    sevk_adresi = models.TextField(null=True, blank=True, verbose_name="Sevk Adresi")
    unique_master_no = models.CharField(max_length=100, unique=True, verbose_name="Eşsiz Anahtar No")
    kalem_grup_kod = models.CharField(max_length=50, null=True, blank=True, verbose_name="Kalem Grup Kodu")
    kalem_grup = models.CharField(max_length=255, null=True, blank=True, verbose_name="Kalem Grubu")
    eski_bilesen_kod = models.CharField(max_length=50, null=True, blank=True, verbose_name="Eski Bileşen Kodu")
    musteri_sip_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Müşteri Sipariş No")
    musteri_sip_tarih = models.DateField(null=True, blank=True, verbose_name="Müşteri Sipariş Tarihi")
    assmann_comm_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Assmann Komisyon No")
    assmann_pos_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Assmann Pozisyon No")
    assmann_item_no = models.CharField(max_length=50, null=True, blank=True, verbose_name="Assmann Ürün No")
    renk_kod = models.CharField(max_length=50, null=True, blank=True, verbose_name="Renk Kodu")
    uretim_aciklamasi = models.TextField(null=True, blank=True, verbose_name="Üretim Açıklaması")
    satir_status = models.CharField(max_length=1, verbose_name="Satır Durumu")
    satir_no = models.IntegerField(verbose_name="Satır No")
    depo_kod = models.CharField(max_length=50, verbose_name="Depo Kodu")
    kalem_kod = models.CharField(max_length=50, verbose_name="Kalem Kodu")
    kalem_tanimi = models.CharField(max_length=255, verbose_name="Kalem Tanımı")
    birim = models.CharField(max_length=50, verbose_name="Birim")
    sip_miktar = models.DecimalField(max_digits=20, decimal_places=4, verbose_name="Sipariş Miktarı")
    sevk_miktar = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Sevk Miktarı")
    kalan_miktar = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Kalan Miktar")
    liste_fiyat_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Liste Fiyatı DPB")
    iskonto_oran = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, verbose_name="İskonto Oranı")
    net_fiyat_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Net Fiyat DPB")
    brut_tutar_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Brüt Tutar DPB")
    net_tutar_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Net Tutar DPB")
    isk_tutar_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="İskonto Tutarı DPB")
    kdv_tutar_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="KDV Tutarı DPB")
    kdvli_net_tutar_dpb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="KDV'li Net Tutar DPB")
    kur = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, verbose_name="Kur")
    doviz = models.CharField(max_length=6, null=True, blank=True, verbose_name="Döviz")
    liste_fiyat_ypb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Liste Fiyatı YPB")
    brut_tutar_ypb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Brüt Tutar YPB")
    isk_tutar_ypb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="İskonto Tutarı YPB")
    net_tutar_ypb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="Net Tutar YPB")
    kdv_oran = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="KDV Oranı")
    kdv_tutar_ypb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="KDV Tutarı YPB")
    kdvli_net_tutar_ypb = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="KDV'li Net Tutar YPB")

    class Meta:
        verbose_name = "Satış Siparişi"
        verbose_name_plural = "Satış Siparişleri"

    def __str__(self):
        return f"{self.sip_no} - {self.musteri_ad}"

