sudo nano /etc/nginx/sites-available/sapreports
user@reportserver:~$ cat /etc/nginx/sites-available/sapreports
server {
    listen 80;
    server_name localhost 10.130.212.112;
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
        
        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;

        # Proxy Buffer Ayarları
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;

        # Proxy Buffer Ayarları
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

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;

        # Proxy Buffer Ayarları
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location / {
        root /var/www/sapb1reportsv2/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}

























********************************
server {
    listen 80;
    server_name localhost 10.130.212.112;
    charset utf-8;

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

    # Django admin paneli ve diğer Django yolları için
    location /admin {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;
    }

    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
    }

    location /ws/ {
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/daphne.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $http_connection;
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /var/www/sapb1reportsv2/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}












***********************************
sudo apt update
sudo apt install nginx


*** /var/www/sapb1reportsv2

localhost:8000

sudo tail -f /var/log/nginx/error.log

sudo ln -s /etc/nginx/sites-available/sapreports /etc/nginx/sites-enabled/

sudo chown -R user:user /etc/nginx/sites-available/sapreports 

kopyalama icin
sudo cat /etc/nginx/sites-available/sapreports

sudo nano /etc/nginx/sites-available/sapreports                                     
# /etc/nginx/sites-available/sapreports

server {
    listen 80;
    server_name localhost 10.130.212.112;
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
        
        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;

        # Proxy Buffer Ayarları
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;

        # Proxy Buffer Ayarları
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

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;

        # Proxy Buffer Ayarları
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    location / {
        root /var/www/sapb1reportsv2/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}



sudo nginx -t
sudo systemctl restart nginx
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

********

curl -X POST -d "username=user&password=Tuna2023" http://10.130.212.112/api/v2/authcentral/login/
********

sudo chown -R www-data:www-data /var/www/sapb1reportsv2
sudo chmod -R u+w /var/www/sapb1reportsv2


sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
After=network.target                                       
                                       
[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sapb1reportsv2/backend
ExecStart=/var/www/sapb1reportsv2/venv/bin/gunicorn --workers 3 --bind unix:/var/www/sapb1reportsv2/backend/gunicorn.sock sapreports.wsgi:application --timeout 300 --forwarded-allow-ips='*' --log-file=/var/www/sapb1reportsv2/backend/logs/gunicorn.log


[Install]
WantedBy=multi-user.target



****
sudo systemctl daemon-reload
sudo systemctl restart gunicorn


*********************************

Projeyi canlıya almak için aşağıdaki adımları takip edebilirsiniz. Lütfen bu adımları uygulamadan önce tüm yedekleme işlemlerinizi tamamladığınızdan emin olun:

**Gunicorn Kurulumu ve Ayarları:**

1. Virtual environment'ınızı aktif edin:

   ```
   source /home/user/sapb1reportsV2/venv/bin/activate
   ```

2. Gunicorn'u kurun (eğer daha önce kurulmadıysa):

   ```
   pip install gunicorn
   ```

3. Gunicorn için bir systemd servis dosyası oluşturun (`/etc/systemd/system/gunicorn.service`):

/etc/systemd/system/gunicorn.service                                                                                                                
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sapb1reportsv2/backend
ExecStart=/var/www/sapb1reportsv2/venv/bin/gunicorn --workers 3 --bind unix:/var/www/sapb1reportsv2/backend/gunicorn.sock sapreports.wsgi:application --log-file=/var/www/sapb1reportsv2/backend/logs/gunicorn.log

[Install]
WantedBy=multi-user.target

   ```

   *Bu dosyayı oluşturduktan sonra, daemonu yeniden yükleyin ve gunicorn servisini başlatın:*

   ```
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

**Nginx Ayarları:**

1. `/etc/nginx/sites-available/sapreports` dosyasını düzenleyin:

   ```nginx
  server {
    listen 80;
    server_name 172.31.13.65;

    # React Uygulamasını Sunmak için Root Yolu ve İndex Dosyası
    root /home/user/sapb1reportsV2/frontend/build;
    index index.html;

    # Ana URL'de (Örneğin http://172.31.13.65/) React Uygulamasını Göster
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Django Uygulamasına Yönlendirme (Gunicorn)
    location /api {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }

    # Django Admin Paneline Yönlendirme
    location /admin {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }

    # Django Static Dosyaları
    location /static/ {
        alias /home/user/sapb1reportsV2/backend/staticfiles/;
    }

    # Django Media Dosyaları
    location /media/ {
        alias /home/user/sapb1reportsV2/backend/media/;
    }

    # Ürün Resimleri için Özel Yol
    location /product_pictures/ {
        alias /mnt/product_picture/;
        autoindex off;
    }
}


   ```

   *Bu dosyayı oluşturduktan veya güncelledikten sonra, Nginx yapılandırmasını kontrol edin ve Nginx servisini yeniden başlatın:*

   ```
   sudo nginx -t
   sudo systemctl restart nginx
   ```

2. Eğer React frontend için bir yapılandırma gerekiyorsa, Nginx'e aşağıdaki gibi bir `location` bloğu ekleyebilirsiniz:

   ```nginx
   location / {
       root /home/user/sapb1reportsV2/frontend/build;
       try_files $uri /index.html;
   }
   ```

**Django Ayarları:**

- `settings.py` dosyanızda `ALLOWED_HOSTS` içerisine sunucunuzun IP adresini ve diğer domain adlarını eklediğinizden emin olun.
- Debug modu kapalı olduğundan (`DEBUG = False`) ve gizli anahtarınızın (`SECRET_KEY`) güvenli bir şekilde saklandığından emin olun.

Bu işlemler tamamlandıktan sonra, Django projenizin canlıda düzgün bir şekilde çalışıp çalışmadığını kontrol edin. Herhangi bir hata alırsanız, sistem loglarına ve Nginx/Gunicorn log dosyalarına bakarak hatanın kaynağını belirleyin ve gerekli düzeltmeleri yapın.


sudo nano 
Gunicorn Loglarını Kontrol Edin: Gunicorn log dosyanızı (/var/www/sapb1reportsv2/backend/logs/gunicorn.log) kontrol ederek, çalışma zamanı hatalarını ve diğer önemli bilgileri inceleyin.

Nginx Loglarını Kontrol Edin: Nginx'in hata loglarını kontrol ederek (/var/log/nginx/error.log), Nginx ile ilgili olası hataları tespit edin.

04/10/2024
nginx settings backup

server {
    listen 80;
    server_name localhost 10.130.212.112;
    charset utf-8;

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
        
        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;
    }

    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/sapb1reportsv2/backend/gunicorn.sock;

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;
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

        # Timeout ayarları
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        send_timeout 600s;
    }

    location / {
        root /var/www/sapb1reportsv2/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}