#!/bin/bash

# 📄 Çıktı dosyası yolu
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_daphne_service.md"

echo "🚀 Daphne servis yapılandırması analiz ediliyor..."

# 📝 Markdown çıktısını oluştur
cat > "$OUTPUT_FILE" <<EOF
# 🌐 Daphne Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde ASGI altyapısını çalıştıran **Daphne** servisine ait systemd servis dosyası, socket kullanımı, log konumu ve başlatma komutları gibi yapılandırmaları içerir. Amaç sistem yöneticisinin bu servisi baştan kurabilmesini sağlamaktır.

---

## 🧾 Systemd Servis Dosyası

Servis dosyasını düzenlemek için:
\`\`\`bash
sudo nano /etc/systemd/system/daphne.service
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/daphne.service 2>/dev/null || echo "❌ /etc/systemd/system/daphne.service bulunamadı.")
\`\`\`

---

## 🔌 Daphne Socket Dosyası (Varsa)

Socket birimi varsa:
\`\`\`bash
sudo nano /etc/systemd/system/daphne.socket
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/daphne.socket 2>/dev/null || echo "ℹ️ /etc/systemd/system/daphne.socket bulunamadı. Socket kullanılmıyor olabilir.")
\`\`\`

---

## 🧠 Daphne Başlatma Komutu (Manuel)

Aşağıdaki komut ile Daphne servisi manuel olarak başlatılabilir:

\`\`\`bash
cd /var/www/sapb1reportsv2/backend
source ../venv/bin/activate
daphne -u /run/daphne.sock sapreports.asgi:application
\`\`\`

---

## 📝 Daphne Log Dosyaları

\`\`\`bash
$(find /var/www/sapb1reportsv2/backend/logs/ -type f -iname "*daphne*.log" 2>/dev/null || echo "/logs içinde Daphne logu bulunamadı.")
\`\`\`

---

## 📂 Daphne Socket (Çalışma Durumu)

\`\`\`bash
$(ls -la /run/daphne.sock 2>/dev/null || echo "⚠️ Daphne socket (/run/daphne.sock) şu anda yok ya da erişilemiyor.")
\`\`\`

---

## 🔧 Daphne Servis Yönetimi (systemd)

\`\`\`bash
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
\`\`\`

---

## 🛡️ Yedekleme ve Kurtarma

\`\`\`bash
sudo cp /etc/systemd/system/daphne.service /etc/systemd/system/daphne.service.bak
[ -f /etc/systemd/system/daphne.socket ] && sudo cp /etc/systemd/system/daphne.socket /etc/systemd/system/daphne.socket.bak
\`\`\`

EOF

echo "✅ Tamamlandı: Daphne servis klavuzu '$OUTPUT_FILE' dosyasına kaydedildi."
