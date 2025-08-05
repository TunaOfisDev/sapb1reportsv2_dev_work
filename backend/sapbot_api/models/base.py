# backend/sapbot_api/models/base.py
from django.db import models
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """Tüm SAPBot modelleri için temel model sınıfı"""
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        verbose_name='ID'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Tarihi'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Güncellenme Tarihi'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktif mi?'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} - {self.id}"


class TimestampedModel(models.Model):
    """Sadece zaman damgası olan modeller için"""
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Tarihi'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Güncellenme Tarihi'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """Soft delete için manager"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(BaseModel):
    """Soft delete destekli model"""
    
    deleted_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Silinme Tarihi'
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Silinmiş kayıtlar dahil

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete işlemi"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Gerçek silme işlemi"""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Silinen kaydı geri getir"""
        self.deleted_at = None
        self.is_active = True
        self.save()


class CacheableModel(BaseModel):
    """Cache destekli model"""
    
    cache_key_prefix = None  # Alt sınıflarda tanımlanacak
    cache_timeout = 3600  # 1 saat varsayılan
    
    class Meta:
        abstract = True
    
    def get_cache_key(self):
        """Cache anahtarı oluştur"""
        if not self.cache_key_prefix:
            return f"{self.__class__.__name__.lower()}_{self.id}"
        return f"{self.cache_key_prefix}_{self.id}"
    
    def invalidate_cache(self):
        """Cache'i temizle"""
        from django.core.cache import cache
        cache.delete(self.get_cache_key())
    
    def save(self, *args, **kwargs):
        """Kaydetme sırasında cache'i temizle"""
        super().save(*args, **kwargs)
        self.invalidate_cache()


class AuditModel(BaseModel):
    """Audit trail için model"""
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='Oluşturan'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='Güncelleyen'
    )
    
    class Meta:
        abstract = True