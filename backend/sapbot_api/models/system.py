
# backend/sapbot_api/models/system.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel, TimestampedModel
import json


class SystemConfiguration(BaseModel):
    """Sistem konfigürasyon modeli"""
    
    CONFIG_TYPE_CHOICES = [
        ('string', 'Metin'),
        ('integer', 'Sayı'),
        ('float', 'Ondalık'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('list', 'Liste'),
    ]
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Anahtar'
    )
    value = models.TextField(
        verbose_name='Değer'
    )
    config_type = models.CharField(
        max_length=20,
        choices=CONFIG_TYPE_CHOICES,
        default='string',
        verbose_name='Veri Tipi'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Açıklama'
    )
    is_sensitive = models.BooleanField(
        default=False,
        verbose_name='Hassas Veri mi?'
    )
    is_editable = models.BooleanField(
        default=True,
        verbose_name='Düzenlenebilir mi?'
    )
    category = models.CharField(
        max_length=50,
        default='general',
        verbose_name='Kategori'
    )
    default_value = models.TextField(
        null=True,
        blank=True,
        verbose_name='Varsayılan Değer'
    )
    validation_regex = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Doğrulama Regex'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Güncelleyen'
    )
    
    class Meta:
        db_table = 'sapbot_system_configurations'
        verbose_name = 'Sistem Konfigürasyonu'
        verbose_name_plural = 'Sistem Konfigürasyonları'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_editable']),
        ]
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    def get_typed_value(self):
        """Tipine göre değer döndür"""
        if self.config_type == 'integer':
            return int(self.value)
        elif self.config_type == 'float':
            return float(self.value)
        elif self.config_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes', 'on']
        elif self.config_type == 'json':
            return json.loads(self.value)
        elif self.config_type == 'list':
            return json.loads(self.value) if self.value else []
        return self.value
    
    def set_typed_value(self, value):
        """Tipine göre değer ata"""
        if self.config_type in ['json', 'list']:
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = str(value)


class SystemMetrics(TimestampedModel):
    """Sistem metrik modeli"""
    
    METRIC_TYPE_CHOICES = [
        ('counter', 'Sayaç'),
        ('gauge', 'Gösterge'),
        ('histogram', 'Histogram'),
        ('summary', 'Özet'),
    ]
    
    metric_name = models.CharField(
        max_length=100,
        verbose_name='Metrik Adı'
    )
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPE_CHOICES,
        default='counter',
        verbose_name='Metrik Tipi'
    )
    value = models.FloatField(
        verbose_name='Değer'
    )
    labels = JSONField(
        default=dict,
        blank=True,
        verbose_name='Etiketler'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Zaman Damgası'
    )
    
    class Meta:
        db_table = 'sapbot_system_metrics'
        verbose_name = 'Sistem Metriği'
        verbose_name_plural = 'Sistem Metrikleri'
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
            models.Index(fields=['metric_type']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.value}"


class SystemLog(TimestampedModel):
    """Sistem log modeli"""
    
    LOG_LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(
        max_length=20,
        choices=LOG_LEVEL_CHOICES,
        default='INFO',
        verbose_name='Log Seviyesi'
    )
    message = models.TextField(
        verbose_name='Mesaj'
    )
    module = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Modül'
    )
    function = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Fonksiyon'
    )
    line_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Satır Numarası'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Kullanıcı'
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Oturum ID'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Adresi'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='Tarayıcı Bilgisi'
    )
    extra_data = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Veriler'
    )
    
    class Meta:
        db_table = 'sapbot_system_logs'
        verbose_name = 'Sistem Log'
        verbose_name_plural = 'Sistem Logları'
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['module']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.level} - {self.message[:50]}..."


class SystemHealth(TimestampedModel):
    """Sistem sağlık durumu modeli"""
    
    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Sağlıklı'),
        ('warning', 'Uyarı'),
        ('critical', 'Kritik'),
        ('down', 'Çalışmıyor'),
    ]
    
    component = models.CharField(
        max_length=50,
        verbose_name='Bileşen'
    )
    status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        verbose_name='Durum'
    )
    response_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Yanıt Süresi (ms)'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Hata Mesajı'
    )
    details = JSONField(
        default=dict,
        blank=True,
        verbose_name='Detaylar'
    )
    
    class Meta:
        db_table = 'sapbot_system_health'
        verbose_name = 'Sistem Sağlığı'
        verbose_name_plural = 'Sistem Sağlık Durumları'
        indexes = [
            models.Index(fields=['component', 'created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.component} - {self.status}"


class APIQuota(BaseModel):
    """API kota modeli"""
    
    QUOTA_TYPE_CHOICES = [
        ('daily', 'Günlük'),
        ('monthly', 'Aylık'),
        ('hourly', 'Saatlik'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Kullanıcı'
    )
    api_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='API Anahtarı'
    )
    endpoint = models.CharField(
        max_length=200,
        verbose_name='Endpoint'
    )
    quota_type = models.CharField(
        max_length=20,
        choices=QUOTA_TYPE_CHOICES,
        default='daily',
        verbose_name='Kota Tipi'
    )
    limit_count = models.IntegerField(
        verbose_name='Limit Sayısı'
    )
    current_count = models.IntegerField(
        default=0,
        verbose_name='Mevcut Kullanım'
    )
    reset_at = models.DateTimeField(
        verbose_name='Sıfırlama Zamanı'
    )
    
    class Meta:
        db_table = 'sapbot_api_quotas'
        verbose_name = 'API Kotası'
        verbose_name_plural = 'API Kotaları'
        indexes = [
            models.Index(fields=['user', 'endpoint']),
            models.Index(fields=['reset_at']),
        ]
    
    def __str__(self):
        return f"{self.endpoint} - {self.current_count}/{self.limit_count}"
    
    @property
    def is_exceeded(self):
        """Kota aşıldı mı?"""
        return self.current_count >= self.limit_count
    
    @property
    def usage_percentage(self):
        """Kullanım yüzdesi"""
        return (self.current_count / self.limit_count) * 100 if self.limit_count > 0 else 0


class SystemNotification(BaseModel):
    """Sistem bildirimi modeli"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Bilgi'),
        ('warning', 'Uyarı'),
        ('error', 'Hata'),
        ('success', 'Başarı'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Düşük'),
        (2, 'Normal'),
        (3, 'Yüksek'),
        (4, 'Kritik'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Başlık'
    )
    message = models.TextField(
        verbose_name='Mesaj'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='info',
        verbose_name='Bildirim Tipi'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name='Öncelik'
    )
    target_users = models.ManyToManyField(
        User,
        blank=True,
        verbose_name='Hedef Kullanıcılar'
    )
    is_system_wide = models.BooleanField(
        default=False,
        verbose_name='Sistem Geneli mi?'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Okundu mu?'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Sona Erme Tarihi'
    )
    action_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='Eylem URL'
    )
    action_text = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Eylem Metni'
    )
    
    class Meta:
        db_table = 'sapbot_system_notifications'
        verbose_name = 'Sistem Bildirimi'
        verbose_name_plural = 'Sistem Bildirimleri'
        indexes = [
            models.Index(fields=['is_system_wide', 'is_read']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"
    
    @property
    def is_expired(self):
        """Süresi dolmuş mu?"""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()


class MaintenanceWindow(BaseModel):
    """Bakım penceresi modeli"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Planlandı'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Başlık'
    )
    description = models.TextField(
        verbose_name='Açıklama'
    )
    start_time = models.DateTimeField(
        verbose_name='Başlangıç Zamanı'
    )
    end_time = models.DateTimeField(
        verbose_name='Bitiş Zamanı'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Durum'
    )
    affects_api = models.BooleanField(
        default=True,
        verbose_name='API\'yi Etkiler mi?'
    )
    affects_chat = models.BooleanField(
        default=True,
        verbose_name='Chat\'i Etkiler mi?'
    )
    affects_upload = models.BooleanField(
        default=False,
        verbose_name='Upload\'ı Etkiler mi?'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Oluşturan'
    )
    
    class Meta:
        db_table = 'sapbot_maintenance_windows'
        verbose_name = 'Bakım Penceresi'
        verbose_name_plural = 'Bakım Pencereleri'
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_active(self):
        """Şu anda aktif mi?"""
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'in_progress'
    
    @property
    def duration_minutes(self):
        """Süre (dakika)"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0