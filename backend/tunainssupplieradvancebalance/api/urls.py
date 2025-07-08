# backend/tunainssupplieradvancebalance/api/urls.py
from django.urls import path
from .views import TotalRiskListView, FetchHanaDataView, LastUpdatedView
from .exportxlsx_view import ExportTotalRiskXLSXView

app_name = 'tunainssupplieradvancebalance'

urlpatterns = [
    path('total-risk/', TotalRiskListView.as_view(), name='tunains-supplieradvance-total-risk'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='tunains-supplieradvance-fetch-hana'),
    path('last-updated/', LastUpdatedView.as_view(), name='tunains-supplieradvance-last-updated'),
    path('export-xlsx/', ExportTotalRiskXLSXView.as_view(), name='export-supplier-advance-xlsx'), 
]

