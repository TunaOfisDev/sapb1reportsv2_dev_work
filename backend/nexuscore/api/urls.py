# path: /var/www/sapb1reportsv2/backend/nexuscore/api/urls.py

from rest_framework.routers import DefaultRouter
# ### YENİ: ReportTemplateViewSet'i import ediyoruz ###
from .viewsets import DynamicDBConnectionViewSet, VirtualTableViewSet, ReportTemplateViewSet

router = DefaultRouter()

router.register(r'connections', DynamicDBConnectionViewSet, basename='connections')
router.register(r'virtual-tables', VirtualTableViewSet, basename='virtual-tables')
# ### YENİ: Yeni endpoint'imizi router'a kaydediyoruz ###
router.register(r'report-templates', ReportTemplateViewSet, basename='report-templates')

urlpatterns = router.urls