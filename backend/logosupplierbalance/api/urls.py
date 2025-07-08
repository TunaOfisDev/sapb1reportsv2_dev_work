# backend/logosupplierbalance/api/urls.py
from django.urls import path
from .views import SupplierBalanceListView, FetchLogoDataView

app_name = 'logosupplierbalance'

urlpatterns = [
    path('supplier-balance/', SupplierBalanceListView.as_view(),
         name='supplier-balance-list'),

    path('fetch-logo-data/', FetchLogoDataView.as_view(),
         name='fetch-logo-supplier-data'),          # <- güncellendi
]

