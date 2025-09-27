#!/bin/bash

# 📄 Çıktı dosyası
OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_postgresql_service.md"
ENV_PATH="/var/www/sapb1reportsv2/backend/.env"

echo "🚀 PostgreSQL servis yapılandırması analiz ediliyor..."

# .env'den değişkenleri oku
PG_HOST=$(grep 'PGDB_HOST=' "$ENV_PATH" | cut -d '=' -f2)
PG_PORT=$(grep 'PGDB_PORT=' "$ENV_PATH" | cut -d '=' -f2)
PG_USER=$(grep 'PGDB_USER=' "$ENV_PATH" | cut -d '=' -f2)
PG_DB=$(grep 'PGDB_NAME=' "$ENV_PATH" | cut -d '=' -f2)
PG_PASS=$(grep 'PGDB_PASSWORD=' "$ENV_PATH" | cut -d '=' -f2)

# Konfigürasyon dosyalarının yolları
PG_CONF=$(sudo -u postgres psql -tAc "SHOW config_file;" 2>/dev/null)
PG_HBA=$(dirname "$PG_CONF")/pg_hba.conf

# Bağlantı test sonucu
PG_VERSION_OUTPUT=$(PGPASSWORD="$PG_PASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c 'SELECT version();' 2>/dev/null || echo "❌ Bağlantı başarısız")

# Markdown çıktısı
cat > "$OUTPUT_FILE" <<EOF
# 🐘 PostgreSQL Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde kullanılan PostgreSQL servisinin yapılandırmasını, bağlantı testlerini ve log denetimlerini içerir.

---

## 🧾 Servis Bilgisi

\`\`\`bash
sudo systemctl cat postgresql
\`\`\`

Birincil unit dosyası:
\`\`\`bash
$(systemctl show -p FragmentPath postgresql | cut -d '=' -f2)
\`\`\`

---

## ⚙️ Konfigürasyon Dosyaları

- postgresql.conf: \`$PG_CONF\`
- pg_hba.conf: \`$PG_HBA\`

\`\`\`ini
$(sudo grep -E '^(listen_addresses|port|password_encryption)' "$PG_CONF" 2>/dev/null || echo "⚠️ postgresql.conf okunamadı")
\`\`\`

---

## 🔐 pg_hba.conf Kuralları

\`\`\`ini
$(sudo grep -v '^#' "$PG_HBA" | grep -v '^$' 2>/dev/null || echo "⚠️ pg_hba.conf erişilemedi")
\`\`\`

---

## 🔁 Django Uyumlu Ayarlar

.env dosyasındaki veritabanı bilgileri:
\`\`\`env
PGDB_NAME=$PG_DB
PGDB_USER=$PG_USER
PGDB_PASSWORD=*****
PGDB_HOST=$PG_HOST
PGDB_PORT=$PG_PORT
\`\`\`

settings.py içeriğinde:
\`\`\`python
'OPTIONS': {
    'options': '-c client_encoding=UTF8'
}
\`\`\`

---

## 🧪 Bağlantı Testi

\`\`\`bash
PGPASSWORD="$PG_PASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c 'SELECT version();'
\`\`\`

Sonuç:
\`\`\`bash
$PG_VERSION_OUTPUT
\`\`\`

---

## 📦 Servis Yönetimi

\`\`\`bash
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
sudo systemctl status postgresql
sudo systemctl enable postgresql
\`\`\`

---

## 📝 Log Takibi

\`\`\`bash
journalctl -u postgresql -f
journalctl -u postgresql --since today
\`\`\`

---

## 🛡️ Yedekleme ve Yapılandırma Yenileme

\`\`\`bash
sudo cp "$PG_CONF" "$PG_CONF.bak"
sudo cp "$PG_HBA" "$PG_HBA.bak"
\`\`\`

Veritabanına bağlı kalmadan reload:
\`\`\`sql
SELECT pg_reload_conf();
\`\`\`

---

EOF

echo "✅ Rapor oluşturuldu: $OUTPUT_FILE"
