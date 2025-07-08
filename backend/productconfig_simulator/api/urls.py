# backend/productconfig_simulator/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .simulation_job_views import SimulationJobViewSet
from .simulation_error_views import SimulationErrorViewSet
from .simulated_variant_views import SimulatedVariantViewSet

# Router oluştur
router = DefaultRouter()

# ViewSet'leri kaydet
router.register(r'simulation-jobs', SimulationJobViewSet, basename='simulation-jobs')
router.register(r'simulation-errors', SimulationErrorViewSet, basename='simulation-errors')
router.register(r'simulated-variants', SimulatedVariantViewSet, basename='simulated-variants')

# URL pattern'leri
urlpatterns = [
    # Router URL'leri
    path('', include(router.urls)),
    
    # Özel endpoint'ler (ihtiyaç duyulursa buraya eklenebilir)
    # path('custom-endpoint/', CustomView.as_view(), name='custom-endpoint'),
]