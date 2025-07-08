#!/bin/bash

# Şablon çıktısı konumu
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_template_service.md"

echo "📄 Template servis klavuzu oluşturuluyor..."

# Markdown içerik
cat > "$OUTPUT_FILE" <<EOF
# 🧩 TEMPLATE Servis Yapılandırma Klavuzu

Bu belge, belirli bir servisin systemd yapılandırmasını, log sistemini, başlatma komutlarını ve yönetim komutlarını belgelemek için **şablon** olarak hazırlanmıştır. Yeni servis entegrasyonlarında bu yapıyı referans alabilirsiniz.

> 🔧 Bu şablon, servis adı ve içerikleri servis özelinde doldurularak özelleştirilmelidir.

---

## 🧾 Systemd Servis Dosyası

Servis dosyasını düzenlemek için:
\`\`\`bash
sudo nano /etc/systemd/system/REPLACE.service
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/REPLACE.service 2>/dev/null || echo "❌ /etc/systemd/system/REPLACE.service bulunamadı.")
\`\`\`

---

## 🔌 Socket Dosyası (Varsa)

\`\`\`bash
sudo nano /etc/systemd/system/REPLACE.socket
\`\`\`

İçerik:
\`\`\`ini
$(sudo cat /etc/systemd/system/REPLACE.socket 2>/dev/null || echo "ℹ️ Socket dosyası bulunamadı veya kullanılmıyor olabilir.")
\`\`\`

---

## 🧠 Manuel Başlatma Komutu

Servis terminalden manuel başlatılmak istenirse:
\`\`\`bash
# Örnek:
cd /path/to/app
source venv/bin/activate
REPLACE_MANUAL_START_COMMAND
\`\`\`

---

## 📝 Log Dosyaları

\`\`\`bash
$(find /var/www/sapb1reportsv2/backend/logs/ -type f -iname "*REPLACE*" 2>/dev/null || echo "Log klasöründe özel log bulunamadı.")
\`\`\`

Canlı log takibi için:
\`\`\`bash
journalctl -u REPLACE -f
\`\`\`

---

## 📂 Socket Durumu (Runtime)

\`\`\`bash
$(ls -la /run/REPLACE.sock 2>/dev/null || echo "⚠️ Socket (/run/REPLACE.sock) şu anda yok ya da erişilemiyor.")
\`\`\`

---

## 🔧 Servis Yönetim Komutları

\`\`\`bash
sudo systemctl daemon-reload

# Servis işlemleri
sudo systemctl start REPLACE
sudo systemctl stop REPLACE
sudo systemctl restart REPLACE
sudo systemctl status REPLACE
sudo systemctl enable REPLACE

# Socket varsa:
sudo systemctl start REPLACE.socket
sudo systemctl status REPLACE.socket
\`\`\`

---

## 🛡️ Yedekleme & Kurtarma

\`\`\`bash
sudo cp /etc/systemd/system/REPLACE.service /etc/systemd/system/REPLACE.service.bak
[ -f /etc/systemd/system/REPLACE.socket ] && sudo cp /etc/systemd/system/REPLACE.socket /etc/systemd/system/REPLACE.socket.bak
\`\`\`

EOF

echo "✅ Şablon klavuz oluşturuldu: $OUTPUT_FILE"
