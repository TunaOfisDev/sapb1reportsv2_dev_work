# backend/mailservice/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MailLogViewSet

router = DefaultRouter()
router.register(r'logs', MailLogViewSet, basename='mail-log')

app_name = 'mailservice'

urlpatterns = [
    path('', include(router.urls)),
]