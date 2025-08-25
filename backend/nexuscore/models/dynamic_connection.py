# path: /var/www/sapb1reportsv2/backend/nexuscore/models/dynamic_connection.py

from django.db import models
from .fields import EncryptedJSONField # <-- Kendi özel alanımızı import ediyoruz!

class DynamicDBConnection(models.Model):
    """
    Harici veri kaynaklarına ait bağlantı ayarlarını GÜVENLİ bir şekilde saklar.
    Bu model, Nexus Core'un dinamik veri entegrasyon yeteneğinin temel taşıdır.
    """

    class DBType(models.TextChoices):
        POSTGRESQL = 'POSTGRESQL', 'PostgreSQL'
        SQL_SERVER = 'SQL_SERVER', 'Microsoft SQL Server'
        MYSQL = 'MYSQL', 'MySQL'
        ORACLE = 'ORACLE', 'Oracle'
        HANA = 'HANA', 'SAP HANA'
        OTHER = 'OTHER', 'Diğer'

    title = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Bu bağlantıyı tanımlayan benzersiz bir başlık (örn: Üretim SQL Sunucusu)."
    )

    db_type = models.CharField(
        max_length=20,
        choices=DBType.choices,
        default=DBType.OTHER,
        help_text="Veri tabanı türü (örn: PostgreSQL, SQL Server)."
    )
    
    # İşte tamamen bizim kontrolümüzde olan, güvenli ve hatasız alanımız.
    json_config = EncryptedJSONField(
        help_text="Django DATABASES ayarlarıyla uyumlu, şifrelenmiş JSON yapılandırması."
    )

    is_active = models.BooleanField(
        default=False,
        help_text="Sistem genelinde sorgular için varsayılan olarak kullanılacak mı?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dinamik Veri Tabanı Bağlantısı"
        verbose_name_plural = "Dinamik Veri Tabanı Bağlantıları"
        ordering = ['title']

    def __str__(self):
        status = "Aktif" if self.is_active else "Pasif"
        return f"{self.title} ({self.get_db_type_display()} - {status})"