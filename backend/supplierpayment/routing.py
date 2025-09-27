# supplierpayment/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/supplierpayment/$', consumers.SupplierPaymentConsumer.as_asgi()),
]
