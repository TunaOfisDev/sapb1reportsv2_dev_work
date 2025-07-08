Mevcut nginx konfigürasyonunuza 443 portu için SSL konfigürasyonunu ekleyelim. Unix soketleri kullanıldığını görüyorum, bu yapıyı koruyarak HTTPS desteği ekleyelim:

```nginx
# HTTP - mevcut konfigürasyon kalacak
server {
    listen 80;
    server_name localhost 10.130.212.112;
    # HTTP'den HTTPS'e yönlendirme ekleyelim
    return 301 https://$server_name$request_uri;
}

# HTTPS için yeni server bloğu
server {
    listen 443 ssl;
    server_name localhost 10.130.212.112;
    
    # SSL sertifika konfigürasyonu
    ssl_certificate /etc/nginx/ssl/sapb1reportsv2.crt;
    ssl_certificate_key /etc/nginx/ssl/sapb1reportsv2.key;
    
    # SSL güvenlik ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    
    charset utf-8;
    client_max_body_size 100M;
    client_body_buffer_size 256k;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/sapb1reportsv2/frontend/build/static/;
    }

    location /backend_static/ {
        alias /var/www/sapb1reportsv2/backend/backend_static/;
    }

    location /media/ {
        alias /var/www/sapb1reportsv2/backend/media/;
    }

    location /admin {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;
        
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;
        
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location /ws/ {
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/daphne.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location / {
        root /var/www/sapb1reportsv2/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}
```

SSL sertifikalarını oluşturmak için:
```bash
# SSL sertifika dizini oluştur
sudo mkdir -p /etc/nginx/ssl

# Self-signed sertifika oluştur
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/sapb1reportsv2.key \
    -out /etc/nginx/ssl/sapb1reportsv2.crt \
    -subj "/C=TR/ST=Istanbul/L=Istanbul/O=TunaOfis/CN=reportserver"

# Sertifika dosyalarının yetkilerini ayarla
sudo chmod 600 /etc/nginx/ssl/sapb1reportsv2.key
sudo chmod 644 /etc/nginx/ssl/sapb1reportsv2.crt

# Nginx konfigürasyonunu test et
sudo nginx -t

# Nginx'i yeniden başlat
sudo systemctl restart nginx
```

Bu konfigürasyon:
1. HTTP'den HTTPS'e otomatik yönlendirme yapar
2. Mevcut unix socket yapısını korur
3. Güçlü SSL güvenlik ayarları içerir
4. Tüm mevcut proxy ve timeout ayarlarını korur

SSL kurulumundan sonra hem HTTP (80) hem de HTTPS (443) portlarının açık olduğunu kontrol edebilirsiniz:
```bash
sudo netstat -tulpn | grep nginx
```