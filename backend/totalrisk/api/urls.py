# backend/totalrisk/api/urls.py
from django.urls import path
from .views import TotalRiskListView, FetchHanaDataView, LastUpdatedView
from .exportxlsx_view import ExportTotalRiskXLSXView

app_name = 'totalrisk'

urlpatterns = [
    path('total-risk/', TotalRiskListView.as_view(), name='total-risk-list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-data'),
    path('last-updated/', LastUpdatedView.as_view(), name='last-updated'),
    path('export-xlsx/', ExportTotalRiskXLSXView.as_view(), name='export-total-risk-xlsx'),
]
