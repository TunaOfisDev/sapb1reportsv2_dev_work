# path: /var/www/sapb1reportsv2/backend/nexuscore/api/urls.py

from rest_framework.routers import DefaultRouter
from .viewsets import DynamicDBConnectionViewSet, VirtualTableViewSet

# Router'ı standart, varsayılan haliyle tanımlıyoruz.
router = DefaultRouter()

router.register(r'connections', DynamicDBConnectionViewSet, basename='connections')
router.register(r'virtual-tables', VirtualTableViewSet, basename='virtual-tables')

urlpatterns = router.urls