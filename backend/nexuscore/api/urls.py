# path: /var/www/sapb1reportsv2/backend/nexuscore/api/urls.py

from rest_framework.routers import DefaultRouter

from .viewsets import (
    DynamicDBConnectionViewSet, 
    VirtualTableViewSet, 
    ReportTemplateViewSet,
    DataAppViewSet,
    AppRelationshipViewSet,
    DBTypeMappingViewSet # Yeni ViewSet'i import ediyoruz
)

router = DefaultRouter()

router.register(r'connections', DynamicDBConnectionViewSet, basename='connections')
router.register(r'virtual-tables', VirtualTableViewSet, basename='virtual-tables')
router.register(r'report-templates', ReportTemplateViewSet, basename='report-templates')
router.register(r'data-apps', DataAppViewSet, basename='data-apps')
router.register(r'app-relationships', AppRelationshipViewSet, basename='app-relationships')

# YENİ: Yönetici paneli için veri tipi eşleştirme endpoint'i
router.register(r'db-type-mappings', DBTypeMappingViewSet, basename='db-type-mappings')


urlpatterns = router.urls