# backend/rawmaterialwarehousestock/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListView, FetchHanaDataView, UpdateSelectionView, UpdateZeroStockVisibilityView, FilteredListView
from .export_views import ColumnFilterExportView
from celery_progress.views import get_progress

app_name = 'rawmaterialwarehousestock'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('list/', ListView.as_view(), name='list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-rawmaterial'),
    path('progress/<task_id>/', get_progress, name='task-progress'),
    path('update-selection/', UpdateSelectionView.as_view(), name='update-selection'),
    path('update-zero-stock-visibility/', UpdateZeroStockVisibilityView.as_view(), name='update-zero-stock-visibility'),
    path('filtered-list/', FilteredListView.as_view(), name='filtered-list'),
    path('export/column-filter/', ColumnFilterExportView.as_view(), name='export-column-filter'),
    
]
