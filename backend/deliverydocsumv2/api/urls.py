# backend/deliverydocsum/api/urls.py
from django.urls import path
from .views import DeliveryDocSummaryListView, FetchHanaDataView
from .dynamicnamecolumn import DynamicNameColumnView  # Yeni view'ı ekliyoruz

app_name = 'deliverydocsumv2'

urlpatterns = [
    path('summary-list/', DeliveryDocSummaryListView.as_view(), name='summary-list'),
    path('fetch-hana/', FetchHanaDataView.as_view(), name='fetch-hana-deliverydocsumv2'),
    path('dynamic-name-columns/', DynamicNameColumnView.as_view(), name='dynamic-name-columns'),  # Yeni endpoint
]

