# backend/customersales/api/urls.py

from django.urls import path
from . import views

app_name = 'customersales_api'

urlpatterns = [
    # Rapor verilerini (filtreli, özetli) göstermek için KULLANILACAK TEK endpoint.
    path('report/', views.CustomerSalesDataView.as_view(), name='report-data'),
    
    # HANA'dan veri çekme işlemini tetiklemek için KULLANILACAK TEK endpoint.
    path('fetch-hana-data/', views.FetchHanaDataView.as_view(),  name='fetch-hana-data'),
]