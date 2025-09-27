# backend/customercollection/api/urls.py
from django.urls import path
from .views import CustomerCollectionView, FetchHanaCustomerCollectionDataView, LastUpdatedCustomerCollectionView
from .closinginvoice_view import CustomerCollectionSimulationView
from .combinedservice import CombinedServiceView

app_name = 'customercollection'

urlpatterns = [
    path('customer_collection/', CustomerCollectionView.as_view(), name='customer_collection'),
    path('fetch_customer_collection/', FetchHanaCustomerCollectionDataView.as_view(), name='fetch_customer_collection'),
    path('local_db_closing_invoice/', CustomerCollectionSimulationView.as_view(), name='local_db_closing_invoice'),
    path('fetch_hana_db_combined_service/', CombinedServiceView.as_view(), name='fetch_hana_db_combined_service'),
    path('last_updated_customer_collection/', LastUpdatedCustomerCollectionView.as_view(), name='last_updated_customer_collection'),
]


