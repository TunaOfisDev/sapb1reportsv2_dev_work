# backend/customersales/models/base.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """
    Projedeki tüm modeller için ortak alanları içeren soyut temel model.
    Bu model, veritabanında bir tablo oluşturmaz. Diğer modellerin
    miras alması için kullanılır.

    Alanlar:
        is_active (BooleanField): Kaydın aktif olup olmadığını belirtir (soft delete için).
        created_at (DateTimeField): Kaydın oluşturulma zaman damgası.
        updated_at (DateTimeField): Kaydın son güncellenme zaman damgası.
    """
    is_active = models.BooleanField(
        _("Aktif Mi?"),
        default=True,
        help_text=_("Kaydın sistemde aktif olarak kullanılıp kullanılmayacağını belirtir.")
    )
    created_at = models.DateTimeField(
        _("Oluşturulma Tarihi"),
        auto_now_add=True,
        editable=False,
        help_text=_("Kaydın veritabanına eklendiği tarih.")
    )
    updated_at = models.DateTimeField(
        _("Güncellenme Tarihi"),
        auto_now=True,
        editable=False,
        help_text=_("Kaydın son güncellendiği tarih.")
    )

    class Meta:
        abstract = True  # Bu modelin soyut olduğunu ve veritabanı tablosu oluşturmayacağını belirtir.
        ordering = ['-created_at'] # Varsayılan sıralama