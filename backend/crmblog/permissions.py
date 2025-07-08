# backend/crmblog/permissions.py
from rest_framework import permissions
from dpap.models.models import APIAccessPermission

class HasCRMBlogAccess(permissions.BasePermission):
    """
    Kullanıcının CRM Blog API'ye erişim iznine sahip olup olmadığını kontrol eder.
    """

    def has_permission(self, request, view):
        user = request.user

        # API için CRUD izinlerini kontrol et
        permission = APIAccessPermission.objects.filter(
            api__name='crmblog',
            departments__in=user.departments.all()
        ).first()

        if permission:
            # Kullanıcının işlem türüne göre yetkilerini kontrol ediyoruz
            if request.method == 'POST' and permission.can_create:
                return True
            if request.method in permissions.SAFE_METHODS and permission.can_read:
                return True
            if request.method == 'PUT' and permission.can_update:
                return True
            if request.method == 'DELETE' and permission.can_delete:
                return True

        # Türkçe hata mesajı döndürülüyor
        self.message = "Bu işlemi yapmak için yetkiniz yok. Lütfen yöneticiyle iletişime geçin."
        return False
