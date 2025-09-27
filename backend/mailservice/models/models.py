# backend/mailservice/models/models.py
from django.db import models
from django.conf import settings
from .base import SoftDeleteModel

class MailLog(SoftDeleteModel):
    """Mail gönderim kayıtları için model"""
    
    MAIL_TYPES = [
        ('NEW_CUSTOMER_FORM', 'Yeni Müşteri Formu'),
        ('SUPPORT', 'Destek'),
        ('NOTIFICATION', 'Bildirim'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Bekliyor'),
        ('SENDING', 'Gönderiliyor'),
        ('SENT', 'Gönderildi'),
        ('FAILED', 'Başarısız'),
    ]
    
    mail_type = models.CharField(
        max_length=50,
        choices=MAIL_TYPES,
        verbose_name="Mail Tipi"
    )
    
    subject = models.CharField(
        max_length=255,
        verbose_name="Konu"
    )
    
    recipients = models.JSONField(
        verbose_name="Alıcılar",
        help_text="Mail alıcılarının listesi"
    )
    
    sender = models.EmailField(
        verbose_name="Gönderen"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Durum"
    )
    
    # ForeignKey yerine email ve user_id alanları
    created_by_email = models.EmailField(
        verbose_name="Oluşturan Kullanıcı Email",
        null=True,
        blank=True
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CustomUser modeline referans
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_mails',
        verbose_name="Oluşturan",
        db_constraint=False  # Bu önemli - veritabanı kısıtlamasını esnetiyor
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Gönderim Tarihi",
        db_index=True
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Hata Mesajı"
    )
    
    has_attachments = models.BooleanField(
        default=False,
        verbose_name="Ek Var Mı?"
    )
    
    related_object_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="İlişkili Nesne Tipi"
    )
    
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="İlişkili Nesne ID"
    )
    
    class Meta:
        verbose_name = "Mail Logu"
        verbose_name_plural = "Mail Logları"
        indexes = [
            models.Index(fields=['mail_type', 'status']),
            models.Index(fields=['related_object_type', 'related_object_id']),
            models.Index(fields=['created_by_email']),
            models.Index(fields=['created_by_id']),
        ]
        
    def __str__(self):
        return f"{self.mail_type} - {self.subject} ({self.status})"

    @property
    def created_by_user(self):
        """CustomUser nesnesini döndürür (ihtiyaç halinde)"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if self.created_by_id:
            return User.objects.filter(id=self.created_by_id).first()
        return None