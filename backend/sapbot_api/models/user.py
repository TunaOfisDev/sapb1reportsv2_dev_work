# backend/sapbot_api/models/user.py
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from .base import BaseModel, TimestampedModel

User = get_user_model()


class UserProfile(BaseModel):
    """Kullanıcı profil modeli - SAPBot özel ayarları"""
    
    LANGUAGE_CHOICES = [
        ('tr', 'Türkçe'),
        ('en', 'İngilizce'),
    ]
    
    USER_TYPE_CHOICES = [
        ('user', 'Son Kullanıcı'),
        ('technical', 'Teknik Kullanıcı'),
        ('admin', 'Yönetici'),
        ('super_admin', 'Süper Yönetici'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='sapbot_profile',
        verbose_name='Kullanıcı'
    )
    display_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Görünen Ad'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user',
        verbose_name='Kullanıcı Tipi'
    )
    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='tr',
        verbose_name='Tercih Edilen Dil'
    )
    sap_modules = JSONField(
        default=list,
        blank=True,
        verbose_name='SAP Modülleri',
        help_text='Kullanıcının erişebileceği SAP modülleri'
    )
    chat_settings = JSONField(
        default=dict,
        blank=True,
        verbose_name='Chat Ayarları'
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Email Bildirimleri'
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name='Push Bildirimleri'
    )
    session_timeout = models.IntegerField(
        default=1440,  # 24 saat
        verbose_name='Oturum Timeout (dakika)'
    )
    max_daily_requests = models.IntegerField(
        default=100,
        verbose_name='Günlük Maksimum İstek'
    )
    avatar = models.ImageField(
        upload_to='sapbot_api/avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='Biyografi'
    )
    is_beta_user = models.BooleanField(
        default=False,
        verbose_name='Beta Kullanıcısı mı?'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Son Giriş IP'
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Son Aktivite'
    )
    
    class Meta:
        db_table = 'sapbot_user_profiles'
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['is_beta_user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"
    
    @property
    def full_name(self):
        """Tam ad"""
        return self.display_name or self.user.email.split('@')[0]
    
    def get_default_chat_settings(self):
        """Varsayılan chat ayarları"""
        return {
            'response_format': 'detailed',
            'show_sources': True,
            'auto_translate': False,
            'context_memory': 10,
            'technical_mode': self.user_type == 'technical'
        }
    
    def update_last_activity(self):
        """Son aktivite zamanını güncelle"""
        from django.utils import timezone
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class UserPreferences(BaseModel):
    """Kullanıcı tercih modeli"""
    
    THEME_CHOICES = [
        ('light', 'Açık Tema'),
        ('dark', 'Koyu Tema'),
        ('auto', 'Otomatik'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='sapbot_preferences',
        verbose_name='Kullanıcı'
    )
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light',
        verbose_name='Tema'
    )
    font_size = models.IntegerField(
        default=14,
        verbose_name='Font Boyutu'
    )
    show_typing_indicator = models.BooleanField(
        default=True,
        verbose_name='Yazıyor Göstergesini Göster'
    )
    sound_enabled = models.BooleanField(
        default=True,
        verbose_name='Ses Etkin'
    )
    keyboard_shortcuts = models.BooleanField(
        default=True,
        verbose_name='Klavye Kısayolları'
    )
    auto_save_conversations = models.BooleanField(
        default=True,
        verbose_name='Konuşmaları Otomatik Kaydet'
    )
    show_source_preview = models.BooleanField(
        default=True,
        verbose_name='Kaynak Önizlemesi Göster'
    )
    compact_mode = models.BooleanField(
        default=False,
        verbose_name='Kompakt Mod'
    )
    custom_css = models.TextField(
        null=True,
        blank=True,
        verbose_name='Özel CSS'
    )
    dashboard_widgets = JSONField(
        default=list,
        blank=True,
        verbose_name='Dashboard Widget\'ları'
    )
    
    class Meta:
        db_table = 'sapbot_user_preferences'
        verbose_name = 'Kullanıcı Tercihi'
        verbose_name_plural = 'Kullanıcı Tercihleri'
    
    def __str__(self):
        return f"{self.user.email} - Tercihler"


class UserSession(TimestampedModel):
    """Kullanıcı oturum modeli"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sapbot_sessions',
        verbose_name='Kullanıcı'
    )
    session_key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Oturum Anahtarı'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP Adresi'
    )
    user_agent = models.TextField(
        verbose_name='Tarayıcı Bilgisi'
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Konum'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktif mi?'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='Son Aktivite'
    )
    expires_at = models.DateTimeField(
        verbose_name='Sona Erme Zamanı'
    )
    device_info = JSONField(
        default=dict,
        blank=True,
        verbose_name='Cihaz Bilgisi'
    )
    
    class Meta:
        db_table = 'sapbot_user_sessions'
        verbose_name = 'Kullanıcı Oturumu'
        verbose_name_plural = 'Kullanıcı Oturumları'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}..."
    
    @property
    def is_expired(self):
        """Süresi dolmuş mu?"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def extend_session(self, minutes=1440):
        """Oturum süresini uzat"""
        from django.utils import timezone
        from datetime import timedelta
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save(update_fields=['expires_at'])


class UserActivity(TimestampedModel):
    """Kullanıcı aktivite modeli"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('login', 'Giriş'),
        ('logout', 'Çıkış'),
        ('chat', 'Chat'),
        ('upload', 'Dosya Yükleme'),
        ('search', 'Arama'),
        ('download', 'İndirme'),
        ('settings', 'Ayarlar'),
        ('api_call', 'API Çağrısı'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sapbot_activities',
        verbose_name='Kullanıcı'
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        verbose_name='Aktivite Tipi'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Açıklama'
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
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Oturum Anahtarı'
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    
    class Meta:
        db_table = 'sapbot_user_activities'
        verbose_name = 'Kullanıcı Aktivitesi'
        verbose_name_plural = 'Kullanıcı Aktiviteleri'
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"


class UserApiKey(BaseModel):
    """Kullanıcı API anahtarı modeli"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sapbot_api_keys',
        verbose_name='Kullanıcı'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Ad'
    )
    key = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='API Anahtarı'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktif mi?'
    )
    permissions = JSONField(
        default=list,
        blank=True,
        verbose_name='İzinler'
    )
    rate_limit = models.IntegerField(
        default=60,
        verbose_name='Dakika Başı Limit'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Sona Erme Zamanı'
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Son Kullanım'
    )
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Kullanım Sayısı'
    )
    
    class Meta:
        db_table = 'sapbot_user_api_keys'
        verbose_name = 'Kullanıcı API Anahtarı'
        verbose_name_plural = 'Kullanıcı API Anahtarları'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    def generate_key(self):
        """API anahtarı oluştur"""
        import secrets
        self.key = secrets.token_urlsafe(48)
    
    def increment_usage(self):
        """Kullanım sayısını artır"""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
    
    @property
    def is_expired(self):
        """Süresi dolmuş mu?"""
        from django.utils import timezone
        return self.expires_at and timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        """Kaydetme sırasında anahtar oluştur"""
        if not self.key:
            self.generate_key()
        super().save(*args, **kwargs)