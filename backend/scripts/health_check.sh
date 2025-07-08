#!/bin/bash
# Bu script sadece son çalıştırmanın sistem sağlık bilgilerini saklar.
# Log dosyası her çalıştırmada otomatik olarak sıfırlanır (overwrite).
# Amaç: Disk alanını korumak, şişkin loglardan kaçınmak ve sistemin en güncel durumunu tutmaktır.
# Eğer tarihsel takip gerekirse logrotate veya arşiv mekanizması eklenmelidir.

LOG_FILE="/var/www/sapb1reportsv2/backend/logs/system_health_check.log"

# Log dizinini ve dosyasını oluştur (gerekirse)
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Log dosyasını sıfırla (append etme, en baştan yaz)
exec > "$LOG_FILE" 2>&1

echo "==================================="
echo " Ubuntu 22.04 Genel Sağlık Kontrolü"
echo " Tarih: $(date)"
echo "==================================="

# Sistem Bilgileri
echo ""
echo "  Sistem Modeli ve Donanım:"
if command -v dmidecode >/dev/null && [[ $(id -u) -eq 0 ]]; then
  dmidecode -t system | grep -E 'Manufacturer|Product Name'
else
  echo "⚠️  dmidecode çalıştırılamadı (root yetkisi gerekebilir veya sanal ortam sınırlaması olabilir)."
fi

echo ""
echo " Ubuntu Sürümü ve Kernel:"
lsb_release -drc
uname -r

# CPU ve RAM Kullanımı
echo ""
echo " CPU Kullanımı:"
top -b -n1 | grep "Cpu(s)" | head -n 1

echo ""
echo " Bellek Kullanımı:"
free -h

# Disk Kullanımı
echo ""
echo "  Disk Durumu:"
df -hT | grep '^/dev'

# Ağ Bağlantısı
echo ""
echo " Ağ Bağlantı Testi (Google DNS):"
ping -c 1 -W 1 8.8.8.8 > /dev/null && echo " ✅ Ağ bağlantısı var" || echo " ❌ Ağ bağlantısı yok!"

# Kritik Servis Kontrolleri
echo ""
echo " Kritik Servis Durumları:"
SERVICES=(nginx gunicorn daphne celery celerybeat redis-server postgresql)

for svc in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$svc"; then
        echo " ✅ $svc çalışıyor"
    else
        echo " ❌ $svc çalışmıyor!"
    fi
done

# Sistem Log Hataları
echo ""
echo " Sistem Log Hataları (son 3 kritik satır):"
if [[ $(id -u) -eq 0 ]]; then
  journalctl -p 3 -xb | tail -n 3
else
  echo "⚠️  journalctl erişimi reddedildi (root değil)."
fi

# Redis Kontrolü
echo ""
echo " Redis Durumu:"
redis-cli -a Tuna2023* ping 2>/dev/null | grep -q PONG && echo " ✅ Redis çalışıyor" || echo " ❌ Redis'e erişilemiyor"

# PostgreSQL Kontrolü
echo ""
echo " PostgreSQL Versiyonu:"
psql -U postgres -Atqc "SELECT version();" 2>/dev/null || echo "⚠️  PostgreSQL erişimi başarısız"

echo ""
echo " ✅ Sağlık Kontrolü Tamamlandı - $(date)"
echo "==================================="
