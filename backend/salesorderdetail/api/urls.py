# backend/salesorderdetail/api/urls.py
from django.urls import path
from .views import SalesOrderDetailView, SalesOrderMasterView, FetchHanaSalesOrderDataView

urlpatterns = [
    path('master/', SalesOrderMasterView.as_view(), name='sales_order_master_list'),
    path('master/<int:pk>/', SalesOrderMasterView.as_view(), name='sales_order_master_detail'),
    path('detail/', SalesOrderDetailView.as_view(), name='sales_order_detail_list'),
    path('detail/<int:pk>/', SalesOrderDetailView.as_view(), name='sales_order_detail_detail'),
    path('detail/search/', SalesOrderDetailView.as_view(), name='sales_order_detail_search'),
    path('fetch-sales-order-data/', FetchHanaSalesOrderDataView.as_view(), name='fetch_sales_order_data'),
]