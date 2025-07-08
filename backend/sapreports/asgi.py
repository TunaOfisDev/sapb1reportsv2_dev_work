# backend/sapreports/asgi.py

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from dotenv import load_dotenv

# .env dosyasını yükle (güvenli yapılandırma için şart)
load_dotenv(dotenv_path="/var/www/sapb1reportsv2/backend/.env")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

# Django setup
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import supplierpayment.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            supplierpayment.routing.websocket_urlpatterns
        )
    ),
})
