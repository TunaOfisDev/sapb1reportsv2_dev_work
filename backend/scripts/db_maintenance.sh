#!/bin/bash
set -euo pipefail

# Renk kodları
GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m'

# Mesaj fonksiyonları
success_msg() { echo -e "${GREEN}$1${NC}"; }
error_msg() { echo -e "${RED}$1${NC}" >&2; }

# Hata yakalama
trap 'error_msg "Hata oluştu! Hata kodu: $? Komut: $BASH_COMMAND Satır: $LINENO"; exit 1' ERR

# Dizin ve log tanımları
BASE_DIR="/var/www/sapb1reportsv2"
LOG_DIR="$BASE_DIR/backend/logs"
LOG_FILE="$LOG_DIR/db_maintenance.log"

# Log dizinini oluştur
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Yalnızca son çalıştırmanın logunu yaz (overwrite)
exec > "$LOG_FILE" 2>&1

echo "----------------------------------------"
echo "DB Bakım işlemi başladı: $(date)"

# Yetkileri geçici olarak al
echo "Yetkileri geçici olarak güncelleniyor..."
sudo chown -R user:user "$BASE_DIR" && success_msg "Yetkiler alındı."

# Django ortamını hazırla
export DJANGO_SETTINGS_MODULE=sapreports.settings
export PYTHONPATH="$BASE_DIR/backend"
source "$BASE_DIR/venv/bin/activate"

DB_NAME=$(python3 -c "import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['NAME'])")
DB_USER=$(python3 -c "import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['USER'])")
DB_PASSWORD=$(python3 -c "import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['PASSWORD'])")

deactivate

# Veritabanı bakım işlemi
export PGPASSWORD="$DB_PASSWORD"

psql -U "$DB_USER" -d "$DB_NAME" << EOF
\echo 'Veritabanı Bakım Raporu'
\echo '----------------------'

\echo '\nBakım Öncesi Tablo Durumu:'
SELECT schemaname, relname, n_live_tup, n_dead_tup, 
       last_vacuum, last_analyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 0;

\echo '\nVACUUM ANALYZE çalıştırılıyor...'
VACUUM (VERBOSE, ANALYZE);

\echo '\nBakım Sonrası Tablo Durumu:'
SELECT schemaname, relname, n_live_tup, n_dead_tup,
       last_vacuum, last_analyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 0;

\echo '\nKullanılmayan Index Raporu:'
SELECT schemaname, relname as table_name, indexrelname as index_name,
       idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_all_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexrelname NOT LIKE 'pg_%';

\echo '\nGenel Veritabanı İstatistikleri:'
SELECT datname,
       numbackends as aktif_bağlantı,
       xact_commit as başarılı_işlem,
       xact_rollback as geri_alınan_işlem,
       blks_read as disk_okunan,
       blks_hit as cache_okunan,
       tup_returned as dönen_satır,
       tup_fetched as alınan_satır
FROM pg_stat_database
WHERE datname = '$DB_NAME';
EOF

echo "DB Bakım işlemi tamamlandı: $(date)"
echo "----------------------------------------"

# Yetkileri geri ver
echo "Yetkiler www-data kullanıcısına geri veriliyor..."
sudo chown -R www-data:www-data "$BASE_DIR" && success_msg "Yetkiler geri verildi."

# Sağlık kontrolü çağır
call_health_check() {
    echo "Servis sağlık kontrolü başlatılıyor..."
    if systemctl is-active --quiet healthcheck; then
        echo "Healthcheck servisi zaten çalışıyor, yeniden başlatılıyor..."
        sudo systemctl restart healthcheck
    else
        echo "Healthcheck servisi başlatılıyor..."
        sudo systemctl start healthcheck
    fi
    echo "Servis sağlık kontrolü başlatıldı - $(date)"
}

call_health_check
