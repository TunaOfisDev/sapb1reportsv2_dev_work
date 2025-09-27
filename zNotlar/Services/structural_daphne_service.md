# 🌐 Daphne Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde ASGI altyapısını çalıştıran **Daphne** servisine ait systemd servis dosyası, socket kullanımı, log konumu ve başlatma komutları gibi yapılandırmaları içerir. Amaç sistem yöneticisinin bu servisi baştan kurabilmesini sağlamaktır.

---

## 🧾 Systemd Servis Dosyası

Servis dosyasını düzenlemek için:
```bash
sudo nano /etc/systemd/system/daphne.service
```

İçerik:
```ini
# /etc/systemd/system/daphne.service

[Unit]
Description=Daphne ASGI Server for sapreports
After=network.target
Requires=redis-server.service
ConditionPathExists=/var/www/sapb1reportsv2/backend

[Service]
User=www-data
Group=sapb1
WorkingDirectory=/var/www/sapb1reportsv2/backend
ExecStart=/var/www/sapb1reportsv2/venv/bin/daphne \
  -u /var/www/sapb1reportsv2/backend/daphne.sock sapreports.asgi:application
Restart=on-failure
RestartSec=10
Environment=DJANGO_SETTINGS_MODULE=sapreports.settings

[Install]
WantedBy=multi-user.target
```

---

## 🔌 Daphne Socket Dosyası (Varsa)

Socket birimi varsa:
```bash
sudo nano /etc/systemd/system/daphne.socket
```

İçerik:
```ini
ℹ️ /etc/systemd/system/daphne.socket bulunamadı. Socket kullanılmıyor olabilir.
```

---

## 🧠 Daphne Başlatma Komutu (Manuel)

Aşağıdaki komut ile Daphne servisi manuel olarak başlatılabilir:

```bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
daphne -u /run/daphne.sock sapreports.asgi:application
```

---

## 📝 Daphne Log Dosyaları

```bash

```

---

## 📂 Daphne Socket (Çalışma Durumu)

```bash
⚠️ Daphne socket (/run/daphne.sock) şu anda yok ya da erişilemiyor.
```

---

## 🔧 Daphne Servis Yönetimi (systemd)

```bash
sudo systemctl daemon-reload

# Servis işlemleri
sudo systemctl start daphne
sudo systemctl stop daphne
sudo systemctl restart daphne
sudo systemctl status daphne
sudo systemctl enable daphne

# Socket birimi varsa:
sudo systemctl start daphne.socket
sudo systemctl status daphne.socket
```

---

## 🛡️ Yedekleme ve Kurtarma

```bash
sudo cp /etc/systemd/system/daphne.service /etc/systemd/system/daphne.service.bak
[ -f /etc/systemd/system/daphne.socket ] && sudo cp /etc/systemd/system/daphne.socket /etc/systemd/system/daphne.socket.bak
```

