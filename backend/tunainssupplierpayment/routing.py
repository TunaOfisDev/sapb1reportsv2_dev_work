# backend/tunainssupplierpayment/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tunainssupplierpayment/$', consumers.SupplierPaymentConsumer.as_asgi()),
]
