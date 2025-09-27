#!/bin/bash

# 📄 Çıktı dosyası
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_redis_service.md"
ENV_FILE="/var/www/sapb1reportsv2/backend/.env"

echo "🚀 Redis servis bilgileri analiz ediliyor..."

# .env dosyasını yükle
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "❌ .env dosyası bulunamadı: $ENV_FILE"
    exit 1
fi

# REDIS_PASS değişkenini çek
REDIS_PASS=${REDIS_PASS:-"default_password"}  # Varsayılan parola, eğer tanımlı değilse

# redis.conf yolunu bul
REDIS_CONF_PATH=$(systemctl show -p ExecStart redis | grep -oP '/[^ ]+\.conf' || echo "/etc/redis/redis.conf")
if [ ! -f "$REDIS_CONF_PATH" ]; then
    echo "❌ redis.conf bulunamadı: $REDIS_CONF_PATH"
    exit 1
fi

# redis-cli bağlantı testi
REDIS_PING=$(redis-cli -a "$REDIS_PASS" ping 2>/dev/null || echo "❌ bağlantı başarısız")

# Konfigürasyon satırlarını oku
REDIS_BIND=$(sudo grep -E '^bind' "$REDIS_CONF_PATH" 2>/dev/null || echo "bind satırı bulunamadı")
REDIS_PORT=$(sudo grep -E '^port' "$REDIS_CONF_PATH" 2>/dev/null || echo "port satırı bulunamadı")
REDIS_REQUIREPASS=$(sudo grep -E '^requirepass' "$REDIS_CONF_PATH" 2>/dev/null || echo "requirepass satırı bulunamadı")

# Markdown çıktısı oluştur
cat > "$OUTPUT_FILE" <<EOF
# 🧠 Redis Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** sunucusundaki Redis servisinin yapılandırma dosyalarını, şifreleme durumunu, port erişimini ve servis denetimini içerir.

---

## 🧾 Redis Servisi (systemd)

Servis dosyasını görmek için:
\`\`\`bash
sudo systemctl cat redis
\`\`\`

---

## 🔧 redis.conf Detayları

Dosya yolu:
\`\`\`bash
${REDIS_CONF_PATH}
\`\`\`

Temel ayarlar:
\`\`\`ini
${REDIS_BIND}
${REDIS_PORT}
${REDIS_REQUIREPASS}
\`\`\`

---

## 🔐 .env Üzerinden REDIS_PASS

\`\`\`env
REDIS_PASS="${REDIS_PASS}"
\`\`\`

---

## 🔌 Port Dinleme Durumu

\`\`\`bash
$(ss -lntp | grep 6379 || echo "❌ Port 6379 dinlenmiyor.")
\`\`\`

---

## 🧪 redis-cli Ping Testi

\`\`\`bash
redis-cli -a ******** ping
\`\`\`

Sonuç:
\`\`\`bash
${REDIS_PING}
\`\`\`

---

## 📦 Servis Yönetimi

\`\`\`bash
sudo systemctl start redis
sudo systemctl stop redis
sudo systemctl restart redis
sudo systemctl status redis
sudo systemctl enable redis
\`\`\`

---

## 📄 Log Takibi

\`\`\`bash
journalctl -u redis -f
journalctl -u redis --since today
\`\`\`

---

## 🧠 Ek Notlar

- Redis varsayılan olarak sadece \`127.0.0.1\` üzerinden dinler.
- Parola doğrulama açıksa \`.env\` içindeki \`REDIS_PASS\` kullanılır.
- Uzak bağlantılar için \`bind 0.0.0.0\` risklidir, dikkatli kullanılmalıdır.
- Bazı sistemlerde servis adı \`redis-server\` olabilir.

EOF

echo "✅ Rapor oluşturuldu: $OUTPUT_FILE"