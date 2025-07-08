# backend/tunainstotalrisk/api/urls.py
from django.urls import path
from .views import TunainsTotalRiskListView, FetchHanaDataView, LastUpdatedView
from .exportxlsx_view import ExportTunainsTotalRiskXLSXView

app_name = 'tunainstotalrisk'

urlpatterns = [
    path('total-risk/', TunainsTotalRiskListView.as_view(), name='tunainstotalrisk-total-risk'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='tunainstotalrisk-fetch-hana-data'),
    path('last-updated/', LastUpdatedView.as_view(), name='tunainstotalrisk-last-updated'),
    path('export-xlsx/', ExportTunainsTotalRiskXLSXView.as_view(), name='tunainstotalrisk-export-xlsx'),
    
]
