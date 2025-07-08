# backend/productpicture/api/urls.py
from django.urls import path
from .views import APIRootView, FetchHanaDataView, ProductListView

app_name = 'productpicture'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-data'),
]

