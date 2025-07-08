# ⚙️ Celery Servis Yapılandırma ve Sistem Entegrasyon Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde kullanılan **Celery Worker** servisinin nasıl yapılandırıldığını, yönetildiğini ve log takibinin nasıl yapılacağını açıklar. Sistemi sürdürebilir ve yeniden kurabilir olmak için hazırlanmıştır.

---

## 📁 Systemd Servis Dosyası

### 🛰️ celery.service

Servis dosyası yolu:
```bash
sudo nano /etc/systemd/system/celery.service
```

İçerik:
```ini
[Unit]
Description=Celery Worker for sapb1reportsv2
After=network.target

[Service]
Type=simple
User=www-data
Group=sapb1
WorkingDirectory=/var/www/sapb1reportsv2/backend
EnvironmentFile=/var/www/sapb1reportsv2/backend/.env
Environment=PYTHONPATH=/var/www/sapb1reportsv2/backend
ExecStart=/var/www/sapb1reportsv2/venv/bin/celery -A sapreports worker \
    --loglevel=ERROR \
    --logfile=/var/www/sapb1reportsv2/backend/logs/celery.log \
    -n worker1@sapb1-pro-srv
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

---

## 🧠 Manuel Başlatma Komutu

```bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
celery -A sapreports worker --loglevel=INFO \
       --logfile=backend/logs/celery.log
```

---

## 📝 Log Dosyası

```bash
/var/www/sapb1reportsv2/backend/logs/celery.log
```

Canlı log takibi:
```bash
journalctl -u celery -f
```

---

## 🔧 Servis Yönetim Komutları

```bash
# Yapılandırma güncellemesi
sudo systemctl daemon-reload

# Worker işlemleri
sudo systemctl start celery
sudo systemctl restart celery
sudo systemctl status celery
sudo systemctl enable celery
```

---

## 📦 Gerekli Python Paketleri

```bash
pip install celery redis django-celery-beat loguru
```

---

## 🔐 .env Ayarları (örnek)

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
DJANGO_SETTINGS_MODULE=sapreports.settings
```

---

## 🧪 Test Görevi (manuel)

```bash
python manage.py shell
>>> from yourapp.tasks import example_task
>>> example_task.delay()
```

---

## 🛡️ Yedekleme & Kurtarma

```bash
sudo cp /etc/systemd/system/celery.service /etc/systemd/system/celery.service.bak
```

