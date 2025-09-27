# 🐉 Gunicorn Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde Django WSGI sunucusu olarak çalışan **Gunicorn** servisinin systemd yapılandırmalarını, socket kullanımını, başlatma komutlarını ve log dosyalarını içerir. Sistem üzerinde değişiklik yapılmaz, sadece analiz yapılır.

---

## 🧾 Systemd Servis Dosyası

Servis dosyasını düzenlemek için:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

İçerik:
```ini
[Unit]
Description=Gunicorn daemon for sapb1reportsv2
After=network.target

[Service]
User=www-data
Group=sapb1
WorkingDirectory=/var/www/sapb1reportsv2/backend
EnvironmentFile=/var/www/sapb1reportsv2/backend/.env
Environment=PYTHONPATH=/var/www/sapb1reportsv2/backend
ExecStart=/var/www/sapb1reportsv2/venv/bin/gunicorn \
    --timeout 180 \
    --access-logfile /var/www/sapb1reportsv2/backend/logs/gunicorn-access.log \
    --error-logfile /var/www/sapb1reportsv2/backend/logs/gunicorn-error.log \
    --workers 3 \
    --bind unix:/var/www/sapb1reportsv2/backend/gunicorn.sock \
    sapreports.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🔌 Gunicorn Socket Dosyası (Varsa)

Socket dosyası varsa:
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

İçerik:
```ini
ℹ️ /etc/systemd/system/gunicorn.socket bulunamadı. Socket kullanılmıyor olabilir.
```

---

## 🧠 Gunicorn Başlatma Komutu (Manuel)

Aşağıdaki gibi çalıştırılabilir:

```bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
gunicorn sapreports.wsgi:application \
  --bind unix:/run/gunicorn.sock \
  --workers 3 \
  --access-logfile backend/logs/gunicorn_access.log \
  --error-logfile backend/logs/gunicorn_error.log
```

---

## 📝 Gunicorn Log Dosyaları

```bash

```

Canlı log takibi için:
```bash
journalctl -u gunicorn -f
```

---

## 📂 Gunicorn Socket Dosyası (Runtime)

```bash
Gunicorn socket (/run/gunicorn.sock) şu anda yok ya da erişilemiyor.
```

---

## 🔧 Gunicorn Servis Yönetimi (systemd)

```bash
sudo systemctl daemon-reload

# Servis işlemleri
sudo systemctl start gunicorn
sudo systemctl stop gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
sudo systemctl enable gunicorn

# Socket varsa:
sudo systemctl start gunicorn.socket
sudo systemctl status gunicorn.socket
```

---

## 🛡️ Yedekleme & Kurtarma

```bash
sudo cp /etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service.bak
[ -f /etc/systemd/system/gunicorn.socket ] && sudo cp /etc/systemd/system/gunicorn.socket /etc/systemd/system/gunicorn.socket.bak
```

