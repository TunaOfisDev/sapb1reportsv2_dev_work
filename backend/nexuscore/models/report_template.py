# path: backend/nexuscore/models/report_template.py

from django.db import models
from django.conf import settings
from .data_app import DataApp  # <-- Doğru import
from .virtual_table import SharingStatus 

class ReportTemplate(models.Model):
    """
    Kullanıcıların 'Playground'da oluşturduğu, artık tek bir tabloyu değil,
    bütün bir 'DataApp' veri modelini görselleştiren rapor şablonları.
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
        on_delete=models.SET_NULL, 
        null=True,
        related_name='report_templates',
        verbose_name="Sahip"
    )

    # ### MİMARİ DEĞİŞİKLİK VE HATA DÜZELTMESİ BURADA ###
    
    source_data_app = models.ForeignKey(
        DataApp,
        # CASCADE yerine SET_NULL kullanmak çok daha güvenlidir.
        # Bir Veri Uygulaması silinirse, ona bağlı raporlar silinmez,
        # sadece bağlantıları boşa düşer (NULL olur). Bu sayede veri kaybetmeyiz.
        on_delete=models.SET_NULL, 
        related_name='report_templates',
        verbose_name="Kaynak Veri Uygulaması",
        help_text="Bu raporun veri çektiği ana veri modeli.",
        
        # HATA DÜZELTMESİ: Veritabanı geçişinin başarılı olması için 
        # bu alanın geçici olarak NULL olmasına izin vermeliyiz.
        null=True,
        blank=True 
    )
    
    # Eski alan (source_virtual_table) model tanımından tamamen kaldırıldı.
    # makemigrations bunu algılayacak.

    configuration_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Rapor Yapılandırması (JSON)",
        help_text="Pivot ayarları, filtreler vb. ayarları içerir."
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