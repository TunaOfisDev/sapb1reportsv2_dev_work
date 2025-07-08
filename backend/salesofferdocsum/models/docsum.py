# backend/salesofferdocsum/models/docsum.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class DocumentSummary(BaseModel):
    belge_no = models.CharField(max_length=50, unique=True, verbose_name="BelgeNo", db_index=True)
    satici = models.CharField(max_length=100, verbose_name="Satıcı", blank=True, null=True)
    belge_tarih = models.DateField(verbose_name="BelgeTarihi", blank=True, null=True)
    teslim_tarih = models.DateField(verbose_name="TeslimTarihi", blank=True, null=True)
    belge_onay = models.CharField(max_length=50, verbose_name="BelgeOnayı", blank=True, null=True)
    iptal_edilen = models.CharField(max_length=50, verbose_name="IptalEdilen", blank=True, null=True)
    elle_kapatilan = models.CharField(max_length=50, verbose_name="ElleKapatilan", blank=True, null=True)
    siparise_aktarilan = models.CharField(max_length=50, verbose_name="SipariseAktarilan", blank=True, null=True)
    belge_durum = models.CharField(max_length=50, verbose_name="BelgeDurumu", blank=True, null=True)
    belge_aciklamasi = models.CharField(max_length=254, verbose_name="BelgeAciklamasi", blank=True, null=True)
    sevk_adres = models.CharField(max_length=254, verbose_name="SevkAdres", blank=True, null=True)
    musteri_kod = models.CharField(max_length=50, verbose_name="MüşteriKodu", db_index=True)
    musteri_ad = models.CharField(max_length=100, verbose_name="MüşteriAdı", blank=True, null=True)
    satis_tipi = models.CharField(max_length=50, verbose_name="SatışTipi", blank=True, null=True)
    net_tutar_ypb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="NetTutarYPB")
    net_tutar_spb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="NetTutarSPB")
    brut_tutar_spb = models.DecimalField(max_digits=16, decimal_places=2, verbose_name="BrutTutarSPB")

    class Meta:
        verbose_name = "Belge Özeti"
        verbose_name_plural = "Belge Özetleri"

    def __str__(self):
        return f"{self.belge_no} - {self.musteri_ad}"

    @property
    def belge_iskonto_oran(self):
        if self.brut_tutar_spb and self.brut_tutar_spb != 0:
            return ((self.net_tutar_spb / self.brut_tutar_spb - 1) * 100) * -1
        return 0



