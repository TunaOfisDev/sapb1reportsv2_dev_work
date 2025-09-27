# backend/dpap/models/base.py
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """
    Tüm modeller için ortak alanlar ve fonksiyonlar sağlar.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Kayıtları fiziksel olarak silmek yerine soft_delete uygulayın."""
        self.is_active = False
        self.save()

    def restore(self):
        """Soft delete ile silinen kayıtları geri yükleyin."""
        self.is_active = True
        self.save()

    def delete(self, using=None, keep_parents=False):
        """Klasik delete yerine soft_delete kullanarak kaydı inaktif hale getirin."""
        self.soft_delete()

    @classmethod
    def active(cls):
        """Sadece aktif olan kayıtları filtreleyen bir queryset döndürür."""
        return cls.objects.filter(is_active=True)

    @classmethod
    def inactive(cls):
        """İnaktif olan kayıtları filtreleyen bir queryset döndürür."""
        return cls.objects.filter(is_active=False)

    @classmethod
    def bulk_create_or_update(cls, objs):
        """
        Kayıtları toplu olarak oluşturun veya güncelleyin.
        Varsayılan model primary key'i üzerinden güncelleme yapılır.
        """
        for obj in objs:
            cls.objects.update_or_create(
                pk=obj.pk,
                defaults=obj.__dict__
            )

    def save(self, *args, **kwargs):
        """Her kaydetme işleminde güncelleme tarihini kaydeder."""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
