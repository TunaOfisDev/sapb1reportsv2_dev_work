# path: backend/nexuscore/models/report_template.py

from django.db import models
from django.conf import settings
from .virtual_table import VirtualTable, SharingStatus

class ReportTemplate(models.Model):
    """
    Kullanıcıların 'Playground'da oluşturduğu, VirtualTable verilerini
    görselleştiren özel rapor şablonlarını saklar.
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Rapor Başlığı"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Açıklama"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Sahibi silinse bile rapor kalabilir
        null=True,
        related_name='report_templates',
        verbose_name="Sahip"
    )
    # Bu raporun hangi ham veri kaynağını kullandığını belirten kritik bağlantı.
    source_virtual_table = models.ForeignKey(
        VirtualTable,
        on_delete=models.CASCADE, # Eğer kaynak sorgu silinirse, bu rapor da silinmeli.
        related_name='report_templates',
        verbose_name="Kaynak Sanal Tablo"
    )
    # Kullanıcının sürükle-bırak ile oluşturduğu tüm ayarlar burada saklanacak.
    configuration_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Rapor Yapılandırması (JSON)",
        help_text="Kolon sırası, görünürlüğü, filtreler vb. ayarları içerir."
    )
    sharing_status = models.CharField(
        max_length=20,
        choices=SharingStatus.choices,
        default=SharingStatus.PRIVATE,
        verbose_name="Paylaşım Durumu"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Rapor Şablonu"
        verbose_name_plural = "Rapor Şablonları"
        ordering = ['-updated_at']