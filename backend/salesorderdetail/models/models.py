# backend/salesorderdetail/models/models.py
from django.db import models
from django.db.models import Sum
from .base import BaseModel

class SalesOrderMaster(BaseModel):
    master_unique_id = models.CharField(max_length=255, unique=True)
    master_belge_giris_no = models.IntegerField()
    sip_no = models.CharField(max_length=50, blank=True, null=True)
    satis_tipi = models.CharField(max_length=50, blank=True, null=True)
    satici = models.CharField(max_length=255, blank=True, null=True)
    belge_tur = models.CharField(max_length=50, blank=True, null=True)
    onay1_status = models.CharField(max_length=10, blank=True, null=True)
    onay2_status = models.CharField(max_length=10, blank=True, null=True)
    belge_tarihi = models.CharField(max_length=10, blank=True, null=True)
    teslim_tarihi = models.CharField(max_length=10, blank=True, null=True)
    belge_onay = models.CharField(max_length=10, blank=True, null=True)
    belge_status = models.CharField(max_length=10, blank=True, null=True)
    belge_kur = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    belge_doviz = models.CharField(max_length=8, blank=True, null=True)
    musteri_kod = models.CharField(max_length=50, blank=True, null=True)
    musteri_ad = models.CharField(max_length=255, blank=True, null=True)

    # Hesaplanmış alanları model içinde metod olarak tanımlayabiliriz
    def calculate_totals(self):
        totals = self.details.aggregate(
            total_brut_tutar_dpb=Sum('brut_tutar_dpb'),
            total_net_tutar_dpb=Sum('net_tutar_dpb'),
            total_isk_tutar_dpb=Sum('isk_tutar_dpb'),
            total_kdv_tutar_dpb=Sum('kdv_tutar_dpb'),
            total_kdvli_net_tutar_dpb=Sum('kdvli_net_tutar_dpb'),
            total_liste_fiyat_ypb=Sum('liste_fiyat_ypb'),
            total_brut_tutar_ypb=Sum('brut_tutar_ypb'),
            total_isk_tutar_ypb=Sum('isk_tutar_ypb'),
            total_net_tutar_ypb=Sum('net_tutar_ypb'),
            total_kdv_tutar_ypb=Sum('kdv_tutar_ypb'),
            total_kdvli_net_tutar_ypb=Sum('kdvli_net_tutar_ypb')
        )
        return {key: value if value is not None else 0 for key, value in totals.items()}

    class Meta:
        verbose_name = 'Satış Sipariş Ana Bilgisi'
        verbose_name_plural = 'Satış Sipariş Ana Bilgileri'



class SalesOrderDetail(BaseModel):
    master = models.ForeignKey(SalesOrderMaster, related_name='details', on_delete=models.CASCADE)
    detay_belge_giris_no = models.IntegerField()
    detay_unique_id = models.CharField(max_length=255, unique=True)
    kalem_grup = models.CharField(max_length=50, blank=True, null=True)
    satir_status = models.CharField(max_length=10, blank=True, null=True)
    satir_no = models.IntegerField(blank=True, null=True)
    depo_kod = models.CharField(max_length=50, blank=True, null=True)
    kalem_kod = models.CharField(max_length=50, blank=True, null=True)
    kalem_tanimi = models.CharField(max_length=255, blank=True, null=True)
    birim = models.CharField(max_length=50, blank=True, null=True)
    sip_miktar = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    sevk_miktar = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    kalan_miktar = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    liste_fiyat_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    detay_kur = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    detay_doviz = models.CharField(max_length=3, blank=True, null=True)
    iskonto_oran = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    net_fiyat_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    brut_tutar_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    net_tutar_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    isk_tutar_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    kdv_tutar_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    kdvli_net_tutar_dpb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    liste_fiyat_ypb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    brut_tutar_ypb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    isk_tutar_ypb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    net_tutar_ypb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    kdv_oran = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    kdv_tutar_ypb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    kdvli_net_tutar_ypb = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Eğer detay_belge_giris_no, ilişkili master'ın belge_giris_no'su ile eşleşmiyorsa, ilişkilendirmeyi kontrol et
        if self.master.master_belge_giris_no != self.detay_belge_giris_no:
            raise ValueError('Master belge giriş numarası ile detay belge giriş numarası eşleşmiyor.')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Satış Sipariş Detayı'
        verbose_name_plural = 'Satış Sipariş Detayları'
    