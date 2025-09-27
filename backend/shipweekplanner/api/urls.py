# backend/shipweekplanner/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentOrderViewSet

app_name = 'shipweekplanner_api'

# DefaultRouter ile viewset'leri otomatik olarak rotaya bağlayacağız
router = DefaultRouter()
router.register(r'shipmentorders', ShipmentOrderViewSet, basename='shipmentorder')

urlpatterns = [
    # ViewSet üzerinden tanımlanan rotaları otomatik ekle
    path('', include(router.urls)),
    
    # Özel endpointler için ek yollar
    path('weekly/', ShipmentOrderViewSet.as_view({'get': 'weekly_orders'}), name='weekly-orders'),
    path('weekly/report/', ShipmentOrderViewSet.as_view({'get': 'weekly_report'}), name='weekly-report'),
    path('current-week/', ShipmentOrderViewSet.as_view({'get': 'current_week'}), name='current-week'),
    path('copy-next-week/', ShipmentOrderViewSet.as_view({'post': 'copy_next_week'}), name='copy-next-week'),
]