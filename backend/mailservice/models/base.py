# backend/mailservice/models/base.py
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    Tüm modeller için temel zaman damgası alanlarını içeren abstract model
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi",
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi",
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
        
class SoftDeleteModel(TimeStampedModel):
    """
    Yumuşak silme özelliği için abstract model
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Silinmiş mi?",
        db_index=True
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Silinme Tarihi"
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Kaydı yumuşak sil"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Silinen kaydı geri yükle"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()