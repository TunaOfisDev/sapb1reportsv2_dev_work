# backend/logo_supplier_receivables_aging/api/urls.py

from django.urls import path
from .views import FetchHanaDataView, SupplierAgingSummaryView, LastUpdatedView

app_name = "logo_supplier_receivables_aging"

urlpatterns = [
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-supplier-aging'),
    path('summary/', SupplierAgingSummaryView.as_view(), name='supplier-aging-summary'),
    path('last-updated/', LastUpdatedView.as_view(), name='last-updated-supplier-aging'),
]
