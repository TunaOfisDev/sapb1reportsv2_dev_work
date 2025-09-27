# backend/orderarchive/urls/order_archive_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.order_archive_view import OrderDetailViewSet
from ..views.column_headers_view import ColumnHeadersAPIView

router = DefaultRouter()
router.register(r'', OrderDetailViewSet, basename='order-detail')

urlpatterns = [
    path('columns/', ColumnHeadersAPIView.as_view(), name='order-archive-columns'),
    path('', include(router.urls)),
]
