#!/bin/bash

# 📄 Çıktı dosyası
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_celery_service.md"

echo "🚀 Celery servis yapılandırması analiz ediliyor..."

# ✅ .env içe aktar (sadece KEY=VALUE satırları, yorumlar hariç)
if [ -f "/var/www/sapb1reportsv2/backend/.env" ]; then
    set -o allexport
    source <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' /var/www/sapb1reportsv2/backend/.env)
    set +o allexport
fi

# 📑 Markdown çıktısını oluştur
cat > "$OUTPUT_FILE" <<EOF
# ⚙️ Celery Servis Yapılandırma ve Sistem Entegrasyon Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde kullanılan **Celery Worker** servisinin nasıl yapılandırıldığını, yönetildiğini ve log takibinin nasıl yapılacağını açıklar. Sistemi sürdürebilir ve yeniden kurabilir olmak için hazırlanmıştır.

---

## 📁 Systemd Servis Dosyası

### 🛰️ celery.service

Servis dosyası yolu:
\`\`\`bash
sudo nano /etc/systemd/system/celery.service
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/celery.service 2>/dev/null || echo "❌ celery.service bulunamadı.")
\`\`\`

---

## 🧠 Manuel Başlatma Komutu

\`\`\`bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
celery -A sapreports worker --loglevel=INFO \\
       --logfile=backend/logs/celery.log
\`\`\`

---

## 📝 Log Dosyası

\`\`\`bash
/var/www/sapb1reportsv2/backend/logs/celery.log
\`\`\`

Canlı log takibi:
\`\`\`bash
journalctl -u celery -f
\`\`\`

---

## 🔧 Servis Yönetim Komutları

\`\`\`bash
# Yapılandırma güncellemesi
sudo systemctl daemon-reload

# Worker işlemleri
sudo systemctl start celery
sudo systemctl restart celery
sudo systemctl status celery
sudo systemctl enable celery
\`\`\`

---

## 📦 Gerekli Python Paketleri

\`\`\`bash
pip install celery redis django-celery-beat loguru
\`\`\`

---

## 🔐 .env Ayarları (örnek)

\`\`\`env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
DJANGO_SETTINGS_MODULE=sapreports.settings
\`\`\`

---

## 🧪 Test Görevi (manuel)

\`\`\`bash
python manage.py shell
>>> from yourapp.tasks import example_task
>>> example_task.delay()
\`\`\`

---

## 🛡️ Yedekleme & Kurtarma

\`\`\`bash
sudo cp /etc/systemd/system/celery.service /etc/systemd/system/celery.service.bak
\`\`\`

EOF

echo "✅ Klavuz başarıyla oluşturuldu: $OUTPUT_FILE"
