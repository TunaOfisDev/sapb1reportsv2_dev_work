# path: /var/www/sapb1reportsv2/backend/nexuscore/models/virtual_table.py

from django.db import models
from django.conf import settings
from .dynamic_connection import DynamicDBConnection

class SharingStatus(models.TextChoices):
    """Bu sanal tablonun görünürlük ve düzenleme izinlerini tanımlar."""
    PRIVATE = 'PRIVATE', 'Özel (Sadece Sahibi Görebilir)'
    PUBLIC_READONLY = 'PUBLIC_READONLY', 'Halka Açık (Sadece Görüntülenebilir)'
    PUBLIC_EDITABLE = 'PUBLIC_EDITABLE', 'Halka Açık (Herkes Düzenleyebilir)'


class VirtualTable(models.Model):
    """
    Kullanıcıların kendi SQL sorgularını kullanarak oluşturduğu sanal veri tablolarını
    ve bu tabloların meta verilerini saklar.
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Başlık",
        help_text="Sanal tabloya verilen, kolay hatırlanabilir isim."
    )
    connection = models.ForeignKey(
        DynamicDBConnection,
        on_delete=models.CASCADE,
        related_name="virtual_tables",
        verbose_name="Veri Kaynağı Bağlantısı",
        help_text="Bu sanal tablonun sorguyu çalıştıracağı veri kaynağı."
    )
    sql_query = models.TextField(
        verbose_name="SQL Sorgusu",
        help_text="Çalıştırılacak olan SELECT veya WITH ile başlayan SQL sorgusu."
    )
    column_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Sütun Meta Verisi",
        help_text='Sütunların görünürlüğü gibi UI ayarlarını saklar.'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="virtual_tables",
        verbose_name="Sahip",
        help_text="Bu sanal tabloyu oluşturan veya sahibi olan kullanıcı."
    )
    sharing_status = models.CharField(
        max_length=20,
        choices=SharingStatus.choices,
        default=SharingStatus.PRIVATE,
        verbose_name="Paylaşım Durumu",
        help_text="Bu sanal tablonun diğer kullanıcılar için görünürlük ayarı."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Sanal Tablo"
        verbose_name_plural = "Sanal Tablolar"
        unique_together = ('owner', 'connection', 'title')
        ordering = ['-updated_at']

    def __str__(self):
        # ### NİHAİ DÜZELTME: `owner.username` yerine `owner.email` kullanıyoruz ###
        owner_identity = self.owner.email if self.owner else "Yok"
        return f'"{self.title}" (Sahip: {owner_identity})'