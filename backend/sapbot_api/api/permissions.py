
# backend/sapbot_api/api/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Yalnızca admin kullanıcılar yazabilir"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """Objenin sahibi veya admin"""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        owner = getattr(obj, "user", None) or getattr(obj, "uploaded_by", None)
        return owner == request.user
 

 
