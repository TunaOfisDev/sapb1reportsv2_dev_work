# path: /var/www/sapb1reportsv2/backend/nexuscore/api/urls.py

from rest_framework.routers import DefaultRouter
from .viewsets import DynamicDBConnectionViewSet, VirtualTableViewSet

# DefaultRouter, aynı zamanda bizim için bir API kök görünümü (root view) oluşturur.
# Bu, geliştirme sırasında tüm endpoint'leri tek bir sayfada görmemizi sağlar.
router = DefaultRouter()

# 1. 'connections' endpoint'ini DynamicDBConnectionViewSet'e bağlıyoruz.
# Bu, veri tabanı bağlantılarını yöneten admin'e özel URL'leri oluşturur.
router.register(r'connections', DynamicDBConnectionViewSet, basename='connections')

# 2. 'virtual-tables' endpoint'ini VirtualTableViewSet'e bağlıyoruz.
# Bu, kullanıcıların sanal tablolarını (sorgularını) yöneteceği URL'leri oluşturur.
# Özel 'execute' aksiyonumuz da otomatik olarak buraya dahil edilir.
router.register(r'virtual-tables', VirtualTableViewSet, basename='virtual-tables')

# Router tarafından oluşturulan tüm URL'leri urlpatterns listesine dahil ediyoruz.
urlpatterns = router.urls