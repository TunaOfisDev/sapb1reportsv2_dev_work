# backend/sapbot_api/models/chat.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from .base import BaseModel, TimestampedModel


class ChatConversation(BaseModel):
    """Chat konuşması modeli"""
    
    USER_TYPE_CHOICES = [
        ('user', 'Son Kullanıcı'),
        ('technical', 'Teknik Kullanıcı'),
        ('admin', 'Yönetici'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sapbot_conversations',
        verbose_name='Kullanıcı'
    )
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Oturum ID'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user',
        verbose_name='Kullanıcı Tipi'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='Tarayıcı Bilgisi'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Adresi'
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='Son Aktivite'
    )
    is_archived = models.BooleanField(
        default=False,
        verbose_name='Arşivlenmiş mi?'
    )
    
    class Meta:
        db_table = 'sapbot_chat_conversations'
        verbose_name = 'Chat Konuşması'
        verbose_name_plural = 'Chat Konuşmaları'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user_type']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['is_archived']),
        ]
    
    def __str__(self):
        return f"Konuşma - {self.session_id[:8]} ({self.user_type})"
    
    @property
    def message_count(self):
        """Mesaj sayısı"""
        return self.messages.count()
    
    @property
    def duration_minutes(self):
        """Konuşma süresi (dakika)"""
        if self.messages.exists():
            first_message = self.messages.order_by('created_at').first()
            last_message = self.messages.order_by('-created_at').first()
            if first_message and last_message:
                duration = last_message.created_at - first_message.created_at
                return duration.total_seconds() / 60
        return 0


class ChatMessage(BaseModel):
    """Chat mesajı modeli"""
    
    MESSAGE_TYPE_CHOICES = [
        ('user', 'Kullanıcı Mesajı'),
        ('assistant', 'Asistan Yanıtı'),
        ('system', 'Sistem Mesajı'),
        ('error', 'Hata Mesajı'),
    ]
    
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Konuşma'
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        verbose_name='Mesaj Tipi'
    )
    content = models.TextField(
        verbose_name='Mesaj İçeriği'
    )
    content_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='İçerik Hash\'i'
    )
    sources_used = models.ManyToManyField(
        'sapbot_api.KnowledgeChunk',
        blank=True,
        related_name='used_in_messages',
        verbose_name='Kullanılan Kaynaklar'
    )
    response_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Yanıt Süresi (saniye)'
    )
    token_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Token Sayısı'
    )
    model_used = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Kullanılan Model'
    )
    intent_detected = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Tespit Edilen Niyet'
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Güven Skoru'
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    
    class Meta:
        db_table = 'sapbot_chat_messages'
        verbose_name = 'Chat Mesajı'
        verbose_name_plural = 'Chat Mesajları'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['message_type']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['intent_detected']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_message_type_display()} - {content_preview}"
    
    @property
    def source_count(self):
        """Kullanılan kaynak sayısı"""
        return self.sources_used.count()
    
    def generate_content_hash(self):
        """İçerik hash'i oluştur"""
        import hashlib
        return hashlib.sha256(self.content.encode('utf-8')).hexdigest()
    
    def save(self, *args, **kwargs):
        """Kaydetme sırasında hash oluştur"""
        if not self.content_hash:
            self.content_hash = self.generate_content_hash()
        super().save(*args, **kwargs)


class MessageFeedback(TimestampedModel):
    """Mesaj geri bildirim modeli"""
    
    RATING_CHOICES = [
        (1, 'Çok Kötü'),
        (2, 'Kötü'),
        (3, 'Orta'),
        (4, 'İyi'),
        (5, 'Çok İyi'),
    ]
    
    message = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name='Mesaj'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Puan'
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
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Kullanıcı IP'
    )
    
    class Meta:
        db_table = 'sapbot_message_feedback'
        verbose_name = 'Mesaj Geri Bildirimi'
        verbose_name_plural = 'Mesaj Geri Bildirimleri'
    
    def __str__(self):
        return f"Geri Bildirim - {self.rating}/5 - {self.message.id}"


class ConversationSummary(BaseModel):
    """Konuşma özet modeli"""
    
    conversation = models.OneToOneField(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='summary',
        verbose_name='Konuşma'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Başlık'
    )
    summary = models.TextField(
        verbose_name='Özet'
    )
    main_topics = JSONField(
        default=list,
        verbose_name='Ana Konular'
    )
    sap_modules_discussed = JSONField(
        default=list,
        verbose_name='Tartışılan SAP Modülleri'
    )
    resolution_status = models.CharField(
        max_length=50,
        choices=[
            ('resolved', 'Çözüldü'),
            ('partial', 'Kısmen Çözüldü'),
            ('unresolved', 'Çözülmedi'),
            ('redirected', 'Yönlendirildi'),
        ],
        default='unresolved',
        verbose_name='Çözüm Durumu'
    )
    auto_generated = models.BooleanField(
        default=True,
        verbose_name='Otomatik Oluşturuldu mu?'
    )
    
    class Meta:
        db_table = 'sapbot_conversation_summaries'
        verbose_name = 'Konuşma Özeti'
        verbose_name_plural = 'Konuşma Özetleri'
    
    def __str__(self):
        return f"Özet - {self.title}"