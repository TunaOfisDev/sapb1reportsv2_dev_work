# backend/hanaservicelayer/models/models.py

from django.db import models
from django.utils.timezone import now
from .base import BaseModel


class HANADBIntegration(BaseModel):
    """
    HANA DB Entegrasyon süreçlerini yöneten merkezi model.
    - JSON verisi burada saklanmaz, sadece entegrasyon süreçlerini yönetir.
    - Her bağımsız entegrasyon servisi (stok kart, satış siparişi vb.) kendi veri modeline sahip olacak.
    """
    integration_name = models.CharField(max_length=255, unique=True, help_text="Entegrasyon adı")
    integration_type = models.CharField(
        max_length=50,
        choices=[
            ("stock_card", "Stok Kart Entegrasyonu"),
            ("sales_order", "Satış Siparişi Entegrasyonu"),
            ("inventory", "Stok Yönetimi Entegrasyonu"),
        ],
        help_text="Entegrasyon tipi"
    )
    external_api_url = models.URLField(help_text="Bağımsız entegrasyon API adresi")
    hana_status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Bekliyor'), 
            ('processing', 'İşleniyor'), 
            ('completed', 'Tamamlandı'),
            ('failed', 'Başarısız')
        ],
        default='pending',
        help_text="HANA DB ile senkronizasyon durumu"
    )
    last_synced_at = models.DateTimeField(null=True, blank=True, help_text="Son senkronizasyon tarihi")

    def mark_as_synced(self):
        """Başarıyla HANA DB'ye senkronize edildiğinde çağrılır."""
        self.hana_status = "completed"
        self.last_synced_at = now()
        self.save()

    def mark_as_failed(self):
        """HANA DB'ye senkronizasyon başarısız olduğunda çağrılır."""
        self.hana_status = "failed"
        self.save()

    def __str__(self):
        return f"{self.integration_name} - {self.integration_type} - {self.hana_status}"
