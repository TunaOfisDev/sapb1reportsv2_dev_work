# path: backend/nexuscore/models/db_type_mapping.py

from django.db import models

class DBTypeMapping(models.Model):
    """
    Farklı veritabanı türlerinin veri tiplerini genel kategorilere eşleştiren model.
    """
    db_type = models.CharField(max_length=50, help_text="Veritabanı türü (örn: 'sap_hana', 'sql_server')")
    source_type = models.CharField(max_length=255, unique=True, help_text="Veritabanından gelen orijinal tip kodu/adı")
    general_category = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('number', 'Number'),
            ('date', 'Date'),
            ('datetime', 'DateTime'),
            ('other', 'Other')
        ],
        default='other',
        help_text="Eşleşen genel kategori"
    )

    class Meta:
        verbose_name = "Veri Tipi Eşleştirme"
        verbose_name_plural = "Veri Tipi Eşleştirmeleri"
        unique_together = ('db_type', 'source_type')
        ordering = ['db_type', 'source_type']

    def __str__(self):
        return f"{self.db_type}: {self.source_type} -> {self.general_category}"
