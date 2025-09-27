# backend/docarchivev2/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'documents', DocumentViewSet)

app_name = 'docarchivev2'

urlpatterns = [
    path('', include(router.urls)),
]
