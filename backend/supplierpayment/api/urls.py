# backend/supplierpayment/api/urls.py // test git
from django.urls import path
from .views import SupplierPaymentView, FetchHanaSupplierPaymentDataView, LastUpdatedSupplierPaymentView, FetchHanaDbDataView
from .closinginvoice_view import SupplierPaymentSimulationView
from .combinedservice import CombinedServiceView
from ..api import combinedservice

app_name = 'supplierpayment'

urlpatterns = [
    path('supplier_payments/', SupplierPaymentView.as_view(), name='supplier_payments'),
    path('fetch_supplier_payments/', FetchHanaSupplierPaymentDataView.as_view(), name='fetch_supplier_payments'),
    path('local_db_closing_invoice/', SupplierPaymentSimulationView.as_view(), name='local_db_closing_invoice'),
    path('fetch_hana_db_combined_service/', CombinedServiceView.as_view(), name='fetch_hana_db_combined_service'),
    path('last_updated_supplier_payment/', LastUpdatedSupplierPaymentView.as_view(), name='last_updated_supplier_payment'),
    path('task_status/<str:task_id>/', combinedservice.TaskStatusView.as_view(), name='task_status'),
    path('fetch_hana_db/', FetchHanaDbDataView.as_view(), name='fetch_hana_db'),  # Yeni endpoint
]