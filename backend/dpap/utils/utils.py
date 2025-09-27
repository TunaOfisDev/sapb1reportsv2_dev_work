# backend/dpap/utils/utils.py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from authcentral.models import CustomUser 
from ..models.models import API, APIAccessPermission, APIAuditLog

def has_api_access(user: CustomUser, api_name: str) -> bool:
    """
    Kullanıcının belirli bir API'ye erişim izni olup olmadığını kontrol eder.
    
    Args:
        user (CustomUser): Erişim izni kontrol edilecek kullanıcı.
        api_name (str): Kontrol edilecek API'nin adı.
    
    Returns:
        bool: Erişim izni varsa True, yoksa False.
    """
    if not user.is_authenticated:
        return False

    # Kullanıcının departman ve pozisyonlarına göre API erişim izni kontrolü
    user_departments = user.departments.all()
    user_positions = user.positions.all()

    # İlgili API'ye erişim izni olup olmadığını kontrol et
    permissions = APIAccessPermission.objects.filter(
        api__name=api_name,
        api__is_active=True
    ).filter(
        Q(departments__in=user_departments) | Q(positions__in=user_positions)
    ).first()

    return permissions is not None


def api_access_required(api_name: str):
    """
    View fonksiyonları için dekoratör. Belirli bir API'ye erişim izni olup olmadığını kontrol eder.
    
    Args:
        api_name (str): Kontrol edilecek API'nin adı.
    
    Returns:
        function: Dekore edilmiş view fonksiyonu.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            user = request.user
            if has_api_access(user, api_name):
                return view_func(view, request, *args, **kwargs)
            else:
                # Erişim reddedildiğinde log kaydı yap
                log_api_access(user, api_name, success=False)
                return Response({'detail': 'Access forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return _wrapped_view
    return decorator


def has_crud_permission(user: CustomUser, api_name: str, action: str) -> bool:
    """
    Kullanıcının belirli bir API'de CRUD işlemi yapma yetkisini kontrol eder.

    Args:
        user (CustomUser): Kontrol edilecek kullanıcı.
        api_name (str): API'nin adı.
        action (str): Yapılacak işlem (create, read, update, delete).
    
    Returns:
        bool: Yetki varsa True, yoksa False.
    """
    if not user.is_authenticated:
        return False

    # Kullanıcının departman ve pozisyonlarına göre CRUD yetkilerini kontrol et
    user_departments = user.departments.all()
    user_positions = user.positions.all()

    permissions = APIAccessPermission.objects.filter(
        api__name=api_name,
        api__is_active=True
    ).filter(
        Q(departments__in=user_departments) | Q(positions__in=user_positions)
    ).first()

    if not permissions:
        return False

    # CRUD işlemi yetkisi kontrolü
    if action == 'create' and permissions.can_create:
        return True
    if action == 'read' and permissions.can_read:
        return True
    if action == 'update' and permissions.can_update:
        return True
    if action == 'delete' and permissions.can_delete:
        return True

    return False


def log_api_access(user: CustomUser, api_name: str, success: bool):
    """
    API erişim denemelerini loglar.
    
    Args:
        user (CustomUser): Erişim denemesi yapan kullanıcı.
        api_name (str): Denenen API'nin adı.
        success (bool): Erişim başarılı mı?
    """
    try:
        api_access = API.objects.get(name=api_name)
        APIAuditLog.objects.create(
            user=user,
            api=api_access,
            success=success
        )
    except API.DoesNotExist:
        pass  # API tanımlı değilse loglama yapılmaz.
