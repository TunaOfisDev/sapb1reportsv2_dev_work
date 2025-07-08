#/var/www/sapb1reportsv2/backend/scripts/deploy_services_ctrl.sh
#!/bin/bash

# Bu script, log yazma işlemleri öncesinde log dizininin yetkilerini 
# aktif kullanıcının (scripti çağıran kullanıcı) üzerine alır, 

# Selim, böylece log dosyasında "Permission denied" hataları olmadan 
# gelişmiş bir kontrol raporu alabilirsin.

# Log klasörünün erişilebilirliğini garanti altına al

sudo find /var/www/sapb1reportsv2/backend/logs -type f -exec chmod 644 {} \;


# Sabit tanımlamalar
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/deploy_services_ctrl.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
# Scripti hangi kullanıcı çalıştırıyorsa onu tespit edelim
CURRENT_USER=$(whoami)

# Renk tanımlamaları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Log fonksiyonu
log_message() {
    local message="$1"
    echo -e "${message}"
    echo "[${DATE}] ${message}" >> "${LOG_FILE}"
}

# Servis listesi
SERVICES=(
    "nginx"
    "gunicorn"
    "redis-server"
    "postgresql@17-main"
    "daphne"
    "celery"
    "celerybeat"
)

# 1) Log dizininin yetkilerini scripti çalıştıran kullanıcıya verelim
# Bu sayede log dosyasına yazarken "Permission denied" hatası almayız
sudo chown -R "$CURRENT_USER":"$CURRENT_USER" "$(dirname "${LOG_FILE}")"
sudo chmod -R 775 "$(dirname "${LOG_FILE}")"

# Log dosyası için dizin oluştur (varsa var, yoksa oluşturur)
mkdir -p "$(dirname "${LOG_FILE}")"

# Başlık yazdırma
header="=== Hana Rapor Sunucusu - Servis Durumları (${DATE}) ==="
log_message "\n${YELLOW}${header}${NC}\n"

# Her servis için durum kontrolü
for service in "${SERVICES[@]}"; do
    service_header="=== $service Servis Durumu ==="
    log_message "\n${YELLOW}${service_header}${NC}"
    
    if sudo systemctl is-active --quiet "$service"; then
        # Servis çalışıyor
        log_message "${GREEN}✓ $service aktif${NC}"
        
        # Servis detaylarını al
        status_output=$(sudo systemctl status "$service" | grep -E "Active:|Memory:|Tasks:|Process:|PID:" 2>/dev/null)
        log_message "$status_output"
        
        # Servis loglarının son 3 satırını al
        log_message "\nSon Loglar:"
        sudo journalctl -u "$service" -n 3 --no-pager | while read -r line; do
            log_message "  $line"
        done
    else
    # Servis çalışmıyor
    log_message "${RED}✗ $service çalışmıyor veya bulunamadı!${NC}"
    
    # Hata detayları
    error_output=$(sudo systemctl status "$service" 2>&1 | grep -E "Failed|Error" | head -n 2)
    if [ ! -z "$error_output" ]; then
        log_message "Hata Detayı: $error_output"
    fi

    # Servisi yeniden başlatmayı deneyelim
    log_message "${YELLOW}↻ $service yeniden başlatılıyor...${NC}"
    if sudo systemctl restart "$service"; then
        log_message "${GREEN}✓ $service başarıyla yeniden başlatıldı${NC}"
    else
        log_message "${RED}✗ $service yeniden başlatılamadı!${NC}"
    fi

    fi
    log_message "----------------------------------------"
done

# Sistem Bilgileri
log_message "\n${YELLOW}=== Sistem Bellek Durumu ===${NC}"
free -h | while read -r line; do
    log_message "$line"
done

log_message "\n${YELLOW}=== Disk Kullanımı ===${NC}"
df -h / | while read -r line; do
    log_message "$line"
done

log_message "\n${YELLOW}=== CPU Kullanımı ===${NC}"
top -bn1 | head -n 5 | while read -r line; do
    log_message "$line"
done

log_message "\n${YELLOW}=== En Çok Kaynak Kullanan Süreçler ===${NC}"
ps aux --sort=-%mem | head -n 6 | while read -r line; do
    log_message "$line"
done

# Port Kontrolü
log_message "\n${YELLOW}=== Port Durumları ===${NC}"
ports=(80 443 8000 6379 5432 30015)
for port in "${ports[@]}"; do
    if sudo netstat -tuln | grep -q ":$port "; then
        log_message "${GREEN}✓ Port $port açık${NC}"
    else
        log_message "${RED}✗ Port $port kapalı${NC}"
    fi
done

# Uygulama Klasörü Yetkileri
log_message "\n${YELLOW}=== Uygulama Klasörü Yetkileri ===${NC}"
ls -l /var/www/sapb1reportsv2/backend/ | head -n 5 | while read -r line; do
    log_message "$line"
done

# Özet Rapor
log_message "\n${YELLOW}=== Özet Rapor ===${NC}"
active_count=0
inactive_count=0
inactive_services=()

for service in "${SERVICES[@]}"; do
    if sudo systemctl is-active --quiet "$service"; then
        ((active_count++))
    else
        ((inactive_count++))
        inactive_services+=("$service")
    fi
done

log_message "Toplam Servis Sayısı: ${#SERVICES[@]}"
log_message "Aktif Servis Sayısı: ${active_count}"
log_message "İnaktif Servis Sayısı: ${inactive_count}"

if [ ${inactive_count} -gt 0 ]; then
    log_message "\n${RED}İnaktif Servisler:${NC}"
    for service in "${inactive_services[@]}"; do
        log_message "- $service"
    done
fi

# Script bitişi
log_message "\n${YELLOW}=== Kontrol Tamamlandı (${DATE}) ===${NC}\n"


# Log dosyalarının yazılabilir olduğundan emin ol
find "$(dirname "${LOG_FILE}")" -type f -exec chmod 644 {} \;

