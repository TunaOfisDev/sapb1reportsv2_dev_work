# path: backend/stockcardintegration/routing.py

from django.urls import re_path
from .ws.consumers import ProductPriceListConsumer

websocket_urlpatterns = [
    re_path(r'^ws/price-list/$', ProductPriceListConsumer.as_asgi()),
]
