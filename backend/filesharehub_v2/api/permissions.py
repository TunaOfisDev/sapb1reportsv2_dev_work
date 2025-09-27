# backend/filesharehub_v2/api/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnlyPermission(BasePermission):
    """
    Yalnızca okuma (GET, HEAD, OPTIONS) isteklerine izin verir.
    """

    message = "Sadece okuma erişiminiz bulunmaktadır. Yazma işlemi yapılamaz."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
