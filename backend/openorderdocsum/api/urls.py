# backend/openorderdocsum/api/urls.py
from django.urls import path
from .views import OpenOrderDetailListView, FetchHanaDataView
from .docsum_views import DocumentSummaryListView, DocumentSummaryDocView
from .openorderdetaildoc import OpenOrderDetailDocView
from .datefilter_views import DateFilterView  # Yeni eklenen view için import

app_name = 'openorderdocsum'

urlpatterns = [
    path('open-order-details/',  OpenOrderDetailListView.as_view(),  name='open-order-details-list', ),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-openorder',),
    path('open-order-detail/<str:belge_no>/', OpenOrderDetailDocView.as_view(), name='openorder-detail-doc', ),
    path('document-summaries/', DocumentSummaryListView.as_view(), name='openorder-docsum-list', ),
    path('document-summary/<str:belge_no>/',DocumentSummaryDocView.as_view(), name='openorder-docsum-detail', ),
    path('date-filter/', DateFilterView.as_view(), name='openorder-date-filter', ),
]

