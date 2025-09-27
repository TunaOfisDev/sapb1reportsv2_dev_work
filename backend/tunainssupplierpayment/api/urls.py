# backend/tunainssupplierpayment/api/urls.py
from django.urls import path
from .views import SupplierPaymentView, FetchHanaSupplierPaymentDataView, LastUpdatedSupplierPaymentView, FetchHanaDbDataView
from .closinginvoice_view import SupplierPaymentSimulationView
from .combinedservice import CombinedServiceView
from ..api import combinedservice

app_name = 'tunainssupplierpayment'

urlpatterns = [
    path('supplier_payments/', SupplierPaymentView.as_view(), name='tunains-supplier-payments'),
    path('fetch_supplier_payments/', FetchHanaSupplierPaymentDataView.as_view(), name='tunains-fetch-supplier-payments'),
    path('local_db_closing_invoice/', SupplierPaymentSimulationView.as_view(), name='tunains-local-db-closing-invoice'),
    path('fetch_hana_db_combined_service/', CombinedServiceView.as_view(), name='tunains-hana-combined-service'),
    path('last_updated_supplier_payment/', LastUpdatedSupplierPaymentView.as_view(), name='tunains-last-updated-supplier-payment'),
    path('task_status/<str:task_id>/', combinedservice.TaskStatusView.as_view(), name='tunains-task-status'),
    path('fetch_hana_db/', FetchHanaDbDataView.as_view(), name='tunains-fetch-hana-db'),  
]
