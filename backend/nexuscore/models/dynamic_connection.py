# path: backend/nexuscore/models/dynamic_connection.py

from django.db import models
from django.conf import settings
from nexuscore.fields import EncryptedJSONField

class DynamicDBConnection(models.Model):
    """
    Farklı veritabanlarına ait bağlantı bilgilerini güvenli bir şekilde
    saklayan model.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='db_connections',
        verbose_name="Sahip",
        null=True,  # Migration'ların sorunsuz çalışması için
        blank=True
    )
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Bağlantı Başlığı"
    )
    db_type = models.CharField(
        max_length=50,
        verbose_name="Veritabanı Türü",
        help_text="Örn: postgresql, sql_server, sap_hana"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif mi?",
        db_index=True,
        help_text="Bu bağlantının sorgularda kullanılıp kullanılamayacağını belirtir."
    )
    config_json = EncryptedJSONField(
        verbose_name="Bağlantı Yapılandırması (Şifreli JSON)",
        default=dict,
        help_text="Hassas bağlantı bilgileri (şifre, host vb.) bu alanda şifrelenerek saklanır."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Dinamik Veritabanı Bağlantısı"
        verbose_name_plural = "Dinamik Veritabanı Bağlantıları"
        ordering = ['-updated_at']