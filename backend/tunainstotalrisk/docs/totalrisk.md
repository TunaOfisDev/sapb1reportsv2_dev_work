# TotalRisk API Amaç ve Model Yapısı

## Amaç

`TotalRisk` API'sinin temel amacı, belirli bir müşteri veya muhatap kartı için finansal riskin gerçekçi bir şekilde hesaplanmasını sağlamaktır. Bu hesaplama, müşterinin cari bakiyelerinin toplamını, açık ve onaylı siparişlerin toplam tutarını, ve sevk edilmiş ancak henüz faturalanmamış irsaliyelerin toplam tutarını TL cinsinden toplayarak gerçekleştirilir. Bu üç bileşenin toplamı, müşterinin toplam riskini temsil eder. Bu bilgi, finansal planlama ve risk yönetimi süreçlerinde kullanılır.

## Model Yapısı

Model, `TotalRisk` adında bir Django modeli olarak tanımlanmıştır. Bu model, SAP HANA veritabanındaki ilgili tabloyla eşleştirilmiş ve aşağıdaki alanlar tanımlanmıştır:

# backend/totalrisk/models/models.py
from django.db import models
from .base import BaseModel

class TotalRiskReport(BaseModel):
    muhatap_kod = models.CharField(max_length=50, verbose_name="Muhatap Kod")
    avans_kod = models.CharField(max_length=50, blank=True, null=True, verbose_name="Avans Kod")
    muhatap_ad = models.CharField(max_length=255, verbose_name="Muhatap Adı")
    bakiye = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Bakiye")
    acik_teslimat = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Açık Teslimat")
    acik_siparis = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Açık Sipariş")
    toplam_risk = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Toplam Risk", editable=False)

    def save(self, *args, **kwargs):
        self.toplam_risk = self.bakiye + self.acik_teslimat + self.acik_siparis
        super(TotalRiskReport, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Toplam Risk Raporu"
        verbose_name_plural = "Toplam Risk Raporları"
```

