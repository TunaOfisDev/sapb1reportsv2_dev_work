#!/bin/bash
set -e

# Renk kodları
GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Başarılı mesaj fonksiyonu
success_msg() {
    echo -e "${GREEN}$1${NC}"
}

# Hata mesaj fonksiyonu
error_msg() {
    echo -e "${RED}$1${NC}" >&2
}

# Hata durumunda hata mesajı ve hata kodu ile çıkış yapmak için trap kullanımı
trap 'error_msg "Hata oluştu! Hata kodu: $? Komut: $BASH_COMMAND Satır: $LINENO"; exit 1' ERR

# Log dosyasını tanımla
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/sambactrl.log"

# Yetkileri geçici olarak güncelle
echo "Yetkiler geçici olarak güncelleniyor"
sudo chown user:user "$LOG_FILE"
sudo chmod 664 "$LOG_FILE"

# Log yönlendirme
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "----- $(date) Mount işlemi başlıyor -----"
sudo mount -a
echo "----- $(date) Mount işlemi tamamlandı -----"

# Yetkileri www-data'ya geri verme
echo "Yetkiler www-data kullanıcısına geri veriliyor"
sudo chown www-data:www-data "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"
success_msg "Yetkiler www-data'ya geri verildi."
