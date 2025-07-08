# backend/salesinvoicesum/api/urls.py
from django.urls import path
from .views import SalesInvoiceSumListView, FetchHanaDataView
from .dynamic_name_column import DynamicNameColumnView  

app_name = 'salesinvoicesum'

urlpatterns = [
    path('sum-list/', SalesInvoiceSumListView.as_view(), name='sum-list'),  # şimdilik sorun yok
    path('fetch-hana/', FetchHanaDataView.as_view(), name='fetch-hana-salesinvoicesum'),  # GÜNCELLENDİ
    path('dynamic-name-columns/', DynamicNameColumnView.as_view(), name='dynamic-name-columns-salesinvoicesum'),  # GÜNCELLENDİ
]
