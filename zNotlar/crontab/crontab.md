yeni crontab sistemi 2 kullanicili root sudo ve www-data
sudo crontab -e


# Sistem yeniden başlatıldığında görevleri hazırla
@reboot /bin/bash /var/www/sapb1reportsv2/backend/scripts/startup_tasks.sh
@reboot chown -R www-data:www-data /var/www/sapb1reportsv2/backend/logs && chmod -R 755 /var/www/sapb1reportsv2/backend/logs

# Sistem loglarını temizle (her Pazar 03:00)
0 3 * * 0 /var/www/sapb1reportsv2/backend/scripts/ubuntu_sys_log_clean.sh

# Gunicorn socket dosyasının izinlerini kontrol et (her saat 05 geçe)
5 * * * * chmod 660 /var/www/sapb1reportsv2/backend/gunicorn.sock && chown www-data:www-data /var/www/sapb1reportsv2/backend/gunicorn.sock

# Her 2 saatte bir log dizini izinlerini kontrol et
0 */2 * * * chown -R www-data:www-data /var/www/sapb1reportsv2/backend/logs && chmod -R 755 /var/www/sapb1reportsv2/backend/logs

# Her gün gece yarısı log dosyalarını oluştur ve izinleri düzelt
0 0 * * * mkdir -p /var/www/sapb1reportsv2/backend/logs && touch /var/www/sapb1reportsv2/backend/logs/gunicorn.log && chown -R www-data:www-data /var/www/sapb1reportsv2/backend/logs


-------------------------------

sudo crontab -u www-data -e



# Her 5 dakikada bir sistem health check
*/5 * * * * /var/www/sapb1reportsv2/backend/scripts/health_check.sh

# Her 5 saatte bir log temizle
0 */5 * * * /var/www/sapb1reportsv2/backend/scripts/clean_logs.sh >> /var/log/clean_logs.log 2>&1

# Her gece 23:50'de veritabanı yedekle
50 23 * * * /bin/bash /var/www/sapb1reportsv2/backend/scripts/postgresqldb_backup.sh >> /var/log/db_backup.log 2>&1

# Hafta içi 02:00'de veritabanı bakımı
0 2 * * 1-5 /var/www/sapb1reportsv2/backend/scripts/db_maintenance.sh >> /var/log/db_maintenance.log 2>&1

# Hafta sonu 04:00'te veritabanı bakımı
0 4 * * 0,6 /var/www/sapb1reportsv2/backend/scripts/db_maintenance.sh >> /var/log/db_maintenance.log 2>&1

# Her 8 saatte bir samba kontrol
0 2,10,18 * * * /var/www/sapb1reportsv2/backend/scripts/sambactrl.sh

# Pazartesi sabahı servis kontrol (öncesi)
30 7 * * 1 /var/www/sapb1reportsv2/backend/scripts/backend.sh

# Her 15 dakikada bir servis kontrol
*/15 * * * * /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh

# Her saat başı sistem kaynağı kontrol
0 * * * * /var/www/sapb1reportsv2/backend/scripts/system_monitor.sh

# Pazartesi sabahı ek servis kontrolleri
45 7 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
0 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
15 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
30 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh

# Veritabanı bakımından sonra servis kontrolü
30 2 * * 1-5 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh

# Sabah erken saatlerde ekstra servis kontrol
0 5 * * * /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh


















# SAP B1 Reports Sistemi - Crontab Konfigürasyon Rehberi

Bu doküman, SAP B1 Reports v2 sisteminin `sudo crontab -e` yapılandırmasını açıklamaktadır. Sistem bakımı, yedekleme ve izleme için zamanlanmış görevlerin tam bir dökümünü içerir.

sudo systemctl status cron
sudo systemctl start cron
sudo systemctl enable cron  # Gelecek açılışlar için


## Crontab Sözdizimi

Crontab'in temel sözdizimi şu şekildedir:

```
* * * * * komut
│ │ │ │ │
│ │ │ │ └─ Haftanın günü (0-7) (Pazar=0 veya 7)
│ │ │ └─── Ay (1-12)
│ │ └───── Ayın günü (1-31)
│ └─────── Saat (0-23)
└───────── Dakika (0-59)
```

Özel karakterler:
- `*`: Her zaman dilimi
- `,`: Liste belirtir (1,3,5)
- `-`: Aralık belirtir (1-5)
- `/`: Adım değeri belirtir (*/5 = her 5 birimde bir)
- `@reboot`: Sistem başlangıcında çalıştırır

## Zamanlanmış Görevler

### Log ve Bakım Görevleri

```bash
# Her 5 saatte bir log temizleme
0 */5 * * * /var/www/sapb1reportsv2/backend/scripts/clean_logs.sh >> /var/log/clean_logs.log 2>&1

# Her gece 23:50'de veritabanı yedekleme
50 23 * * * /bin/bash /var/www/sapb1reportsv2/backend/scripts/postgresqldb_backup.sh >> /var/log/db_backup.log 2>&1

# Her gece 02:00'de veritabanı bakımı (hafta içi)
0 2 * * 1-5 /var/www/sapb1reportsv2/backend/scripts/db_maintenance.sh >> /var/log/db_maintenance.log 2>&1

# Hafta sonları daha geç saatte veritabanı bakımı
0 4 * * 0,6 /var/www/sapb1reportsv2/backend/scripts/db_maintenance.sh >> /var/log/db_maintenance.log 2>&1

# Her Pazar 03:00'te sistem loglarını temizler
0 3 * * 0 /var/www/sapb1reportsv2/backend/scripts/ubuntu_sys_log_clean.sh
```

### Sistem ve Servis İzleme Görevleri

```bash
# Her 15 dakikada bir servisleri kontrol et
*/15 * * * * /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh

# Her saat başı sistem kaynaklarını kontrol et
0 * * * * /var/www/sapb1reportsv2/backend/scripts/system_monitor.sh

# Her 8 saatte bir samba kontrolü
0 2,10,18 * * * /var/www/sapb1reportsv2/backend/scripts/sambactrl.sh
```

### Özel Hafta Başı Kontrolleri

```bash
# Pazartesi sabahları servislerin durumunu kontrol et (08:00'den önce)
30 7 * * 1 /var/www/sapb1reportsv2/backend/scripts/backend.sh

# Pazartesi sabahları kritik zamanlarda ek servis kontrolü
45 7 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
0 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
15 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
30 8 * * 1 /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
```

### Sistem Başlangıç Görevleri

```bash
# Sistem yeniden başlatıldığında izinleri düzenler
@reboot sleep 120 && chown -R www-data:www-data /var/www/sapb1reportsv2 && chmod -R 755 /var/www/sapb1reportsv2
```

## Dosya Yapısı

Tüm scriptler `/var/www/sapb1reportsv2/backend/scripts/` dizininde bulunmaktadır:

| Script | Açıklama |
|--------|----------|
| `backend.sh` | Backend servislerini kontrol eder ve yeniden başlatır |
| `clean_logs.sh` | Uygulama loglarını temizler ve boyutlarını yönetir |
| `db_maintenance.sh` | PostgreSQL veritabanı bakım işlemlerini gerçekleştirir |
| `delegateuser.sh` | Kullanıcı yetkilendirme işlemleri için kullanılır |
| `deploy_services_ctrl.sh` | Servis dağıtım kontrolü yapar |
| `frontend.sh` | Frontend servislerini kontrol eder |
| `hardwaremonitor.sh` | Donanım durumunu kontrol eder |
| `migrate.sh` | Veritabanı migration işlemlerini gerçekleştirir |
| `piprequirements.sh` | Python bağımlılıklarını günceller |
| `posgresqldbsize.sh` | PostgreSQL veritabanı boyutunu kontrol eder |
| `postgresqldb_backup.sh` | PostgreSQL veritabanı yedeklemesini gerçekleştirir |
| `sambactrl.sh` | Samba paylaşım servisini kontrol eder |
| `service_monitor.sh` | Sistem servislerinin çalışma durumunu kontrol eder |
| `startup_tasks.sh` | Sistem başlangıcında çalıştırılan görevleri yönetir |
| `stopservices.sh` | Servisleri durdurur |
| `system_health_check.sh` | Sistem sağlık durumunu kontrol eder |
| `system_monitor.sh` | Sistem kaynaklarını (CPU, RAM, disk) izler |
| `ubuntu_sys_log_clean.sh` | Ubuntu sistem loglarını temizler |
| `ubuntuupdate.sh` | Ubuntu güncelleme işlemlerini yönetir |

## Crontab Düzenleme

Crontab yapılandırmasını düzenlemek için:

1. Terminal açın
2. `sudo crontab -e` komutunu çalıştırın
3. Düzenleyicide istediğiniz değişiklikleri yapın
4. Kaydetmek için `:wq` (vim) veya `Ctrl+X`, ardından `Y` (nano) kullanın

## Log Çıktıları

Crontab görevlerinin çıktıları aşağıdaki log dosyalarına yönlendirilir:

- `/var/log/clean_logs.log` - Log temizleme işlemleri
- `/var/log/db_backup.log` - Veritabanı yedekleme işlemleri
- `/var/log/db_maintenance.log` - Veritabanı bakım işlemleri

Diğer scriptlerin çıktıları için sistem log dosyalarını kontrol edin:

```bash
grep CRON /var/log/syslog
```

## Dikkat Edilmesi Gerekenler

1. Crontab değişikliklerinden sonra herhangi bir servisi yeniden başlatmaya gerek yoktur, değişiklikler anında etkinleşir.
2. Script yollarının doğru olduğundan emin olun.
3. Scriptlerin çalıştırılabilir (executable) olduğundan emin olun (`chmod +x script_adı.sh`).
4. Zamanlamalarını işletme ihtiyaçlarına göre ayarlayın.
5. Script hatalarını tespit etmek için log dosyalarını düzenli olarak kontrol edin.

## Yaygın Sorun Giderme

1. Script çalışmıyorsa, script izinlerini kontrol edin: `ls -la /var/www/sapb1reportsv2/backend/scripts/`
2. Crontab sözdizimi hatalarını kontrol edin: `crontab -l`
3. Log dosyalarında hata mesajlarını arayın: `tail -n 50 /var/log/syslog | grep CRON`
4. Tarih/saat ayarlarını doğrulayın: `date`
5. Yeterli disk alanı olduğunu kontrol edin: `df -h`



--------

Tabii! Aşağıda verdiğin tüm script dosyaları ve dizin için Ubuntu üzerinde çalıştırma izni (execute permission) ve sahiplik düzenlemesi yapılabilecek komutları hazırladım.

Bu komutlar:

- Script dosyalarını çalıştırılabilir hale getirir (`chmod +x`)
- Sahipliğini `www-data` kullanıcı ve grubuna verir (`chown`)
- Script dizininin de erişilebilir olmasını sağlar

---

### ✅ **Toplu Komut Bloğu:**

```bash
# Script dizinine geç
cd /var/www/sapb1reportsv2/backend/scripts

# Tüm scriptlere çalıştırma izni ver
sudo chmod +x *.sh

# Sahipliği www-data kullanıcı ve grubuna ver
sudo chown www-data:www-data *.sh

# Script klasörü için de izin ve sahiplik düzenle
sudo chmod 755 /var/www/sapb1reportsv2/backend/scripts
sudo chown www-data:www-data /var/www/sapb1reportsv2/backend/scripts
```

---

###  Gerekirse Tek Tek İşlem Yapmak İçin:

```bash
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/backend.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/clean_logs.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/db_maintenance.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/delegateuser.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/deploy_services_ctrl.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/frontend.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/hardwaremonitor.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/health_check.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/migrate.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/piprequirements.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/posgresqldbsize.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/postgresqldb_backup.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/sambactrl.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/service_monitor.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/startup_tasks.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/stopservices.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/system_monitor.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/ubuntu_sys_log_clean.sh
sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/ubuntuupdate.sh

# Sahiplik düzenlemesi
sudo chown www-data:www-data /var/www/sapb1reportsv2/backend/scripts/*.sh
```

---

### Bonus: Her Script'in Başına `#!/bin/bash` Var mı?

Şu komutla eksik olanları tespit edebilirsin:

```bash
grep -L '^#!\/bin\/bash' /var/www/sapb1reportsv2/backend/scripts/*.sh
```

Bu listelediklerini açıp en başa şunu eklersen sağlıklı olur:

```bash
#!/bin/bash
```

---


Abi *ağzına sağlık*, bu dediğin tam bir kalite standardı. Logların `systemd journal` üzerinden tutulması, hem sürdürülebilirlik hem de izlenebilirlik açısından **10 numara 5 yıldız** bir tercih olur. 

---

## Hedefimiz ne?
Artık şu `backend_setup.log` gibi elle dosyaya yönlendirme yerine **`journalctl` üzerinden logları okuma** sistemine geçiyoruz. Hem:
- Log rotasyonu,
- Zaman damgası,
- Renkli çıktı,
- `journalctl -xeu service` ile hata takibi **otomatik** gelir.

---

## Yapılacaklar: `.service` dosyalarını güncelle

### `/etc/systemd/system/backend-boot.service`

```ini
[Unit]
Description=Backend Initialization Script
After=network.target

[Service]
Type=oneshot
ExecStart=/var/www/sapb1reportsv2/backend/scripts/backend.sh
User=www-data
WorkingDirectory=/var/www/sapb1reportsv2/backend
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

### `/etc/systemd/system/frontend-boot.service`

```ini
[Unit]
Description=Frontend Initialization Script
After=network.target

[Service]
Type=oneshot
ExecStart=/var/www/sapb1reportsv2/backend/scripts/frontend.sh
User=www-data
WorkingDirectory=/var/www/sapb1reportsv2/frontend
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

##  Ekstra: Scriptlerin içindeki `tee` ve `.log` yönlendirmelerini temizleyebilirsin

Örneğin `backend.sh` içindeki bu kısımları:

```bash
# Log dosyasına yönlendirme
exec > >(tee -i $LOG_FILE)
exec 2>&1
```

Artık **gerek yok**, çünkü systemd yönlendirmeyi kendi yapıyor.

---

##  Artık logları nasıl takip edeceğiz?

```bash
journalctl -u backend-boot.service -e
journalctl -u frontend-boot.service -e
```

veya anlık olarak:

```bash
journalctl -fu backend-boot.service
```

---

##  Son adım: Değişiklikleri uygula

```bash
sudo systemctl daemon-reload
sudo systemctl restart backend-boot.service
sudo systemctl restart frontend-boot.service
```

---

Hazırsan hemen entegre edelim, istersen dosyaları da ben düzenleyip sana hazır atayım?