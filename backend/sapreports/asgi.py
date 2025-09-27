# path: backend/sapreports/asgi.py

import os
import django
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

# Ortam değişkenlerini .env'den yükle
load_dotenv(dotenv_path="/var/www/sapb1reportsv2/backend/.env")

# Django ayarları
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')
django.setup()

# Channels importları
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# WebSocket route dosyalarını içeri al
import supplierpayment.routing
import stockcardintegration.routing

# Uygulama router yapısı
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            supplierpayment.routing.websocket_urlpatterns +
            stockcardintegration.routing.websocket_urlpatterns
        )
    ),
})

