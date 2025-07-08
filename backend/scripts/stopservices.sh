# backend/scripts/stopservices.sh
#!/bin/bash

# Yetkileri geçici olarak güncelle
sudo chown -R user:user /var/www/sapb1reportsv2

# Nginx servisini durdurma
echo "Nginx servisini durduruyor..."
sudo systemctl stop nginx

# Gunicorn süreçlerini güvenli bir şekilde durdurma
echo "Gunicorn süreçlerini güvenli bir şekilde durduruyor..."
GUNICORN_SOCK_PATH="/var/www/sapb1reportsv2/backend/gunicorn.sock"

# Gunicorn ana sürecinin ve işçi süreçlerinin PID'lerini bul
PIDS=$(pgrep -f "$GUNICORN_SOCK_PATH")
if [[ -n "$PIDS" ]]; then
    # Her PID için sudo ile kill komutunu çalıştır
    for PID in $PIDS; do
        echo "Gunicorn PID $PID durduruluyor..."
        sudo kill -TERM "$PID"
    done
    
    # Tüm süreçlerin sonlanmasını bekle
    echo "Gunicorn süreçlerinin sonlanması bekleniyor..."
    wait $PIDS
else
    echo "Gunicorn süreci bulunamadı."
fi

# Daphne servisini durdurma
echo "Daphne servisini durduruyor..."
sudo systemctl stop daphne

# Celery servisini durdurma
echo "Celery servisini durduruyor..."
sudo systemctl stop celery

# Celery Beat'i durdurma (eğer ayrı bir servis olarak çalışıyorsa)
echo "Celery Beat'i durduruyor..."
sudo systemctl stop celerybeat

# Ek dosya ve soketleri temizleme
echo "Ek dosya ve soketleri temizliyor..."

# celerybeat-schedule dosyasını silme
if [ -f /var/www/sapb1reportsv2/backend/celerybeat-schedule ]; then
    rm /var/www/sapb1reportsv2/backend/celerybeat-schedule
    echo "celerybeat-schedule dosyası silindi."
fi

# daphne.sock ve daphne.sock.lock dosyalarını silme
if [ -S /var/www/sapb1reportsv2/backend/daphne.sock ]; then
    rm /var/www/sapb1reportsv2/backend/daphne.sock
    echo "daphne.sock dosyası silindi."
fi

if [ -f /var/www/sapb1reportsv2/backend/daphne.sock.lock ]; then
    rm /var/www/sapb1reportsv2/backend/daphne.sock.lock
    echo "daphne.sock.lock dosyası silindi."
fi

# gunicorn.sock dosyasını silme
if [ -S /var/www/sapb1reportsv2/backend/gunicorn.sock ]; then
    rm /var/www/sapb1reportsv2/backend/gunicorn.sock
    echo "gunicorn.sock dosyası silindi."
fi

echo "Tüm servisler başarıyla durduruldu ve ek dosyalar temizlendi."