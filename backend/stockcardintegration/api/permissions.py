# backend/stockcardintegration/api/permissions.py

from rest_framework.permissions import BasePermission

class IsStockCardAuthorizedUser(BasePermission):
    """
    Stok Kartı API erişim kontrolü.
    - Sadece 'Export', 'Yurtici_Satis' ve 'Bilgi_Sistem' departmanlarına ait kullanıcılar erişebilir.
    """

    allowed_departments = {"Export", "Yurtici_Satis", "Bilgi_Sistem"}

    def has_permission(self, request, view):
        """
        Kullanıcının yetkili olup olmadığını kontrol eder.
        """
        user = request.user

        # Kullanıcı oturum açmış mı ve yetkili mi?
        if not user or not user.is_authenticated:
            return False

        # Kullanıcının departmanlarını kontrol et
        user_departments = {dept.name for dept in user.departments.all()}
        return bool(self.allowed_departments.intersection(user_departments))
