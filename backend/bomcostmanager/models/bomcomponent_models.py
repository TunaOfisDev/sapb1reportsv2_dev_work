# backend/bomcostmanager/models/bomcomponent_models.py

from django.db import models
from django.core.validators import MinValueValidator
from .base import BaseModel

class BOMComponent(BaseModel):
    """
    BOM (Bill of Materials) maliyet analizinde kullanılan kalem detaylarını saklar.
    Kullanıcı, SAP HANA’dan çekilen verilerle birlikte, override edilebilen
    yeni son satın alma fiyatı, döviz ve çarpan alanları üzerinden güncel maliyeti hesaplayabilir.
    """
    main_item = models.CharField("Ana Ürün Kodu", max_length=50)
    sub_item = models.CharField("Alt Ürün/Kod", max_length=50, blank=True, null=True)
    component_item_code = models.CharField("Bileşen Stok Kodu", max_length=50)
    component_item_name = models.CharField("Bileşen Adı", max_length=200, blank=True, null=True)
    quantity = models.DecimalField("Miktar", max_digits=18, decimal_places=2, validators=[MinValueValidator(0)])
    level = models.IntegerField("BOM Seviyesi")
    type_description = models.CharField("Kalem Tipi", max_length=50)
    last_purchase_price = models.DecimalField("Son Satın Alma Fiyatı", max_digits=18, decimal_places=2, default=0)
    currency = models.CharField("Para Birimi", max_length=10, default='TRY')
    rate = models.DecimalField("Döviz Kuru", max_digits=18, decimal_places=4, default=1)
    last_purchase_price_upb = models.DecimalField("Birim Satın Alma Fiyatı", max_digits=18, decimal_places=2, default=0)
    price_source = models.CharField("Fiyat Kaynağı", max_length=50, default='Taban Fiyat')
    doc_date = models.DateField("Belge Tarihi", blank=True, null=True)
    component_cost_upb = models.DecimalField("Bileşen Maliyeti", max_digits=18, decimal_places=2, default=0)
    sales_price = models.DecimalField("Satış Fiyatı", max_digits=18, decimal_places=2, default=0)
    sales_currency = models.CharField("Satış Para Birimi", max_length=10, default='TRY')
    price_list_name = models.CharField("Fiyat Listesi Adı", max_length=50, default='YOK')
    item_group_name = models.CharField("Ürün Grubu", max_length=100, blank=True, null=True)

    # Kullanıcı override alanları (satın alma fiyatı override)
    new_last_purchase_price = models.DecimalField(
        "Yeni Son Satın Alma Fiyatı", max_digits=18, decimal_places=2, default=0,
        help_text="Kullanıcı tarafından girilebilen yeni son satın alma fiyatı (override)"
    )
    new_currency = models.CharField(
        "Yeni Döviz", max_length=10, default='',
        help_text="Kullanıcı tarafından girilebilen yeni döviz cinsi (override). Boş bırakılırsa orijinal değer kullanılır."
    )

    # Master çarpan faktörler (override sonrası nihai maliyeti hesaplamak için)
    labor_multiplier = models.DecimalField(
        "İşçilik Çarpanı", max_digits=10, decimal_places=4, default=1,
        help_text="Ham madde maliyeti üzerine uygulanacak işçilik çarpanı"
    )
    overhead_multiplier = models.DecimalField(
        "Genel Üretim Gideri Çarpanı", max_digits=10, decimal_places=4, default=1,
        help_text="Ham madde maliyeti üzerine uygulanacak genel üretim gideri çarpanı"
    )
    license_multiplier = models.DecimalField(
        "Lisans Çarpanı", max_digits=10, decimal_places=4, default=1,
        help_text="Ürün üzerindeki lisans ve komisyon giderlerini hesaplamak için kullanılacak çarpan"
    )
    commission_multiplier = models.DecimalField(
        "Komisyon Çarpanı", max_digits=10, decimal_places=4, default=1,
        help_text="Ürün satışından doğan komisyon giderlerini hesaplamak için kullanılacak çarpan"
    )

    # Güncel maliyet: Hesaplanan ham madde maliyeti * tüm master çarpanlar
    updated_cost = models.DecimalField(
        "Güncel Maliyet", max_digits=18, decimal_places=2, default=0,
        help_text="Ham madde maliyeti, override fiyatı ve master çarpanların (işçilik, genel gider, lisans, komisyon) "
                  "ile hesaplanmış nihai maliyet"
    )

    def save(self, *args, **kwargs):
        # Override alanı girilmişse onu kullan; aksi halde orijinal birim fiyat üzerinden hesapla.
        effective_price = self.new_last_purchase_price if self.new_last_purchase_price > 0 else self.last_purchase_price_upb
        # Master çarpanların tamamı ile güncel maliyeti hesapla.
        self.updated_cost = effective_price * self.labor_multiplier * self.overhead_multiplier * self.license_multiplier * self.commission_multiplier
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.main_item} - {self.component_item_code}"

    class Meta:
        verbose_name = "BOM Kalemi"
        verbose_name_plural = "BOM Kalemleri"


class BOMRecord(BaseModel):
    """
    Bu model, mamul (ürün ağacı) oluşturma ve güncelleme bilgilerini saklar.
    Kullanıcı, hesaplanan BOM raporunu bir proje adı altında kaydedip, daha sonra rapor
    üzerinde değişiklik yapabilir (versiyonlama).
    """
    project_name = models.CharField("Proje Adı", max_length=255)
    description = models.TextField("Açıklama", blank=True, null=True)
    created_by = models.CharField("Oluşturan Kullanıcı", max_length=50, blank=True, null=True)

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "BOM Kaydı"
        verbose_name_plural = "BOM Kayıtları"
