# backend/girsbergerordropqt/api/urls.py
from django.urls import path
from .views import OrdrDetailOpqtListView, FetchHanaDataView

app_name = 'girsbergerordropqt'

urlpatterns = [
    path('ordr_detail_opqt/', OrdrDetailOpqtListView.as_view(), name='ordr_detail_opqt_list'),
    path('fetch_hana_data/', FetchHanaDataView.as_view(), name='fetch-hana-girsbergerordropqt'),
    
]
