# backend/stockcardintegration/models/models.py

from django.db import models
from .base import BaseModel
from django.utils.timezone import now

# Ürün Grupları (Statik JSON Verileri)
ITEMS_GROUP_DEFAULTS = {
    105: {  # Mamul Ürün
        "ItemType": "itItems",
        "SalesVATGroup": "HES0010",
        "PurchaseVATGroup": "İND010",
        "PurchaseItem": "tNO",
        "SalesItem": "tYES",
        "InventoryItem": "tYES",
        "ManageSerialNumbersOnReleaseOnly": "tNO",
        "SalesUnit": "Ad",
        "PurchaseUnit": "Ad",
        "DefaultWarehouse": "M-01",
        "InventoryUOM": "Ad",
        "PlanningSystem": "M",
        "ProcurementMethod": "M",
        "UoMGroupEntry": 1,
        "InventoryUoMEntry": 1,
        "DefaultSalesUoMEntry": 1,
        "DefaultPurchasingUoMEntry": 1
    },
    103: {  # Ticari Ürün
        "ItemType": "itItems",
        "SalesVATGroup": "HES0010",
        "PurchaseVATGroup": "İND010",
        "PurchaseItem": "tYES",
        "SalesItem": "tYES",
        "InventoryItem": "tYES",
        "ManageSerialNumbersOnReleaseOnly": "tNO",
        "SalesUnit": "Ad",
        "PurchaseUnit": "Ad",
        "DefaultWarehouse": "M-01",
        "InventoryUOM": "Ad",
        "PlanningSystem": "M",
        "ProcurementMethod": "B",
        "UoMGroupEntry": 1,
        "InventoryUoMEntry": 1,
        "DefaultSalesUoMEntry": 1,
        "DefaultPurchasingUoMEntry": 1
    },
    112: {  # Girsberger Ürün
        "ItemType": "itItems",
        "SalesVATGroup": "HES0010",
        "PurchaseVATGroup": "İND010",
        "PurchaseItem": "tYES",
        "SalesItem": "tYES",
        "InventoryItem": "tYES",
        "ManageSerialNumbersOnReleaseOnly": "tNO",
        "SalesUnit": "Ad",
        "PurchaseUnit": "Ad",
        "DefaultWarehouse": "M-01",
        "InventoryUOM": "Ad",
        "PlanningSystem": "M",
        "ProcurementMethod": "B",
        "UoMGroupEntry": 1,
        "InventoryUoMEntry": 1,
        "DefaultSalesUoMEntry": 1,
        "DefaultPurchasingUoMEntry": 1
    }
}


class StockCard(BaseModel):
    """
    Stok Kartı Entegrasyonu için merkezi model.
    """

    item_code = models.CharField(max_length=50, help_text="Stok Kodu (ItemCode)")
    item_name = models.CharField(max_length=200, help_text="Stok Tanımı (ItemName)")
    items_group_code = models.IntegerField(
        choices=[(105, "Mamul"), (103, "Ticari"), (112, "Girsberger")],
        help_text="Ürün Grubu Kodu (ItemsGroupCode)"
    )
    price = models.DecimalField(max_digits=19, decimal_places=4, help_text="Fiyat")
    currency = models.CharField(max_length=10, default="EUR", help_text="Para Birimi")
    extra_data = models.JSONField(default=dict, blank=True, help_text="SAP Payload JSON verisi")
    
    hana_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Bekliyor'),
            ('processing', 'İşleniyor'),
            ('completed', 'Tamamlandı'),
            ('failed', 'Başarısız')
        ],
        default='pending',
        help_text="HANA DB ile Senkronizasyon Durumu"
    )

    last_synced_at = models.DateTimeField(null=True, blank=True, help_text="Son Senkronizasyon Zamanı")

    def save(self, *args, **kwargs):
        """
        StockCard kaydedildiğinde otomatik olarak HANADBIntegration’a gönderilir.
        """
        is_new = self.pk is None  # Yeni bir kayıt mı, güncelleme mi kontrol et
        super().save(*args, **kwargs)

        # Lazy Import burada! Circular Import hatasını engellemek için servisi burada çağırıyoruz.
        from stockcardintegration.services import send_stock_card_to_hanadb, update_stock_card_on_hanadb

        # Yeni bir kayıt oluşturulduğunda veya güncellendiğinde senkronizasyon başlat
        if is_new or self.hana_status == "pending":
            send_stock_card_to_hanadb(self.id)

    def mark_as_synced(self):
        """Başarıyla HANA DB'ye senkronize edildiğinde çağrılır."""
        self.hana_status = "completed"
        self.last_synced_at = now()
        self.save(update_fields=["hana_status", "last_synced_at"])

    def mark_as_failed(self):
        """HANA DB'ye senkronizasyon başarısız olduğunda çağrılır."""
        self.hana_status = "failed"
        self.save(update_fields=["hana_status"])

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"
