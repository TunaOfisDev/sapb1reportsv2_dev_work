Daphne'yi yüklemeniz ve ardından ASGI uygulamanızı çalıştırmanız gerekiyor. Daphne, Django Channels ile çalışan bir ASGI sunucusudur ve WebSocket bağlantılarını kabul edebilmek için kullanılır.

### 1. Daphne'yi Yükleyin

Daphne'yi yüklemek için aşağıdaki komutu kullanabilirsiniz:

```bash
sudo apt install daphne
```

Alternatif olarak, pip kullanarak da yükleyebilirsiniz:

```bash
pip install daphne
```

### 2. Daphne Sunucusunu Başlatın

Daphne yüklendikten sonra, aşağıdaki komutu kullanarak Daphne sunucusunu başlatabilirsiniz:

```bash
daphne -b 0.0.0.0 -p 8001 sapreports.asgi:application
```

### 3. Nginx Konfigürasyonunu Kontrol Edin

Nginx konfigürasyon dosyanızın `/ws/` konumunun Daphne'ye yönlendirildiğinden emin olun. Aşağıda doğru bir Nginx konfigürasyonu örneği verilmiştir:

```nginx
server {
    listen 80;
    server_name localhost 10.130.212.112;
    charset utf-8;

    location /ws/ {
        proxy_pass http://127.0.0.1:8001;  # ASGI/Daphne sunucusunun çalıştığı port
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Diğer konfigürasyonlar...
}
```

### 4. Django Channels ve Redis Ayarlarını Kontrol Edin

Django Channels ve Redis ayarlarının doğru olduğundan emin olun:

```python
# settings.py

ASGI_APPLICATION = 'sapreports.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [{
                'address': (REDIS_HOST, REDIS_PORT),
                'password': REDIS_PASSWORD,
                'db': 2,  # Channels için 2 numaralı database
            }],
        },
    },
}
```

### 5. WebSocket URL'sini Kontrol Edin

WebSocket bağlantısı kurmaya çalıştığınız JavaScript dosyasındaki URL'nin doğru olduğundan emin olun:

```javascript
const socket = new WebSocket('ws://10.130.212.112/ws/supplierpayment/');
socket.onopen = function(e) {
  console.log("[open] Connection established");
  console.log("Sending to server");
  socket.send("My name is John");
};

socket.onmessage = function(event) {
  console.log(`[message] Data received from server: ${event.data}`);
};

socket.onclose = function(event) {
  if (event.wasClean) {
    console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
  } else {
    console.log('[close] Connection died');
  }
};

socket.onerror = function(error) {
  console.log(`[error] ${error.message}`);
};
```

Bu adımları takip ederek WebSocket bağlantı sorununu çözebilirsiniz. Daphne'nin kurulumundan sonra sunucuyu başlatmak ve Nginx yapılandırmasının doğru olduğundan emin olmak genellikle sorunu çözer. Eğer hala sorun yaşıyorsanız, daha fazla ayrıntı veya hata mesajlarını paylaşarak yardımcı olabilirim.
Daphne için daphne.service dosyasını Ubuntu'da oluşturmak için aşağıdaki adımları izleyebilirsiniz:
1. daphne.service Dosyasını Oluşturma

Öncelikle, daphne.service dosyasını oluşturun ve içerisine gerekli yapılandırmayı ekleyin.
Adım 1: Dosyayı oluşturma

Terminalde aşağıdaki komutu çalıştırarak boş bir dosya oluşturun ve düzenleyici ile açın:

bash

sudo nano /etc/systemd/system/daphne.service

Adım 2: Dosya içeriğini ekleme

Açılan düzenleyiciye aşağıdaki içeriği ekleyin:

ini

[Unit]
Description=Daphne daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sapb1reportsv2/backend
ExecStart=/var/www/sapb1reportsv2/venv/bin/daphne -u /var/www/sapb1reportsv2/backend/daphne.sock sapreports.asgi:application

[Install]
WantedBy=multi-user.target

Bu içeriği ekledikten sonra, Ctrl+O tuşlarına basarak dosyayı kaydedin ve ardından Ctrl+X tuşlarına basarak düzenleyiciden çıkın.
2. Servis Dosyasını Yükleme ve Başlatma
Adım 1: Systemd daemon'ı yeniden yükleyin

Aşağıdaki komutu çalıştırarak systemd daemon'ını yeniden yükleyin:

bash

sudo systemctl daemon-reload

Adım 2: Daphne servisini etkinleştirme

Daphne servisini sistemin açılışında otomatik olarak başlatılacak şekilde etkinleştirin:

bash

sudo systemctl enable daphne

Adım 3: Daphne servisini başlatma

Daphne servisini hemen başlatın:

bash

sudo systemctl start daphne

3. Servis Durumunu Kontrol Etme

Daphne servisinin durumunu kontrol ederek her şeyin düzgün çalıştığından emin olun:

bash

sudo systemctl status daphne

Eğer servis düzgün çalışıyorsa, active (running) mesajını görmelisiniz. Eğer bir hata varsa, hata mesajlarını inceleyerek sorunu belirleyebilirsiniz.