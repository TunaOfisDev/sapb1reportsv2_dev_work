# backend/hanaservicelayer/api/permissions.py

from rest_framework.permissions import BasePermission

class IsSAPAuthorizedUser(BasePermission):
    """
    Sadece 'Export', 'Yurtici_Satis' ve 'Bilgi_Sistem' departmanındaki kullanıcıların API'yi kullanmasına izin verir.
    """

    allowed_departments = {"Export", "Yurtici_Satis", "Bilgi_Sistem"}

    def has_permission(self, request, view):
        # Kullanıcı giriş yapmış olmalı
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Kullanıcının departmanlarını al
        user_departments = set(request.user.departments.values_list("name", flat=True))

        # Kullanıcının yetkili departmanlardan birinde olup olmadığını kontrol et
        return bool(self.allowed_departments.intersection(user_departments))
