# backend/hanadbintegration/api/urls.py

from django.urls import path
from .views import HANADBIntegrationListView, HANADBIntegrationDetailView

# Uygulama adı
app_name = "hanadbintegration"

urlpatterns = [
    path("hanadb-integration/", HANADBIntegrationListView.as_view(), name="hanadb-integration-list"),
    path("hanadb-integration/<int:pk>/", HANADBIntegrationDetailView.as_view(), name="hanadb-integration-detail"),
]
