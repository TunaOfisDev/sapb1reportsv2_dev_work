# backend/bomcostmanager/models/bomproduct_models.py

from django.db import models
from .base import BaseModel

class BOMProduct(BaseModel):
    """
    Bu model, BOM (ürün ağacı) oluşturma/güncelleme için temel stok bilgilerini saklar.
    Örneğin:
      - Ürün Kodu, Ürün Adı, Varsayılan Depo,
      - Stok Kalemi, Satılabilir, Satın Alınabilir,
      - Satış Fiyat Listesi, Satış Fiyatı, Para Birimi,
      - BOM Oluşturma ve Güncelleme Tarihleri,
      - Oluşturan ve Güncelleyen Kullanıcı Kodları.
    """
    item_code = models.CharField("Ürün Kodu", max_length=50)
    item_name = models.CharField("Ürün Adı", max_length=200)
    default_wh = models.CharField("Varsayılan Depo", max_length=50, blank=True, null=True)
    invnt_item = models.BooleanField("Stok Kalemi", default=True)
    sell_item = models.BooleanField("Satılabilir", default=True)
    purch_item = models.BooleanField("Satın Alınabilir", default=True)
    sales_price_list = models.CharField("Satış Fiyat Listesi", max_length=50, default='YOK')
    sales_price = models.DecimalField("Satış Fiyatı", max_digits=18, decimal_places=2, default=0)
    currency = models.CharField("Para Birimi", max_length=10, default='TRY')
    bom_create_date = models.DateField("BOM Oluşturma Tarihi", blank=True, null=True)
    bom_update_date = models.DateField("BOM Güncelleme Tarihi", blank=True, null=True)
    created_user_code = models.CharField("Oluşturan Kullanıcı Kodu", max_length=50, blank=True, null=True)
    updated_user_code = models.CharField("Güncelleyen Kullanıcı Kodu", max_length=50, blank=True, null=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    class Meta:
        verbose_name = "BOM Ürünü"
        verbose_name_plural = "BOM Ürünleri"
