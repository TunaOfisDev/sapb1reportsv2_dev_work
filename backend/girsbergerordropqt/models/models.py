# backend/girsbergerordropqtctrl/models/models.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class OrdrDetailOpqt(BaseModel):
    uniq_detail_no = models.CharField(max_length=255, unique=True)  # UniqDetailNo
    belge_no = models.CharField(max_length=255, db_index=True)  # BelgeNo
    satici = models.CharField(max_length=255, db_index=True)  # Satici
    belge_tarih = models.DateField(db_index=True)  # BelgeTarih
    teslim_tarih = models.DateField(db_index=True)  # TeslimTarih
    musteri_kod = models.CharField(max_length=255, db_index=True)  # MusteriKod
    musteri_ad = models.CharField(max_length=255)  # MusteriAd
    satis_tipi = models.CharField(max_length=255)  # SatisTipi
    kalem_kod = models.CharField(max_length=255, db_index=True)  # KalemKod (Yeni Alan)
    kalem_tanimi = models.CharField(max_length=255)  # KalemTanimi (Yeni Alan)
    satir_status = models.CharField(max_length=10, db_index=True)  # SatirStatus
    sip_miktar = models.FloatField()  # SipMiktar
    salma_teklif_tedarikci_kod = models.CharField(max_length=255, null=True, blank=True)  # SalmaTeklifTedarikciKod
    salma_teklif_tedarikci_ad = models.CharField(max_length=255, null=True, blank=True)  # SalmaTeklifTedarikciAd
    salma_teklif_no = models.CharField(max_length=255, null=True, blank=True)  # SalmaTeklifNo
    salma_teklif_kaynak_detay_no = models.CharField(max_length=255, null=True, blank=True)  # SalmaTeklifKaynakDetayNo
    salma_teklif_kalem_no = models.CharField(max_length=255, null=True, blank=True)  # SalmaTeklifKalemNo
    salma_teklif_miktar = models.FloatField(null=True, blank=True)  # SalmaTeklifMiktar


    class Meta:
        indexes = [
            models.Index(fields=['uniq_detail_no']),
            models.Index(fields=['belge_no']),
            models.Index(fields=['satici']),
            models.Index(fields=['belge_tarih']),
            models.Index(fields=['teslim_tarih']),
            models.Index(fields=['musteri_kod']),
            models.Index(fields=['kalem_kod']),
            models.Index(fields=['satir_status']),
     
        ]

    def __str__(self):
        return self.uniq_detail_no
