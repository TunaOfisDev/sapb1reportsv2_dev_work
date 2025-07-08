# File: procure_compare/models/comparison.py
from django.db import models
from django.db.models import JSONField


class PurchaseComparison(models.Model):
    uniq_detail_no = models.CharField(max_length=50, unique=True)
    belge_no = models.CharField(max_length=20)
    tedarikci_kod = models.CharField(max_length=20)
    tedarikci_ad = models.CharField(max_length=100)
    belge_tarih = models.DateField()
    teslim_tarih = models.DateField(null=True, blank=True)
    belge_status = models.CharField(max_length=10)
    belge_aciklamasi = models.TextField(null=True, blank=True)
    sevk_adres = models.TextField(null=True, blank=True)

    kalem_grup = models.CharField(max_length=100, null=True, blank=True)
    satir_status = models.CharField(max_length=10)
    satir_no = models.IntegerField()
    kalem_kod = models.CharField(max_length=50)
    kalem_tanimi = models.CharField(max_length=255)
    birim = models.CharField(max_length=20)
    sip_miktar = models.DecimalField(max_digits=18, decimal_places=2)

    detay_kur = models.DecimalField(max_digits=18, decimal_places=4)
    detay_doviz = models.CharField(max_length=10)

    net_fiyat_dpb = models.DecimalField(max_digits=18, decimal_places=4)
    net_tutar_ypb = models.DecimalField(max_digits=18, decimal_places=2)

    referans_teklifler = JSONField(null=True, blank=True)
    teklif_fiyatlari_json = JSONField(null=True, blank=True)
    teklif_fiyatlari_list = JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase_comparisons"
        verbose_name = "Purchase Comparison"
        verbose_name_plural = "Purchase Comparisons"

    def __str__(self):
        return f"{self.belge_no} - {self.kalem_kod}"
