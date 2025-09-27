# backend/productconfig/api/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import VariantViewSet, OptionViewSet
from .configuration import ConfigurationAPIView

router = DefaultRouter()
router.register(r'variants', VariantViewSet, basename='variant')
router.register(r'options', OptionViewSet, basename='option')

urlpatterns = [
    path('configuration/', ConfigurationAPIView.as_view(), name='configuration'),
    path('configuration/<int:variant_id>/', ConfigurationAPIView.as_view(), name='configuration-detail'),
    path('configuration/<int:variant_id>/revert/', ConfigurationAPIView.as_view(), name='configuration-revert'),
] + router.urls
