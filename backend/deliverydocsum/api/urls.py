# backend/deliverydocsum/api/urls.py
from django.urls import path
from .views import DeliveryDocSummaryListView, FetchHanaDataView

app_name = 'deliverydocsum'

urlpatterns = [
    path('summary-list/', DeliveryDocSummaryListView.as_view(), name='summary-list'),
    path('fetch-hana/', FetchHanaDataView.as_view(), name='fetch-hana-deliverydocsum'),

]
