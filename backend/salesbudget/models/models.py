# backend/salesbudget/models/models.py
from django.db import models
from .base import BaseModel


class SalesBudget(BaseModel):
    satici = models.CharField(max_length=100)
   
    # Toplam gerçekleşen ve hedeflenen tutarlar
    toplam_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    toplam_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    # Aylık gerçekleşen ve hedeflenen tutarlar
    oca_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    oca_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    
    sub_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    sub_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    mar_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    mar_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    nis_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    nis_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    may_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    may_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    haz_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    haz_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    tem_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    tem_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    agu_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    agu_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    eyl_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    eyl_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    eki_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    eki_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    kas_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    kas_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    ara_gercek = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    ara_hedef = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)

    def __str__(self):
        return f"{self.satici}"

    def yuzde_oran_hesapla(self):
        # Yıllık toplam gerçekleşen ve hedeflenen tutarlar için yüzde oran hesaplaması
        if self.toplam_hedef and self.toplam_hedef > 0:
            return (self.toplam_gercek / self.toplam_hedef * 100 )
        return 0
