# backend/docarchive/api/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    DocumentListCreateAPIView, DocumentDetailAPIView,
    DepartmentListCreateAPIView, DepartmentDetailAPIView,
    DocumentFileListCreateAPIView, DocumentFileDetailAPIView
)

app_name = 'docarchive'  # Uygulama adı ayarlanıyor

urlpatterns = [
    path('documents/', DocumentListCreateAPIView.as_view(), name='document-list-create'),
    path('documents/<int:pk>/', DocumentDetailAPIView.as_view(), name='document-detail'),
    path('departments/', DepartmentListCreateAPIView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentDetailAPIView.as_view(), name='department-detail'),
    path('document-files/', DocumentFileListCreateAPIView.as_view(), name='document-file-list-create'),
    path('document-files/<int:pk>/', DocumentFileDetailAPIView.as_view(), name='document-file-detail'),
    path('documents/<int:document_id>/files/', DocumentFileListCreateAPIView.as_view(), name='document-files-list')
]

# Yükleme işlemi için statik dosya yolunu ayarla
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

