# backend/dpap/models/models.py
from django.db import models
from django.conf import settings
from authcentral.models import Department, Position
from .base import BaseModel

class API(BaseModel):
    """
    API'lere erişim izinlerini dinamik olarak yönetir.
    """
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class APIAccessPermission(BaseModel):
    """
    Her API için CRUD yetkilerini yönetir.
    """
    api = models.ForeignKey(API, on_delete=models.CASCADE, related_name='permissions')
    can_create = models.BooleanField(default=False)  # Create yetkisi
    can_read = models.BooleanField(default=True)     # Varsayılan olarak okuma izni açık
    can_update = models.BooleanField(default=False)  # Update yetkisi
    can_delete = models.BooleanField(default=False)  # Delete yetkisi
    departments = models.ManyToManyField(Department, related_name='api_permissions', blank=True)
    positions = models.ManyToManyField(Position, related_name='api_permissions', blank=True)

    def __str__(self):
        return f"Permissions for {self.api.name}"

    class Meta:
        unique_together = ('api',)


class APIAuditLog(BaseModel):
    """
    API erişim denemelerini ve sonuçlarını kayıt altına alır.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api = models.ForeignKey(API, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.api.name} - {'Success' if self.success else 'Failed'}"
