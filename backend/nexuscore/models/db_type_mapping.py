# path: backend/nexuscore/models/db_type_mapping.py
from django.db import models

class DBTypeMapping(models.Model):
    """
    Farklı veritabanı türlerinin veri tiplerini genel kategorilere eşleştiren model.
    Bu model, sistemin zamanla yeni veri tiplerini öğrenmesini sağlar.
    """
    # GÜÇLENDİRME: Kategorileri daha anlamlı hale getiriyoruz.
    GENERAL_CATEGORIES = (
        ('string', 'Metin (String)'),
        ('integer', 'Tamsayı (Integer)'),
        ('decimal', 'Ondalıklı Sayı (Decimal)'),
        ('date', 'Tarih (Date)'),
        ('datetime', 'Tarih ve Zaman (DateTime)'),
        ('boolean', 'Mantıksal (Boolean)'),
        ('json', 'JSON'),
        ('other', 'Diğer/Bilinmeyen'), # <-- Bilinmeyenler için bir sığınak
    )

    db_type = models.CharField(
        max_length=50, 
        help_text="Veritabanı türü (örn: 'sap_hana', 'sql_server')"
    )
    # DEĞİŞİKLİK: source_type_code yerine source_type kullanıyoruz (mevcut modelinle uyumlu)
    source_type = models.CharField(
        max_length=255, 
        help_text="Veritabanından gelen orijinal tip kodu/adı (örn: 'NVARCHAR', '1043')"
    )
    general_category = models.CharField(
        max_length=20,
        choices=GENERAL_CATEGORIES,
        default='other',
        help_text="Eşleşen genel kategori"
    )

    class Meta:
        verbose_name = "Veri Tipi Eşleştirme"
        verbose_name_plural = "Veri Tipi Eşleştirmeleri"
        # Bu kısıtlama, her veritabanı için her tipin sadece bir kez tanımlanmasını sağlar.
        unique_together = ('db_type', 'source_type')
        ordering = ['db_type', 'source_type']

    def __str__(self):
        return f"{self.db_type}: {self.source_type} -> {self.general_category}"