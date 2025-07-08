# backend/logocustomerbalance/urls.py
from django.urls import path
from .views import CustomerBalanceListView, FetchLogoDataView

app_name = 'logocustomerbalance'

urlpatterns = [
    path('customer-balance/', CustomerBalanceListView.as_view(),
         name='customer-balance-list'),

    path('fetch-logo-data/', FetchLogoDataView.as_view(),
         name='fetch-logo-customer-data'),          # <- güncellendi
]
