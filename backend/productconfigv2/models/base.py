# productconfigv2/models/base.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name="Güncelleyen Kullanıcı"
    )

    class Meta:
        abstract = True
        verbose_name = "01- Base Model"
        verbose_name_plural = "01- Base Modeller"

    def soft_delete(self):
        self.is_active = False
        self.save()

    def restore(self):
        self.is_active = True
        self.save()
