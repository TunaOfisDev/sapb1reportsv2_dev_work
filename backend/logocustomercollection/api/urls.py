# backend/logocustomercollection/api/urls.py

from django.urls import path
from .views import (
    FetchLogoDataView,
    CustomerAgingSummaryView,
    LastUpdatedView,
)

app_name = "logocustomercollection"

urlpatterns = [
    # Logo DB’den ham veriyi çek + yaşlandırma tablosunu yeniden oluştur
    path("fetch-logo-data/", FetchLogoDataView.as_view(), name="fetch-logo-customer-aging", ),
    # Tüm müşteriler için yaşlandırma özeti
    path("summary/", CustomerAgingSummaryView.as_view(), name="customer-aging-summary", ),
    # Ham verinin / özetin en son güncellendiği dönem
    path("last-updated/", LastUpdatedView.as_view(), name="customer-aging-last-updated", ),
]
