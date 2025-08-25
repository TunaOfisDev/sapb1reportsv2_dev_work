# path: /var/www/sapb1reportsv2/backend/nexuscore/api/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from ..models import SharingStatus

class IsOwnerOrPublic(BasePermission):
    """
    Nesne seviyesinde özel bir izin sınıfı. Bir kullanıcının bir VirtualTable
    nesnesi üzerinde yetkisi olup olmadığını kontrol eder.

    Kurallar:
    1. Görüntüleme (GET, HEAD, OPTIONS):
       - Eğer nesne "Özel" (Private) DEĞİLSE (yani halka açıksa), HERKES görebilir.
       - VEYA isteği yapan kullanıcı nesnenin sahibi (owner) ise görebilir.

    2. Düzenleme/Silme (PUT, PATCH, DELETE):
       - Eğer nesne "Halka Açık (Düzenlenebilir)" (Public Editable) ise, HERKES düzenleyebilir.
       - VEYA isteği yapan kullanıcı nesnenin sahibi (owner) ise düzenleyebilir.
    """

    def has_permission(self, request, view):
        """
        ViewSet seviyesinde genel bir kontrol. Herhangi bir işlem için
        kullanıcının en azından sisteme giriş yapmış (authenticated) olması gerekir.
        Bu kontrol genellikle ViewSet'in kendi `permission_classes` listesindeki
        `IsAuthenticated` ile zaten sağlanır, ancak burada da bulunması iyidir.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Bu metod, DRF tarafından tek bir nesne üzerinde işlem yapılırken çağrılır.
        `obj`, kontrol edilen VirtualTable örneğidir.
        """
        # Görüntüleme (read-only) istekleri için (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            # Nesnenin sahibi ise veya nesne özel değilse (halka açıksa) izin ver.
            return obj.owner == request.user or obj.sharing_status != SharingStatus.PRIVATE

        # Yazma (write) istekleri için (PUT, PATCH, DELETE)
        # Nesnenin sahibi ise veya nesne herkes tarafından düzenlenebilir ise izin ver.
        return obj.owner == request.user or obj.sharing_status == SharingStatus.PUBLIC_EDITABLE