# path: /var/www/sapb1reportsv2/backend/nexuscore/api/urls.py

from rest_framework.routers import DefaultRouter

# ### YENİ: Tüm ViewSet'lerimizi import ediyoruz ###
from .viewsets import (
    DynamicDBConnectionViewSet, 
    VirtualTableViewSet, 
    ReportTemplateViewSet,
    DataAppViewSet,                 # <-- YENİ
    AppRelationshipViewSet          # <-- YENİ
)

router = DefaultRouter()

router.register(r'connections', DynamicDBConnectionViewSet, basename='connections')
router.register(r'virtual-tables', VirtualTableViewSet, basename='virtual-tables')
router.register(r'report-templates', ReportTemplateViewSet, basename='report-templates')

# ### YENİ: Yeni endpoint'lerimizi router'a kaydediyoruz ###
# Bunlar bizim "Veri Modeli Editörü"müzün API'ları olacak.
router.register(r'data-apps', DataAppViewSet, basename='data-apps')
router.register(r'app-relationships', AppRelationshipViewSet, basename='app-relationships')


urlpatterns = router.urls