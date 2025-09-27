# backend/salesofferdocsum/models/salesofferdetail.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SalesOfferDetail(BaseModel):
    uniq_detail_no = models.CharField(max_length=100, unique=True, verbose_name="UniqDetayNo")
    iptal_edilen = models.CharField(max_length=50, verbose_name="IptalEdilen", blank=True, null=True)
    elle_kapatilan = models.CharField(max_length=50, verbose_name="ElleKapatilan", blank=True, null=True)
    siparise_aktarilan = models.CharField(max_length=50, verbose_name="SipariseAktarilan", blank=True, null=True)
    belge_durum = models.CharField(max_length=50, verbose_name="BelgeDurumu", blank=True, null=True)
    belge_no = models.CharField(max_length=50, verbose_name="BelgeNumarası", db_index=True)
    satici = models.CharField(max_length=100, verbose_name="Satıcı", blank=True, null=True, db_index=True)
    belge_tarih = models.DateField(verbose_name="BelgeTarihi", blank=True, null=True, db_index=True)
    teslim_tarih = models.DateField(verbose_name="TeslimTarihi", blank=True, null=True, db_index=True)
    belge_onay = models.CharField(max_length=50, verbose_name="BelgeOnay", blank=True, null=True)
    belge_aciklamasi = models.CharField(max_length=254, verbose_name="BelgeAciklamasi", blank=True, null=True)
    sevk_adres = models.CharField(max_length=254, verbose_name="SevkAdres", blank=True, null=True)
    musteri_kod = models.CharField(max_length=50, verbose_name="MüşteriKodu", db_index=True)
    musteri_ad = models.CharField(max_length=100, verbose_name="MüşteriAdı", blank=True, null=True)
    satis_tipi = models.CharField(max_length=50, verbose_name="SatışTipi", blank=True, null=True)
    kalem_grup = models.CharField(max_length=100, verbose_name="KalemGrubu", blank=True, null=True)
    satir_durum = models.CharField(max_length=50, verbose_name="SatırDurumu", db_index=True)
    satir_no = models.CharField(max_length=50, verbose_name="SatırDurumu")
    kalem_kod = models.CharField(max_length=50, verbose_name="KalemKodu", db_index=True)
    kalem_tanimi = models.CharField(max_length=200, verbose_name="KalemTanımı", db_index=True)
    birim = models.CharField(max_length=50, verbose_name="Birim")
    siparis_miktari = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="SiparişMiktarı", default=0.0)
    liste_fiyat_dpb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="ListeFiyatıDPB", default=0.0)
    detay_kur = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="DetayKur", default=1.0)
    detay_doviz = models.CharField(max_length=10, verbose_name="DetayDöviz")
    iskonto_oran = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="İskOran", default=0.0)
    net_fiyat_dpb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="NetFiyatDPB", default=0.0)
    net_tutar_ypb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="NetTutarYPB", default=0.0)
    net_tutar_spb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="NetTutarSPB", default=0.0)
    brut_tutar_spb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="BrutTutarSPB", default=0.0)


    class Meta:
        verbose_name = "Satis Teklif Detayı"
        verbose_name_plural = "Satis Teklif Detayları"

    def __str__(self):
        return f"{self.belge_no} - {self.musteri_ad}"

