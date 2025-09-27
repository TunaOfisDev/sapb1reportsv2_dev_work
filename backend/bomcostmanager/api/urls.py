# backend/bomcostmanager/api/urls.py

from django.urls import path
from .bomcomponent_views import (
    BOMComponentListView,
    BOMComponentFetchView,
    BOMComponentLastUpdatedView,
)
from .bomproduct_views import (
    BOMProductListView,
    BOMProductFetchView,
    BOMProductLastUpdatedView,
    BOMProductDetailView,
)
from .bcm_rate_views import (
    ExchangeRateView,
    SingleExchangeRateView,
    ExchangeRateLastUpdatedView
)

app_name = "bomcostmanager_api"

urlpatterns = [
    # BOMComponent API Endpoint'leri
    path('bomcomponents/list/', BOMComponentListView.as_view(), name='bomcomponent-list'),
    path('bomcomponents/fetch/', BOMComponentFetchView.as_view(), name='bomcomponent-fetch'),
    path('bomcomponents/last-updated/', BOMComponentLastUpdatedView.as_view(), name='bomcomponent-last-updated'),

    # BOMProduct API Endpoint'leri
    path('bomproducts/', BOMProductListView.as_view(), name='bomproduct-list'),
    path('bomproducts/fetch/', BOMProductFetchView.as_view(), name='bomproduct-fetch'),
    path('bomproducts/last-updated/', BOMProductLastUpdatedView.as_view(), name='bomproduct-last-updated'),
    path('bomproducts/<str:item_code>/', BOMProductDetailView.as_view(), name='bomproduct-detail'),

    # kur api
    path('exchange-rates/', ExchangeRateView.as_view(), name='exchange-rates'),
    path('exchange-rates/<str:currency_code>/', SingleExchangeRateView.as_view(), name='exchange-rate-detail'),
    path('exchange-rates-last-updated/', ExchangeRateLastUpdatedView.as_view(), name='exchange-rates-last-updated'),
]




