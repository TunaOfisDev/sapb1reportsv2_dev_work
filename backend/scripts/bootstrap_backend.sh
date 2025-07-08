#!/bin/bash

LOG_FILE="/tmp/bootstrap_backend.log"

# Sadece en son çalışmayı logla (önceki logu sil)
exec > "$LOG_FILE" 2>&1

echo "[BOOTSTRAP] Servisler başlatılıyor: $(date)"

# Log izinlerini düzenle
chown -R www-data:www-data /var/www/sapb1reportsv2/backend/logs
chmod -R 755 /var/www/sapb1reportsv2/backend/logs

# Gunicorn başlat
echo "Gunicorn başlatılıyor..."
systemctl start gunicorn

# Daphne başlat
echo "Daphne başlatılıyor..."
systemctl start daphne

# Celery başlat
echo "Celery başlatılıyor..."
systemctl start celery

# Celery Beat başlat
echo "Celery Beat başlatılıyor..."
systemctl start celerybeat

# Log dosyalarını kontrol et
ls -l /var/www/sapb1reportsv2/backend/*.sock

echo "[BOOTSTRAP] Tamamlandı: $(date)"
