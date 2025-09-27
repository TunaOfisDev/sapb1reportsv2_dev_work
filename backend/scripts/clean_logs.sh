#!/bin/bash
set -e

# Renk kodları
GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m'

# Fonksiyonlar
success_msg() {
    echo -e "${GREEN}$1${NC}"
}

error_msg() {
    echo -e "${RED}$1${NC}" >&2
}

# Sağlık kontrolünü her durumda çağırmak için EXIT trap
call_health_check() {
    echo -e "${GREEN}Healthcheck servisi kontrol ediliyor...${NC}"
    if systemctl is-active --quiet healthcheck; then
        echo -e "${GREEN}Healthcheck servisi yeniden başlatılıyor...${NC}"
        sudo systemctl restart healthcheck
    else
        echo -e "${GREEN}Healthcheck servisi başlatılıyor...${NC}"
        sudo systemctl start healthcheck
    fi
    echo -e "${GREEN}Healthcheck tamamlandı.${NC}"
}
trap call_health_check EXIT

# Log dizini
LOG_DIR="/var/www/sapb1reportsv2/backend/logs"

# Temizlenecek log dosyaları
LOGS=(
    "backend.log"
    "celery_beat.log"
    "celery_worker.log"
    "celery.log"
    "celerybeat.log"
    "clean_logs.log"
    "cron.log"
    "daphne.log"
    "db_backup.log"
    "db_maintenance.log"
    "deploy_services_ctrl.log"
    "frontend_setup.log"
    "gunicorn.log"
    "gunicorn-access.log",
    "gunicorn-error.log",
    "hanadb_integration.log"
    "health_check.log"
    "load_data.log"
    "migrate.log"
    "piprequirements.log"
    "sambactrl.log"
    "service_monitor.log"
    "startup_tasks.log"
    "stockcard_integration.log"
    "system_cleanup.log"
    "system_health_check.log"
    "system_monitor.log"
)

# PID dosyaları (kontrol edilecek ama sıfırlanmaz!)
PID_FILES=(
    "celery_beat.pid"
    "celery_worker.pid"
)

success_msg "Log temizleme işlemi başlatıldı"

