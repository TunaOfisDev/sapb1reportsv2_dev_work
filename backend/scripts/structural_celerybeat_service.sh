#!/bin/bash

# 📄 Klavuz çıktısı
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_celerybeat_service.md"

echo "🚀 Celery Beat servis yapılandırması analiz ediliyor..."

# 📝 Markdown çıktısı oluştur
cat > "$OUTPUT_FILE" <<EOF
# ⏰ Celery Beat Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde zamanlanmış görevleri yöneten **Celery Beat** servisinin systemd yapılandırmasını, başlatma komutunu ve yönetim süreçlerini detaylı olarak açıklar. Amaç, bir sistem yöneticisinin bu servisi baştan kurabilmesi ve sürdürebilmesidir.

---

## 📁 Systemd Servis Dosyası

Servis dosyasını düzenlemek için:
\`\`\`bash
sudo nano /etc/systemd/system/celerybeat.service
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/celerybeat.service 2>/dev/null || echo "❌ /etc/systemd/system/celerybeat.service bulunamadı.")
\`\`\`

---

## 🧠 Celery Beat Başlatma Komutu (Manuel)

Aşağıdaki komut, servis dışında celery beat'i çalıştırmak için kullanılabilir:

\`\`\`bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
celery -A sapreports beat --loglevel=INFO \\
       --scheduler django_celery_beat.schedulers:DatabaseScheduler \\
       --logfile=backend/logs/celerybeat.log
\`\`\`

---

## 📝 Log Dosyaları

Varsayılan log konumları:
\`\`\`bash
$(find /var/www/sapb1reportsv2/backend/logs/ -type f -iname "*beat*.log" 2>/dev/null)
\`\`\`

Canlı log takibi:
\`\`\`bash
journalctl -u celerybeat -f
\`\`\`

---

## ⚙️ Servis Yönetim Komutları

Systemd ile celerybeat servisini kontrol etmek için aşağıdaki komutları kullanabilirsiniz:

\`\`\`bash
# Yapılandırma değişikliklerinden sonra:
sudo systemctl daemon-reexec         # systemd PID & çekirdeğini yeniler (gerekmedikçe kullanılmaz)
sudo systemctl daemon-reload         # .service dosyasında değişiklik sonrası zorunlu

# Servis başlatma/durdurma:
sudo systemctl start celerybeat
sudo systemctl stop celerybeat
sudo systemctl restart celerybeat
sudo systemctl reload celerybeat     # destekliyorsa sadece konfigürasyonları yeniden yükler

# Otomatik başlatma ayarları:
sudo systemctl enable celerybeat
sudo systemctl disable celerybeat
sudo systemctl is-enabled celerybeat

# Servis durumu:
sudo systemctl status celerybeat
\`\`\`

---

## 🛡️ Yedekleme ve Kurtarma

Servis dosyasını yedeklemek için:

\`\`\`bash
sudo cp /etc/systemd/system/celerybeat.service /etc/systemd/system/celerybeat.service.bak
\`\`\`

EOF

echo "✅ Tamamlandı: Celery Beat servis klavuzu '$OUTPUT_FILE' dosyasına kaydedildi."
