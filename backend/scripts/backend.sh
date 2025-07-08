#!/bin/bash
# Kurumsal, sürdürülebilir backend yönetim scripti
set -e

# Renk kodlari
GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

success_msg() {
    echo -e "${GREEN}$1${NC}"
}

error_msg() {
    echo -e "${RED}$1${NC}" >&2
}

handle_error() {
    error_msg "Hata olustu! Kodu: $? Komut: $BASH_COMMAND Satir: $LINENO"
    exit 1
}

trap 'handle_error' ERR

cd /var/www/sapb1reportsv2/

# 👍 Yalnızca logs ve frontend/build için uygula:
sudo chown -R www-data:sapb1 backend/logs frontend/build
sudo chmod -R 775 backend/logs frontend/build


# venv aktive et
source venv/bin/activate
cd backend

# Django kontrolleri
success_msg "Django kontrol basladi"
python manage.py check
python manage.py showmigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Gunicorn & nginx restart
sudo nginx -t && success_msg "Nginx konfigurasyon testi basarili"
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl restart gunicorn
success_msg "Gunicorn ve Nginx yeniden baslatildi."

# Daphne kontrol
if ! systemctl is-active --quiet daphne; then
    sudo systemctl start daphne
    sudo systemctl enable daphne
fi
systemctl is-active --quiet daphne && success_msg "Daphne calisiyor" || error_msg "Daphne calismiyor"

# Celery stop-start
for svc in celery celerybeat; do
    if systemctl list-units --full -all | grep -q "$svc.service"; then
        sudo systemctl stop $svc || true
        sudo systemctl start $svc
        sudo systemctl enable $svc
        systemctl is-active --quiet $svc && success_msg "$svc calisiyor" || error_msg "$svc baslatilamadi"
    else
        error_msg "$svc servis dosyasi tanimli degil."
    fi
done

# Uygulama kontrolu
curl -sSf http://localhost -o /dev/null && success_msg "Uygulama erisilebilir durumda" || error_msg "Uygulama erisilemiyor"

success_msg "TUM ISLEMLER BASARIYLA TAMAMLANDI."
