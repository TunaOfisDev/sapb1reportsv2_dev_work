# backend/sapbot_api/models/analytics.py
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel, TimestampedModel
from datetime import timedelta

User = get_user_model()


class QueryAnalytics(BaseModel):
    """Sorgu analitik modeli"""
    
    USER_TYPE_CHOICES = [
        ('user', 'Son Kullanıcı'),
        ('technical', 'Teknik Kullanıcı'),
        ('admin', 'Yönetici'),
        ('anonymous', 'Anonim'),
    ]
    
    INTENT_CHOICES = [
        ('error_solving', 'Hata Çözme'),
        ('configuration', 'Yapılandırma'),
        ('how_to', 'Nasıl Yapılır'),
        ('explanation', 'Açıklama'),
        ('reporting', 'Raporlama'),
        ('troubleshooting', 'Sorun Giderme'),
        ('feature_request', 'Özellik İsteği'),
        ('general', 'Genel'),
    ]
    
    SAP_MODULE_CHOICES = [
        ('FI', 'Mali Muhasebe'),
        ('MM', 'Malzeme Yönetimi'),
        ('SD', 'Satış ve Dağıtım'),
        ('PP', 'Üretim Planlama'),
        ('HR', 'İnsan Kaynakları'),
        ('QM', 'Kalite Yönetimi'),
        ('PM', 'Tesis Bakımı'),
        ('CO', 'Maliyet Kontrolü'),
        ('WM', 'Depo Yönetimi'),
        ('CRM', 'Müşteri İlişkileri'),
        ('BI', 'Business Intelligence'),
        ('ADMIN', 'Sistem Yönetimi'),
        ('OTHER', 'Diğer'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sapbot_queries',
        verbose_name='Kullanıcı'
    )
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Oturum ID'
    )
    query = models.TextField(
        verbose_name='Sorgu'
    )
    query_hash = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name='Sorgu Hash'
    )
    query_length = models.IntegerField(
        verbose_name='Sorgu Uzunluğu'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        verbose_name='Kullanıcı Tipi'
    )
    sap_module_detected = models.CharField(
        max_length=10,
        choices=SAP_MODULE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Tespit Edilen SAP Modülü'
    )
    intent_detected = models.CharField(
        max_length=50,
        choices=INTENT_CHOICES,
        null=True,
        blank=True,
        verbose_name='Tespit Edilen Niyet'
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Güven Skoru'
    )
    response_generated = models.BooleanField(
        default=False,
        verbose_name='Yanıt Oluşturuldu mu?'
    )
    response_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Yanıt Süresi (saniye)'
    )
    sources_used_count = models.IntegerField(
        default=0,
        verbose_name='Kullanılan Kaynak Sayısı'
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Kullanılan Token Sayısı'
    )
    cost_estimate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name='Tahmini Maliyet'
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
    language_detected = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='Tespit Edilen Dil'
    )
    error_occurred = models.BooleanField(
        default=False,
        verbose_name='Hata Oluştu mu?'
    )
    error_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Hata Tipi'
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    
    class Meta:
        db_table = 'sapbot_query_analytics'
        verbose_name = 'Sorgu Analitiği'
        verbose_name_plural = 'Sorgu Analitikleri'
        indexes = [
            models.Index(fields=['query_hash']),
            models.Index(fields=['sap_module_detected']),
            models.Index(fields=['intent_detected']),
            models.Index(fields=['user_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['response_generated']),
        ]
    
    def __str__(self):
        return f"Query - {self.query[:50]}... ({self.user_type})"
    
    def generate_query_hash(self):
        """Sorgu hash'i oluştur"""
        import hashlib
        return hashlib.sha256(self.query.encode('utf-8')).hexdigest()
    
    def save(self, *args, **kwargs):
        """Kaydetme sırasında hash ve uzunluk hesapla"""
        if not self.query_hash:
            self.query_hash = self.generate_query_hash()
        self.query_length = len(self.query)
        super().save(*args, **kwargs)


class UserFeedback(BaseModel):
    """Kullanıcı geri bildirim modeli"""
    
    FEEDBACK_TYPE_CHOICES = [
        ('rating', 'Puan'),
        ('comment', 'Yorum'),
        ('bug_report', 'Hata Bildirimi'),
        ('feature_request', 'Özellik İsteği'),
        ('general', 'Genel'),
    ]
    
    RATING_CHOICES = [
        (1, 'Çok Kötü'),
        (2, 'Kötü'),
        (3, 'Orta'),
        (4, 'İyi'),
        (5, 'Mükemmel'),
    ]
    
    SATISFACTION_CHOICES = [
        ('very_dissatisfied', 'Çok Memnun Değil'),
        ('dissatisfied', 'Memnun Değil'),
        ('neutral', 'Nötr'),
        ('satisfied', 'Memnun'),
        ('very_satisfied', 'Çok Memnun'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sapbot_feedback',
        verbose_name='Kullanıcı'
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Oturum ID'
    )
    message = models.ForeignKey(
        'sapbot_api.ChatMessage',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedback_records',
        verbose_name='İlgili Mesaj'
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        verbose_name='Geri Bildirim Tipi'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='Puan'
    )
    satisfaction = models.CharField(
        max_length=20,
        choices=SATISFACTION_CHOICES,
        null=True,
        blank=True,
        verbose_name='Memnuniyet'
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name='Yorum'
    )
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='Faydalı mı?'
    )
    improvement_suggestions = models.TextField(
        null=True,
        blank=True,
        verbose_name='İyileştirme Önerileri'
    )
    contact_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='İletişim Email'
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
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    is_processed = models.BooleanField(
        default=False,
        verbose_name='İşlendi mi?'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='İşlenme Tarihi'
    )
    response_sent = models.BooleanField(
        default=False,
        verbose_name='Yanıt Gönderildi mi?'
    )
    
    class Meta:
        db_table = 'sapbot_user_feedback'
        verbose_name = 'Kullanıcı Geri Bildirimi'
        verbose_name_plural = 'Kullanıcı Geri Bildirimleri'
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Feedback - {self.get_feedback_type_display()} - {self.rating or 'N/A'}"


class UsageStatistics(BaseModel):
    """Kullanım istatistik modeli"""
    
    METRIC_TYPE_CHOICES = [
        ('daily', 'Günlük'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('yearly', 'Yıllık'),
    ]
    
    date = models.DateField(
        verbose_name='Tarih'
    )
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPE_CHOICES,
        verbose_name='Metrik Tipi'
    )
    total_queries = models.IntegerField(
        default=0,
        verbose_name='Toplam Sorgu'
    )
    successful_queries = models.IntegerField(
        default=0,
        verbose_name='Başarılı Sorgu'
    )
    failed_queries = models.IntegerField(
        default=0,
        verbose_name='Başarısız Sorgu'
    )
    unique_users = models.IntegerField(
        default=0,
        verbose_name='Benzersiz Kullanıcı'
    )
    unique_sessions = models.IntegerField(
        default=0,
        verbose_name='Benzersiz Oturum'
    )
    avg_response_time = models.FloatField(
        default=0.0,
        verbose_name='Ortalama Yanıt Süresi'
    )
    avg_satisfaction = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Ortalama Memnuniyet'
    )
    total_tokens_used = models.IntegerField(
        default=0,
        verbose_name='Toplam Kullanılan Token'
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0.0000,
        verbose_name='Toplam Maliyet'
    )
    documents_processed = models.IntegerField(
        default=0,
        verbose_name='İşlenen Döküman'
    )
    chunks_created = models.IntegerField(
        default=0,
        verbose_name='Oluşturulan Chunk'
    )
    top_sap_modules = JSONField(
        default=list,
        blank=True,
        verbose_name='En Çok Kullanılan SAP Modülleri'
    )
    top_intents = JSONField(
        default=list,
        blank=True,
        verbose_name='En Çok Kullanılan Niyetler'
    )
    error_breakdown = JSONField(
        default=dict,
        blank=True,
        verbose_name='Hata Dağılımı'
    )
    
    class Meta:
        db_table = 'sapbot_usage_statistics'
        verbose_name = 'Kullanım İstatistiği'
        verbose_name_plural = 'Kullanım İstatistikleri'
        unique_together = ['date', 'metric_type']
        indexes = [
            models.Index(fields=['date', 'metric_type']),
            models.Index(fields=['metric_type']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.get_metric_type_display()}"
    
    @property
    def success_rate(self):
        """Başarı oranı"""
        if self.total_queries > 0:
            return (self.successful_queries / self.total_queries) * 100
        return 0
    
    @property
    def avg_queries_per_user(self):
        """Kullanıcı başına ortalama sorgu"""
        if self.unique_users > 0:
            return self.total_queries / self.unique_users
        return 0


class PerformanceMetrics(TimestampedModel):
    """Performans metrik modeli"""
    
    COMPONENT_CHOICES = [
        ('api', 'API'),
        ('chat', 'Chat'),
        ('embedding', 'Embedding'),
        ('search', 'Arama'),
        ('document_processing', 'Döküman İşleme'),
        ('database', 'Veritabanı'),
        ('cache', 'Cache'),
        ('external_api', 'Harici API'),
    ]
    
    component = models.CharField(
        max_length=50,
        choices=COMPONENT_CHOICES,
        verbose_name='Bileşen'
    )
    metric_name = models.CharField(
        max_length=100,
        verbose_name='Metrik Adı'
    )
    value = models.FloatField(
        verbose_name='Değer'
    )
    unit = models.CharField(
        max_length=20,
        verbose_name='Birim'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Zaman Damgası'
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    
    class Meta:
        db_table = 'sapbot_performance_metrics'
        verbose_name = 'Performans Metriği'
        verbose_name_plural = 'Performans Metrikleri'
        indexes = [
            models.Index(fields=['component', 'metric_name']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.component} - {self.metric_name}: {self.value} {self.unit}"


class ErrorLog(BaseModel):
    """Hata log modeli"""
    
    ERROR_LEVEL_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Kritik'),
    ]
    
    ERROR_TYPE_CHOICES = [
        ('api_error', 'API Hatası'),
        ('database_error', 'Veritabanı Hatası'),
        ('processing_error', 'İşleme Hatası'),
        ('external_api_error', 'Harici API Hatası'),
        ('validation_error', 'Doğrulama Hatası'),
        ('authentication_error', 'Kimlik Doğrulama Hatası'),
        ('permission_error', 'Yetki Hatası'),
        ('system_error', 'Sistem Hatası'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sapbot_errors',
        verbose_name='Kullanıcı'
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Oturum ID'
    )
    error_type = models.CharField(
        max_length=50,
        choices=ERROR_TYPE_CHOICES,
        verbose_name='Hata Tipi'
    )
    error_level = models.CharField(
        max_length=20,
        choices=ERROR_LEVEL_CHOICES,
        verbose_name='Hata Seviyesi'
    )
    error_message = models.TextField(
        verbose_name='Hata Mesajı'
    )
    stack_trace = models.TextField(
        null=True,
        blank=True,
        verbose_name='Stack Trace'
    )
    component = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Bileşen'
    )
    function_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Fonksiyon Adı'
    )
    line_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Satır Numarası'
    )
    request_data = JSONField(
        default=dict,
        blank=True,
        verbose_name='İstek Verisi'
    )
    context = JSONField(
        default=dict,
        blank=True,
        verbose_name='Bağlam'
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
    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Çözüldü mü?'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Çözülme Tarihi'
    )
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Çözüm Notları'
    )
    
    class Meta:
        db_table = 'sapbot_error_logs'
        verbose_name = 'Hata Log'
        verbose_name_plural = 'Hata Logları'
        indexes = [
            models.Index(fields=['error_type', 'error_level']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.get_error_level_display()} - {self.error_type} - {self.created_at}"