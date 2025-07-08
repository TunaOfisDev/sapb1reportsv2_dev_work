#!/bin/bash
set -e

# LOG dosyası
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/system_cleanup.log"
LOG_DIR="$(dirname "$LOG_FILE")"

# Log sahibini bozmayacak şekilde ayarla
if [ ! -w "$LOG_FILE" ]; then
    sudo touch "$LOG_FILE"
    sudo chown www-data:www-data "$LOG_FILE"
    sudo chmod 664 "$LOG_FILE"
fi

# Log fonksiyonu
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

log "==================================="
log " Ubuntu Sistem Temizleme Başladı - $(date)"
log "==================================="

# Healthcheck ve log yetki iade işlemi
restore_permissions() {
    log "Log dosyası yetkileri www-data'ya geri veriliyor..."
    sudo chown www-data:www-data "$LOG_FILE"
    sudo chmod 664 "$LOG_FILE"
    log "Yetki iade tamamlandı - $(date)"
}

call_health_check() {
    log "Servis sağlık kontrolü çağırılıyor..."
    if systemctl is-active --quiet healthcheck; then
        sudo systemctl restart healthcheck
        log "Healthcheck servisi yeniden başlatıldı."
    else
        sudo systemctl start healthcheck
        log "Healthcheck servisi başlatıldı."
    fi
}

trap 'restore_permissions; call_health_check' EXIT

### --- TEMİZLEME İŞLEMLERİ BAŞLIYOR ---

log "Snap önbelleği temizleniyor..."
if [ -d "/var/lib/snapd/cache" ]; then
    before=$(du -sh /var/lib/snapd/cache | awk '{print $1}')
    sudo rm -rf /var/lib/snapd/cache/* || true
    after=$(du -sh /var/lib/snapd/cache | awk '{print $1}')
    log "Snap cache: $before -> $after"
else
    log "Snap cache dizini bulunamadı."
fi

log "Eski ve büyük log dosyaları sıfırlanıyor..."
sudo find /var/log -type f -name "*.log" \
    \( -mtime +3 -size +100M -o -size +500M \) \
    ! -path "/var/log/postgresql/*" \
    ! -path "/var/log/redis/*" \
    ! -path "/var/log/nginx/*" \
    ! -path "$LOG_DIR/*" \
    -exec truncate -s 0 {} \; || true

log "Systemd journal logları temizleniyor..."
sudo journalctl --vacuum-time=7d --vacuum-size=500M

log "APT önbellekleri temizleniyor..."
sudo apt-get autoremove -y
sudo apt-get autoclean -y
sudo apt-get clean -y

log "Geçici dosyalar temizleniyor..."
sudo find /tmp -type f -mtime +7 -delete || true
sudo find /tmp -type d -empty -delete || true
sudo find /var/tmp -type f -mtime +7 -delete || true
sudo find /var/tmp -type d -empty -delete || true

log "Kullanıcı çöp kutuları temizleniyor (30+ gün)..."
for user in $(ls /home/); do
    trash="/home/$user/.local/share/Trash"
    if [ -d "$trash/files" ]; then
        sudo find "$trash/files" -type f -mtime +30 -delete || true
        sudo find "$trash/info" -type f -mtime +30 -delete || true
    fi
done

log "Disk Kullanımı:"
df -h | grep '^/dev/' | tee -a "$LOG_FILE"

log "Temizlik tamamlandı - $(date)"
