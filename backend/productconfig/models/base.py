# backend/productconfig/models/base.py
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """
    Tüm modeller için ortak özellikleri barındıran temel model.
    ID tamsayı olarak tanımlanmış olup, soft delete, oluşturulma ve güncellenme
    zamanı gibi temel alanları içerir.
    """

    id = models.AutoField(primary_key=True, verbose_name="ID")
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Oluşturulma Zamanı"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Güncellenme Zamanı"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")

    class Meta:
        abstract = True  # Bu sınıf sadece diğer modeller için temel olarak kullanılır.
        ordering = ['-created_at']  # Varsayılan sıralama oluşturulma zamanına göre.

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete işlemi gerçekleştirir. Kayıt veritabanında kalır ancak aktiflik durumu False olur.
        """
        self.is_active = False
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """
        Hard delete işlemi gerçekleştirir. Kayıt veritabanından tamamen silinir.
        """
        super(BaseModel, self).delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """
        Soft delete edilmiş bir kaydı geri getirir.
        """
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.__class__.__name__} #{self.id}"
