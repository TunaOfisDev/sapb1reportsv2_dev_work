#!/bin/bash

# 📄 Çıktı dosyası
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_gunicorn_service.md"

echo "🚀 Gunicorn servis yapılandırması analiz ediliyor..."

# 📑 Markdown içeriği
cat > "$OUTPUT_FILE" <<EOF
# 🐉 Gunicorn Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde Django WSGI sunucusu olarak çalışan **Gunicorn** servisinin systemd yapılandırmalarını, socket kullanımını, başlatma komutlarını ve log dosyalarını içerir. Sistem üzerinde değişiklik yapılmaz, sadece analiz yapılır.

---

## 🧾 Systemd Servis Dosyası

Servis dosyasını düzenlemek için:
\`\`\`bash
sudo nano /etc/systemd/system/gunicorn.service
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/gunicorn.service 2>/dev/null || echo "❌ /etc/systemd/system/gunicorn.service bulunamadı.")
\`\`\`

---

## 🔌 Gunicorn Socket Dosyası (Varsa)

Socket dosyası varsa:
\`\`\`bash
sudo nano /etc/systemd/system/gunicorn.socket
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/gunicorn.socket 2>/dev/null || echo "ℹ️ /etc/systemd/system/gunicorn.socket bulunamadı. Socket kullanılmıyor olabilir.")
\`\`\`

---

## 🧠 Gunicorn Başlatma Komutu (Manuel)

Aşağıdaki gibi çalıştırılabilir:

\`\`\`bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
gunicorn sapreports.wsgi:application \\
  --bind unix:/run/gunicorn.sock \\
  --workers 3 \\
  --access-logfile backend/logs/gunicorn_access.log \\
  --error-logfile backend/logs/gunicorn_error.log
\`\`\`

---

## 📝 Gunicorn Log Dosyaları

\`\`\`bash
$(find /var/www/sapb1reportsv2/backend/logs/ -type f -name "gunicorn_*.log" 2>/dev/null || echo "Log klasöründe gunicorn_*.log bulunamadı.")
\`\`\`

Canlı log takibi için:
\`\`\`bash
journalctl -u gunicorn -f
\`\`\`

---

## 📂 Gunicorn Socket Dosyası (Runtime)

\`\`\`bash
$(ls -la /run/gunicorn.sock 2>/dev/null || echo "Gunicorn socket (/run/gunicorn.sock) şu anda yok ya da erişilemiyor.")
\`\`\`

---

## 🔧 Gunicorn Servis Yönetimi (systemd)

\`\`\`bash
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
\`\`\`

---

## 🛡️ Yedekleme & Kurtarma

\`\`\`bash
sudo cp /etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service.bak
[ -f /etc/systemd/system/gunicorn.socket ] && sudo cp /etc/systemd/system/gunicorn.socket /etc/systemd/system/gunicorn.socket.bak
\`\`\`

EOF

echo "✅ Tamamlandı: Gunicorn servis klavuzu '$OUTPUT_FILE' dosyasına kaydedildi."
