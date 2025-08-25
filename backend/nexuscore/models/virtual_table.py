# path: /var/www/sapb1reportsv2/backend/nexuscore/models/virtual_table.py

from django.db import models
from django.conf import settings
from .dynamic_connection import DynamicDBConnection

# --- DÜZELTME BURADA ---
# SharingStatus sınıfını, VirtualTable'ın DIŞINA, modül seviyesine taşıyoruz.
# Artık bağımsız ve her yerden kolayca import edilebilir bir bileşen.
class SharingStatus(models.TextChoices):
    """Bu sanal tablonun görünürlük ve düzenleme izinlerini tanımlar."""
    PRIVATE = 'PRIVATE', 'Özel (Sadece Sahibi Görebilir)'
    PUBLIC_READONLY = 'PUBLIC_READONLY', 'Halka Açık (Sadece Görüntülenebilir)'
    PUBLIC_EDITABLE = 'PUBLIC_EDITABLE', 'Halka Açık (Herkes Düzenleyebilir)'


class VirtualTable(models.Model):
    """
    Kullanıcıların kendi SQL sorgularını kullanarak oluşturduğu sanal veri tablolarını
    ve bu tabloların meta verilerini (örn: kolon görünürlüğü, sahiplik, paylaşım durumu) saklar.
    Bu, Nexus Core'un iş birliği ve analiz katmanıdır.
    """
    # ... (diğer alanlar title, connection, sql_query, column_metadata, owner aynı kalıyor) ...
    title = models.CharField(max_length=255, help_text="...")
    connection = models.ForeignKey(DynamicDBConnection, on_delete=models.CASCADE, related_name="virtual_tables", help_text="...")
    sql_query = models.TextField(help_text="...")
    column_metadata = models.JSONField(default=dict, blank=True, help_text='...')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="virtual_tables", help_text="...")
    
    # sharing_status alanı artık dışarıda tanımladığımız SharingStatus sınıfını kullanıyor.
    sharing_status = models.CharField(
        max_length=20,
        choices=SharingStatus.choices,
        default=SharingStatus.PRIVATE,
        help_text="Bu sanal tablonun diğer kullanıcılar için görünürlük ve düzenleme ayarı."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sanal Tablo"
        verbose_name_plural = "Sanal Tablolar"
        unique_together = ('owner', 'connection', 'title')
        ordering = ['-updated_at']

    def __str__(self):
        owner_username = self.owner.username if self.owner else "Yok"
        return f'"{self.title}" (Sahip: {owner_username})'