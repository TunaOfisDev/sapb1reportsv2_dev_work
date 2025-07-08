# backend/openorderdocsum/api/urls.py
from django.urls import path
from .views import SalesOrderDetailListView, FetchHanaDataView
from .docsum_views import DocumentSummaryListView, DocumentSummaryDocView
from .salesorderdetaildoc import SalesOrderDetailDocView
from .datefilter_views import DateFilterView  

app_name = 'salesorderdocsum'

urlpatterns = [
    path('sales-order-details/', SalesOrderDetailListView.as_view(), name='sales-order-details-list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-openorder'),
    path('sales-order-detail/<str:belge_no>/', SalesOrderDetailDocView.as_view(), name='sales-order-detail-doc'),
    path('document-summaries/', DocumentSummaryListView.as_view(), name='document-summaries-list'),
    path('document-summary/<str:belge_no>/', DocumentSummaryDocView.as_view(), name='document-summary-doc'),
    path('date-filter/', DateFilterView.as_view(), name='date-filter'),  # Yeni endpoint
]
