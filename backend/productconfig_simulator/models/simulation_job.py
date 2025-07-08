# backend/productconfig_simulator/models/simulation_job.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# from django.contrib.postgres.fields import JSONField  # Bu satırı kaldırın
from django.db.models import JSONField  # Bunun yerine bunu kullanın
from django.conf import settings

from .base import SimulatorBaseModel
from productconfig.models import Brand, ProductGroup, Category, ProductModel

class SimulationJob(SimulatorBaseModel):
    """
    Simülasyon işlerini takip eden model. Her simülasyon için bir kayıt oluşturulur.
    """
    class SimulationLevel(models.TextChoices):
        BRAND = 'brand', _('Marka Seviyesi')
        PRODUCT_GROUP = 'product_group', _('Ürün Grubu Seviyesi')
        CATEGORY = 'category', _('Kategori Seviyesi')
        PRODUCT_MODEL = 'product_model', _('Ürün Modeli Seviyesi')

    class SimulationStatus(models.TextChoices):
        PENDING = 'pending', _('Bekliyor')
        RUNNING = 'running', _('Çalışıyor')
        COMPLETED = 'completed', _('Tamamlandı')
        FAILED = 'failed', _('Başarısız')
        CANCELLED = 'cancelled', _('İptal Edildi')

    name = models.CharField(
        max_length=255, 
        verbose_name=_("Simülasyon Adı")
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_("Açıklama")
    )
    
    level = models.CharField(
        max_length=20,
        choices=SimulationLevel.choices,
        default=SimulationLevel.PRODUCT_MODEL,
        verbose_name=_("Simülasyon Seviyesi")
    )
    
    status = models.CharField(
        max_length=20,
        choices=SimulationStatus.choices,
        default=SimulationStatus.PENDING,
        verbose_name=_("Durum")
    )
    
    # Simülasyon hedefleri (level'e göre doldurulur)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='simulations',
        verbose_name=_("Marka")
    )
    
    product_group = models.ForeignKey(
        ProductGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='simulations',
        verbose_name=_("Ürün Grubu")
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='simulations',
        verbose_name=_("Kategori")
    )
    
    product_model = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='simulations',
        verbose_name=_("Ürün Modeli")
    )
    
    # Simülasyon konfigürasyonu
    max_variants_per_model = models.PositiveIntegerField(
        default=1000,
        verbose_name=_("Model Başına Maksimum Varyant"),
        help_text=_("Bir model için oluşturulacak maksimum varyant sayısı")
    )
    
    include_dependent_rules = models.BooleanField(
        default=True,
        verbose_name=_("Bağımlı Kuralları Dahil Et"),
        help_text=_("Bağımlı kuralları simülasyona dahil et")
    )
    
    include_conditional_options = models.BooleanField(
        default=True,
        verbose_name=_("Koşullu Seçenekleri Dahil Et"),
        help_text=_("Koşullu seçenekleri simülasyona dahil et")
    )
    
    include_price_multipliers = models.BooleanField(
        default=True,
        verbose_name=_("Fiyat Çarpanlarını Dahil Et"),
        help_text=_("Fiyat çarpanlarını simülasyona dahil et")
    )
    
    # Simülasyon sonuçları
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Başlangıç Zamanı")
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Bitiş Zamanı")
    )
    
    total_models = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Toplam Model Sayısı")
    )
    
    processed_models = models.PositiveIntegerField(
        default=0,
        verbose_name=_("İşlenen Model Sayısı")
    )
    
    total_variants = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Toplam Varyant Sayısı")
    )
    
    total_errors = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Toplam Hata Sayısı")
    )
    
    celery_task_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Celery Task ID")
    )
    
    result_summary = JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Sonuç Özeti")
    )
    
    # İlişkiler
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='simulations',
        verbose_name=_("Oluşturan Kullanıcı")
    )
    
    class Meta:
        verbose_name = _("Simülasyon İşi")
        verbose_name_plural = _("Simülasyon İşleri")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['level']),
            models.Index(fields=['brand']),
            models.Index(fields=['product_group']),
            models.Index(fields=['category']),
            models.Index(fields=['product_model']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def start(self):
        """Simülasyonu başlatır"""
        self.status = self.SimulationStatus.RUNNING
        self.start_time = timezone.now()
        self.save()
    
    def complete(self):
        """Simülasyonu tamamlanmış olarak işaretler"""
        self.status = self.SimulationStatus.COMPLETED
        self.end_time = timezone.now()
        self.save()
    
    def fail(self, error_message=None):
        """Simülasyonu başarısız olarak işaretler"""
        self.status = self.SimulationStatus.FAILED
        self.end_time = timezone.now()
        if error_message:
            summary = self.result_summary or {}
            summary['error_message'] = error_message
            self.result_summary = summary
        self.save()
    
    def cancel(self):
        """Simülasyonu iptal eder"""
        self.status = self.SimulationStatus.CANCELLED
        self.end_time = timezone.now()
        self.save()
    
    def update_progress(self, processed_models, total_variants, total_errors):
        """Simülasyon ilerleme durumunu günceller"""
        self.processed_models = processed_models
        self.total_variants = total_variants
        self.total_errors = total_errors
        self.save()
    
    @property
    def duration(self):
        """Simülasyonun süresini döndürür"""
        if not self.start_time:
            return None
            
        end = self.end_time or timezone.now()
        return end - self.start_time
    
    @property
    def progress_percentage(self):
        """Simülasyonun ilerleme yüzdesini döndürür"""
        if not self.total_models or self.total_models == 0:
            return 0
        return int((self.processed_models / self.total_models) * 100)