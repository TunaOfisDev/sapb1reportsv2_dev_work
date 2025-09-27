# Django Uygulama Sağlık Kontrolü Servisi (Healthcheck)

## Amaç

Healthcheck servisi, Django tabanlı web uygulamasının (SAP B1 Reports v2) tüm bileşenlerini (nginx, gunicorn, daphne, celery, celerybeat, postgresql) sürekli olarak izleyen ve herhangi bir servis durduğunda otomatik olarak müdahale eden bir sistem hizmetidir. Bu servis, özellikle pazartesi sabahları (08:00-08:30 arası) yaşanan servis kesintilerini önlemek ve sistemin 7/24 kesintisiz çalışmasını sağlamak için tasarlanmıştır.

## Servis Bileşenleri

### 1. Systemd Servis Dosyası

```ini
[Unit]
Description=Health Check for Django Application
After=network.target

[Service]
Type=simple
User=www-data
ExecStart=/var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
Restart=on-failure
RestartSec=30
StartLimitIntervalSec=300
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

Bu dosya `/etc/systemd/system/healthcheck.service` konumunda bulunur.

### 2. Servis İzleme Scripti

```bash
#!/bin/bash
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/service_monitor.log"

# Log dizinini ve dosyasını oluştur
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chown www-data:www-data "$LOG_FILE"

log_message() {
  echo "$(date): $1" | sudo tee -a "$LOG_FILE"
}

backend_restart_count=0
max_backend_restarts=3

# Backend.sh çalıştırma fonksiyonu
run_backend_script() {
  if [ $backend_restart_count -lt $max_backend_restarts ]; then
    log_message "Backend.sh scripti çalıştırılıyor (Deneme: $((backend_restart_count+1))/$max_backend_restarts)..."
    backend_restart_count=$((backend_restart_count+1))
    
    # trap hatasını önlemek için bash komutunu kullan
    sudo bash /var/www/sapb1reportsv2/backend/scripts/backend.sh
    
    # Script çalıştıktan sonra servisi tekrar kontrol et
    sleep 10
    if systemctl is-active --quiet $1; then
      log_message "$1 servisi başarıyla başlatıldı."
      return 0
    else
      log_message "$1 servisi hala çalışmıyor."
      return 1
    fi
  else
    log_message "UYARI: Maksimum backend.sh çalıştırma sayısına ulaşıldı."
    return 1
  fi
}

function check_service {
  if ! systemctl is-active --quiet $1; then
    log_message "$1 servisi çalışmıyor! Backend.sh scripti çalıştırılacak."
    run_backend_script $1
  else
    log_message "$1 servisi çalışıyor."
  fi
}

log_message "Servis izleme scripti başlatıldı"

# Servisleri kontrol et
check_service nginx
check_service gunicorn
check_service daphne
check_service celery
check_service celerybeat

log_message "Servis izleme scripti tamamlandı"
log_message "----------------------------------------"
```

Bu script `/var/www/sapb1reportsv2/backend/scripts/service_monitor.sh` konumunda bulunur.

### 3. Backend-Restart Servisi

```ini
[Unit]
Description=Django Backend Restart Service
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/var/www/sapb1reportsv2/backend/scripts/backend.sh
RemainAfterExit=no

[Install]
WantedBy=multi-user.target
```

Bu dosya `/etc/systemd/system/backend-restart.service` konumunda bulunur.

## Kurulum

Sağlık kontrol servisini kurmak için aşağıdaki adımları izleyin:

1. Servis dosyasını oluşturun:
```bash
sudo nano /etc/systemd/system/healthcheck.service
# İçeriği yukarıdaki gibi yapıştırın
```

2. Backend-restart servisini oluşturun:
```bash
sudo nano /etc/systemd/system/backend-restart.service
# İçeriği yukarıdaki gibi yapıştırın
```

3. Servisleri etkinleştirin:
```bash
sudo systemctl daemon-reload
sudo systemctl enable healthcheck.service
sudo systemctl enable backend-restart.service
sudo systemctl start healthcheck.service
```

## Çalışma Prensibi

1. Healthcheck servisi, systemd tarafından sistem başlangıcında otomatik olarak başlatılır
2. Servis, service_monitor.sh scriptini çalıştırır
3. Script, tüm kritik servisleri (nginx, gunicorn, daphne, celery, celerybeat) kontrol eder
4. Herhangi bir servis çalışmıyorsa, backend.sh scriptini çağırarak servisin yeniden başlatılmasını sağlar
5. Tüm işlemler `/var/www/sapb1reportsv2/backend/logs/service_monitor.log` dosyasına kaydedilir

## Otomatik İzleme Zamanlaması (Crontab)

Crontab, sağlık kontrolünün belirli zamanlarda ek olarak çalışmasını sağlar:

```
# Her 15 dakikada bir servisleri kontrol et
*/15 * * * * /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh

# Her saat başı sistem kaynaklarını kontrol et
0 * * * * /var/www/sapb1reportsv2/backend/scripts/system_monitor.sh

# Pazartesi sabahları özellikle kritik zamanlarda servisleri kontrol et
30 7 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
45 7 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
0 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
15 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
30 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
```

## Sorun Giderme

### Servis Durumunu Kontrol Etme
```bash
sudo systemctl status healthcheck
```

### Log Dosyalarını İnceleme
```bash
sudo tail -f /var/www/sapb1reportsv2/backend/logs/service_monitor.log
```

### Servisi Yeniden Başlatma
```bash
sudo systemctl restart healthcheck
```

### İzinleri Kontrol Etme
```bash
sudo ls -la /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
```

## Notlar ve Öneriler

1. **Servis Yapılandırması**: Eğer servis sürekli çöküyorsa, RestartSec ve StartLimitIntervalSec parametrelerini arttırmayı düşünün.

2. **Log Rotasyonu**: Log dosyaları zamanla büyüyebilir. Düzenli olarak logrotate yapılandırması ekleyerek log dosyalarının boyutunu kontrol edin.

3. **Daphne Sorunları**: Daphne servisi sık sık sorun yaşıyorsa, Django ASGI yapılandırmasını gözden geçirin veya servisi şu şekilde düzenleyin:
   ```bash
   sudo nano /etc/systemd/system/daphne.service
   # Environment=DJANGO_SETTINGS_MODULE parametresini doğru olduğundan emin olun
   ```

4. **İzleme Bildirimleri**: Kritik servis kesintilerinde e-posta veya SMS bildirimleri için servisi şu şekilde geliştirebilirsiniz:
   ```bash
   # service_monitor.sh içinde bildirim fonksiyonu ekleyin
   send_notification() {
     message="$1"
     # E-posta gönderme komutu
     echo "$message" | mail -s "Servis Uyarısı" admin@example.com
   }
   ```

Bu servis, sistemin sağlıklı kalmasını sağlayarak manuel müdahale ihtiyacını azaltır ve servis kesintilerini minimize eder.

# system_monitor.sh için çalıştırma izni verin
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/system_monitor.sh

# System monitor script için de çalıştırma izni verin (oluşturduysanız)
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/system_monitor.sh

# Tüm scriptlerin izinlerini kontrol edip düzenleyelim
sudo find /var/www/sapb1reportsv2/backend/scripts -name "*.sh" -type f -exec chmod +x {} \;

# Dosya sahipliğini de düzenleyelim
sudo chown www-data:www-data /var/www/sapb1reportsv2/backend/scripts/*.sh