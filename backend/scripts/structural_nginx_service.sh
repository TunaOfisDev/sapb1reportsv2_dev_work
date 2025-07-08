#!/bin/bash

# 📄 Çıktı dosyası yolu
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_nginx_service.md"

echo "🚀 Nginx yapılandırması analiz ediliyor..."

# 📝 Markdown çıktısını oluştur
cat > "$OUTPUT_FILE" <<EOF
# 🌐 Nginx Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** sunucusunda kurulu **Nginx** servisinin yapılandırmalarını, site tanımlarını, log dosyalarını ve servis yönetim komutlarını içerir. Sistem üzerinde değişiklik yapılmaz, sadece analiz sağlar.

---

## 🧭 Nginx Sürüm Bilgisi

\`\`\`bash
$(nginx -v 2>&1)
\`\`\`

---

## 🧾 Global Konfigürasyon: nginx.conf

Konfigürasyon dosyası:
\`\`\`bash
sudo nano /etc/nginx/nginx.conf
\`\`\`

İçerik:
\`\`\`nginx
$(cat /etc/nginx/nginx.conf)
\`\`\`

---

## 🌐 Aktif Site Tanımları (sites-enabled)

\`\`\`bash
$(ls -l /etc/nginx/sites-enabled/ 2>/dev/null || echo "Aktif site bulunamadı.")
\`\`\`

---

## 📂 Site Konfigürasyonları (sites-available)

Tüm tanımlı site dosyalarının içeriği:

EOF

for site in /etc/nginx/sites-available/*; do
  echo "### 📄 $(basename "$site")" >> "$OUTPUT_FILE"
  echo '```nginx' >> "$OUTPUT_FILE"
  cat "$site" >> "$OUTPUT_FILE"
  echo '```' >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
done

# 🔍 sapreports özel kontrol
if [ -f "/etc/nginx/sites-available/sapreports" ]; then
  echo "## 📌 Özel Konfigürasyon: sapreports" >> "$OUTPUT_FILE"
  echo '```nginx' >> "$OUTPUT_FILE"
  cat /etc/nginx/sites-available/sapreports >> "$OUTPUT_FILE"
  echo '```' >> "$OUTPUT_FILE"
else
  echo "⚠️ sapreports yapılandırması bulunamadı (/etc/nginx/sites-available/sapreports)." >> "$OUTPUT_FILE"
fi

# 🔍 Log yolları
cat >> "$OUTPUT_FILE" <<EOF

---

## 📝 Log Tanımları (access_log / error_log)

\`\`\`bash
$(grep -r "access_log\|error_log" /etc/nginx/nginx.conf /etc/nginx/sites-* 2>/dev/null | sort -u || echo "Log satırı bulunamadı.")
\`\`\`

---

## 🔧 Nginx Servis Yönetimi (systemd)

\`\`\`bash
sudo systemctl daemon-reload

# Servis işlemleri
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx        # Konfigürasyon güncellemelerinde önerilir
sudo systemctl status nginx
sudo systemctl enable nginx
\`\`\`

---

## 📡 Nginx Log Takibi (journalctl)

\`\`\`bash
journalctl -u nginx -f             # Canlı log izle
journalctl -u nginx --since today  # Günlük log
\`\`\`

---

## 🛡️ Yedekleme ve Geri Yükleme

\`\`\`bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
sudo cp /etc/nginx/sites-available/sapreports /etc/nginx/sites-available/sapreports.bak
\`\`\`

EOF

echo "✅ Tamamlandı: Nginx klavuzu '$OUTPUT_FILE' dosyasına kaydedildi."
