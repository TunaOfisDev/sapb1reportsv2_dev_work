# backend/heliosforgev2/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from heliosforgev2.api.views import (
    DocumentViewSet,
    ChunkViewSet,
    ImageViewSet,
    DocumentUploadView
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'chunks', ChunkViewSet, basename='chunk')
router.register(r'images', ImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
]

