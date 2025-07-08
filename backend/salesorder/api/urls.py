# backend/salesorder/api/urls.py
from django.urls import path
from .views import SalesOrderListView, FetchHanaDataView
from .customersales_view import CustomerSalesOrderListView, FetchHanaCustomerSalesDataView, LastUpdatedView
from .filter_views import DynamicFilterView, SalesReportView
from .exportxlsx_view import ExportXLSXView

app_name = 'salesorder'

urlpatterns = [
    path('salesorders/', SalesOrderListView.as_view(), name='sales-order-list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-salesorder'),
    path('dynamic-filter/', DynamicFilterView.as_view(), name='dynamic-filter'),  
    path('sales-report/', SalesReportView.as_view(), name='sales-report'), 
    # Yeni eklenen CustomerSalesOrder için endpoint'ler
    path('customer-salesorders/', CustomerSalesOrderListView.as_view(), name='customer-sales-order-list'),
    path('fetch-hana-customersales-data/', FetchHanaCustomerSalesDataView.as_view(), name='fetch-hana-customersales-data'),
    path('last-updated/', LastUpdatedView.as_view(), name='last-updated'),
    path('export-xlsx/', ExportXLSXView.as_view(), name='export-salesorder-xlsx'),

]
