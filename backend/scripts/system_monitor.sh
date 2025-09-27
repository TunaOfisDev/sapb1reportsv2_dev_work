#!/bin/bash
set -e

# LOG ayarı (hem terminale hem dosyaya, sadece son çıktıyı)
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/system_monitor.log"
: > "$LOG_FILE"  # önce sıfırla


# Log dizinini ve dosyasını oluştur (overwrite mantığı)
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"
chown $(whoami):$(whoami) "$LOG_FILE"


# Çıkışta log yetkisini geri ver
cleanup() {
  chown www-data:www-data "$LOG_FILE"
  echo "$(date): Yetkiler www-data kullanıcısına geri verildi."
}
trap cleanup EXIT

log_message() {
  echo "$(date): $1"
}

log_message "Sistem monitör script çalıştırıldı"

# Bellek kullanımı
MEMORY_TOTAL=$(free -m | grep Mem | awk '{print $2}')
MEMORY_USED=$(free -m | grep Mem | awk '{print $3}')
MEMORY_USAGE=$(awk "BEGIN {printf \"%.2f\", $MEMORY_USED*100/$MEMORY_TOTAL}")

# Swap kontrol
SWAP_TOTAL=$(free -m | grep Swap | awk '{print $2}')
SWAP_USAGE="0.00"
if [ "$SWAP_TOTAL" -gt 0 ]; then
  SWAP_USED=$(free -m | grep Swap | awk '{print $3}')
  SWAP_USAGE=$(awk "BEGIN {printf \"%.2f\", $SWAP_USED*100/$SWAP_TOTAL}")
fi

# Disk durumu
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')

# PostgreSQL DB boyutu
if command -v psql &> /dev/null && systemctl is-active --quiet postgresql; then
  DB_NAME=$(sudo -u postgres psql -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;" | grep -v postgres | head -n 1 | xargs)
  if [ -n "$DB_NAME" ]; then
    DB_SIZE=$(sudo -u postgres psql -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs)
    log_message "Veritabanı ($DB_NAME) Boyutu: $DB_SIZE"
  else
    log_message "Veritabanı adı bulunamadı"
  fi
fi

# CPU yükü
CPU_LOAD=$(uptime | awk '{print $(NF-2)}' | tr -d ',')

# Ağ bağlantı kontrolü
if command -v ss &> /dev/null; then
  ACTIVE_CONNECTIONS=$(ss -tn | grep ESTAB | wc -l)
else
  ACTIVE_CONNECTIONS="netstat/ss komutu bulunamadı"
fi

# Gunicorn işlem sayısı
GUNICORN_PROCESSES=$(pgrep -f gunicorn | wc -l)

log_message "Bellek Kullanımı: $MEMORY_USAGE% ($MEMORY_USED/$MEMORY_TOTAL MB)"
log_message "Swap Kullanımı: $SWAP_USAGE%"
log_message "Disk Kullanımı: $DISK_USAGE% (Boş alan: $DISK_FREE)"
log_message "CPU Yükü: $CPU_LOAD"
log_message "Aktif Bağlantı Sayısı: $ACTIVE_CONNECTIONS"
log_message "Gunicorn İşlem Sayısı: $GUNICORN_PROCESSES"

# Servis kontrol
check_service() {
  local service_name=$1
  if systemctl is-active --quiet "$service_name"; then
    log_message "$service_name servisi çalışıyor"
    return 0
  else
    log_message "$service_name servisi çalışmıyor"
    return 1
  fi
}

check_service nginx
check_service gunicorn
check_service daphne
check_service celery
check_service celerybeat
check_service postgresql

# Bellek kritikse müdahale
if (( $(echo "$MEMORY_USAGE > 90" | bc -l 2>/dev/null || echo 0) )); then
  log_message "UYARI: Bellek kullanımı kritik seviyede ($MEMORY_USAGE%)"

  log_message "Bellek yoğunluklu işlemler:"
  ps aux --sort=-%mem | head -n 6

  systemctl restart gunicorn && log_message "Gunicorn yeniden başlatıldı"
  sleep 5
  systemctl restart daphne && log_message "Daphne yeniden başlatıldı"
  sleep 5
  systemctl restart celery && log_message "Celery yeniden başlatıldı"
  sleep 5
  systemctl restart celerybeat && log_message "Celerybeat yeniden başlatıldı"
fi

# Disk kritikse log temizliği
if [ "$DISK_USAGE" -gt 90 ]; then
  log_message "UYARI: Disk kullanımı kritik seviyede ($DISK_USAGE%)"

  log_message "En büyük dosya/dizinler:"
  sudo du -h /var/www/sapb1reportsv2/ | sort -rh | head -n 10

  if [ -f "/var/www/sapb1reportsv2/backend/scripts/clean_logs.sh" ]; then
    sudo /var/www/sapb1reportsv2/backend/scripts/clean_logs.sh
    log_message "Log temizleme scripti çalıştırıldı"
  else
    log_message "Log temizleme scripti bulunamadı, acil temizlik uygulanıyor"
    sudo find /var/www/sapb1reportsv2/backend/logs -name "*.log" -type f -size +50M -exec truncate -s 0 {} \;
    sudo find /var/log -name "*.log" -type f -size +100M -exec truncate -s 0 {} \;
  fi
fi

# Servislerden biri çalışmıyorsa backend.sh çağır
if ! check_service nginx || ! check_service gunicorn || ! check_service daphne || ! check_service celery || ! check_service celerybeat; then
  log_message "UYARI: Çalışmayan servisler bulundu. backend.sh çalıştırılıyor"
  /var/www/sapb1reportsv2/backend/scripts/backend.sh >> "$LOG_FILE" 2>&1
  log_message "backend.sh çıktısı loglandı"
fi

log_message "Sistem monitör script tamamlandı"
log_message "-------------------------------------------------"
