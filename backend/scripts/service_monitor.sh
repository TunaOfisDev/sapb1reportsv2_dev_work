#!/bin/bash
set -e

# Renkler
GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m'

# Log dosyası
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/service_monitor.log"

# Log dizinini ve dosyasını hazırla
prepare_log_file() {
  sudo mkdir -p "$(dirname "$LOG_FILE")"
  sudo touch "$LOG_FILE"
  sudo chown "$(whoami)":"$(whoami)" "$LOG_FILE"
  sudo chmod 664 "$LOG_FILE"

  # Tüm çıktıları log dosyasına yönlendir (append değil, overwrite)
  exec > "$LOG_FILE" 2>&1
}

# Script sonunda log dosyasının izinlerini geri ver
restore_permissions() {
  sudo chown www-data:www-data "$LOG_FILE"
  sudo chmod 644 "$LOG_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log dosyası yetkileri www-data'ya iade edildi."
}
trap restore_permissions EXIT

# Log yazdırıcı
log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Başarılı mesaj
success() {
  echo -e "${GREEN}$1${NC}"
}

# Hata mesajı
error() {
  echo -e "${RED}$1${NC}" >&2
}

# Servis kontrol fonksiyonu
check_service() {
  local service_name=$1
  if systemctl is-active --quiet "$service_name"; then
    log " $service_name servisi çalışıyor."
  else
    log " $service_name servisi çalışmıyor! backend-restart.service tetikleniyor..."
    if sudo systemctl start backend-restart.service; then
      log " backend-restart.service başarıyla başlatıldı."
    else
      log " backend-restart.service başlatılamadı!"
    fi
  fi
}

# Başlatıcı
main() {
  prepare_log_file
  log " Servis izleme scripti başlatıldı."

  services=(nginx gunicorn daphne celery celerybeat)
  for svc in "${services[@]}"; do
    check_service "$svc"
  done

  log " Servis izleme tamamlandı."
  log "----------------------------------------"
  success "Tüm servisler kontrol edildi."
}

main
