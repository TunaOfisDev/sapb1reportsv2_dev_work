# path: backend/nexuscore/models/app_relationship.py

from django.db import models
from .data_app import DataApp
from .virtual_table import VirtualTable

class JoinType(models.TextChoices):
    """Destekleyeceğimiz SQL JOIN türleri."""
    INNER = 'INNER JOIN', 'İç Birleştirme (INNER JOIN)'
    LEFT = 'LEFT JOIN', 'Sol Birleştirme (LEFT JOIN)'
    # RIGHT ve FULL şimdilik eklemeyelim, karmaşıklığı artırır.


class AppRelationship(models.Model):
    """
    Bir DataApp içindeki iki VirtualTable arasındaki JOIN ilişkisini tanımlar.
    """
    app = models.ForeignKey(
        DataApp,
        on_delete=models.CASCADE,
        related_name='relationships',
        verbose_name="Ait Olduğu Uygulama"
    )
    
    # "Soldaki Tablo" (Örn: Satiş İşlemleri)
    left_table = models.ForeignKey(
        VirtualTable,
        on_delete=models.CASCADE,
        related_name='left_relations',
        verbose_name="Sol Tablo"
    )
    left_column = models.CharField(
        max_length=255,
        verbose_name="Sol Tablo Kolonu",
        help_text="JOIN için kullanılacak kolon adı (Örn: MusteriID)"
    )
    
    # "Sağdaki Tablo" (Örn: Müşteri Ana Verisi)
    right_table = models.ForeignKey(
        VirtualTable,
        on_delete=models.CASCADE,
        related_name='right_relations',
        verbose_name="Sağ Tablo"
    )
    right_column = models.CharField(
        max_length=255,
        verbose_name="Sağ Tablo Kolonu",
        help_text="JOIN için kullanılacak kolon adı (Örn: ID)"
    )
    
    join_type = models.CharField(
        max_length=20,
        choices=JoinType.choices,
        default=JoinType.LEFT,
        verbose_name="Birleştirme Türü"
    )

    class Meta:
        verbose_name = "Uygulama İlişkisi"
        verbose_name_plural = "Uygulama İlişkileri"
        ordering = ['app']

    def __str__(self):
        return f"{self.left_table.title}.{self.left_column} {self.join_type} {self.right_table.title}.{self.right_column}"