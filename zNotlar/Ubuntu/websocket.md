### Django, WebSocket, Channels, Redis ve Celery Kullanımı

Projenizde WebSocket, Django Channels, Redis ve Celery kullanımı ile ilgili daha derin bir teknik bilgi sağlamak için bu servislerin nasıl çalıştığını ve birbirleriyle nasıl etkileşime girdiklerini açıklamak istiyorum.

#### 1. Django Channels ve WebSocket

**Django Channels**, Django uygulamanıza WebSocket ve diğer asenkron protokol desteği ekler. WebSocket, gerçek zamanlı iletişim sağlayan bir protokoldür.

**Channels Mimarisi:**
- **ASGI (Asynchronous Server Gateway Interface):** Django Channels, ASGI'yi kullanarak çalışır. ASGI, asenkron Python web uygulamaları için bir standarttır.
- **Consumer:** WebSocket bağlantılarını yönetir. WebSocketConsumer veya AsyncWebsocketConsumer sınıflarını kullanarak özel tüketiciler oluşturabilirsiniz.

**Örnek Consumer:**
```python
# backend/supplierpayment/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SupplierPaymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        await self.send(text_data=json.dumps({'message': message}))
```

**Routing:**
```python
# backend/supplierpayment/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/supplierpayment/$', consumers.SupplierPaymentConsumer.as_asgi()),
]
```

**ASGI Konfigürasyonu:**
```python
# backend/sapreports/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import supplierpayment.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            supplierpayment.routing.websocket_urlpatterns
        )
    ),
})
```

#### 2. Redis

Redis, hızlı ve esnek bir in-memory veri yapısı deposudur. Django Channels ve Celery için mesaj kuyruklama ve önbellekleme işlevleri sağlar.

**Redis Ayarları:**
```python
# settings.py
REDIS_HOST = config('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = config('REDIS_PORT', default=6379)
REDIS_PASSWORD = config('REDIS_PASS', default='Tuna2023*')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1"],
        },
    },
}
```

#### 3. Celery

Celery, dağıtık görev kuyrukları için popüler bir sistemdir. Uzun süren işlemleri asenkron olarak çalıştırır.

**Celery Yapılandırması:**
```python
# backend/sapreports/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

app = Celery('sapreports')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

**Celery Ayarları:**
```python
# settings.py
CELERY_BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
```

**Görev Tanımlama:**
```python
# backend/supplierpayment/tasks.py
from celery import shared_task
from .models import SupplierPayment

@shared_task
def calculate_supplier_payments():
    # Hesaplama işlemleri
    pass
```

#### 4. WebSocket İstemcisi

React kullanarak WebSocket bağlantısı kurabilirsiniz. Örnek bir React WebSocket istemcisi:
```javascript
import React, { useEffect, useState } from 'react';

const WebSocketComponent = () => {
  const [message, setMessage] = useState('');
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws/supplierpayment/');
    setWs(websocket);

    websocket.onmessage = function(event) {
      const data = JSON.parse(event.data);
      setMessage(data.message);
    };

    websocket.onclose = function(event) {
      console.error('WebSocket closed unexpectedly');
    };

    return () => {
      websocket.close();
    };
  }, []);

  const sendMessage = () => {
    if (ws) {
      ws.send(JSON.stringify({ message: 'Hello WebSocket' }));
    }
  };

  return (
    <div>
      <button onClick={sendMessage}>Send Message</button>
      <p>Message: {message}</p>
    </div>
  );
};

export default WebSocketComponent;
```

Bu bilgilerle, projenizde WebSocket, Django Channels, Redis ve Celery'nin nasıl çalıştığını ve nasıl yapılandırıldığını anlayabilirsiniz. Bu servislerin mimarisini ve işleyişini anlamak, projenizin performansını optimize etmenize ve daha etkin kullanmanıza yardımcı olacaktır. Eğer daha fazla detaya ihtiyacınız olursa, belirli konular hakkında daha derinlemesine bilgi sağlayabilirim.