# backend/dpap/api/urls.py
from django.urls import path
from .views import (
    APIAccessListView,
    APIAccessDetailView,
    APIAccessPermissionListView,
    APIAuditLogListView,
    APIAccessCreateView,
    APIAccessUpdateView,
    APIAccessDeleteView
)

app_name = 'dpap'

urlpatterns = [
    # API erişim listesi ve detayları
    path('access/', APIAccessListView.as_view(), name='api_access_list'),
    path('access/<int:api_id>/', APIAccessDetailView.as_view(), name='api_access_detail'),

    # API CRUD yetkileri listesi
    path('permissions/', APIAccessPermissionListView.as_view(), name='api_access_permission_list'),

    # API erişim logları
    path('audit-logs/', APIAuditLogListView.as_view(), name='api_audit_log_list'),

    # API erişim oluşturma, güncelleme ve silme işlemleri
    path('access/create/', APIAccessCreateView.as_view(), name='api_access_create'),
    path('access/update/<int:api_id>/', APIAccessUpdateView.as_view(), name='api_access_update'),
    path('access/delete/<int:api_id>/', APIAccessDeleteView.as_view(), name='api_access_delete'),
]
