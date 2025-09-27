
crontab -l  # Kullanıcı bazlı cron görevlerini listele
sudo crontab -l  # Root seviyesinde cron görevlerini listele
crontab -r  # Kullanıcı bazlı cron görevlerini temizler
sudo crontab -l
sudo reboot
ls -ld /var/www/sapb1reportsv2




sudo crontab -e


# Her 5 saatte bir log temizleme
0 */5 * * * /var/www/sapb1reportsv2/backend/scripts/clean_logs.sh >> /var/log/clean_logs.log 2>&1

# Her gece 23:50'de veritabanı yedekleme
50 23 * * * /bin/bash /var/www/sapb1reportsv2/backend/scripts/postgresqldb_backup.sh >> /var/log/db_backup.log 2>&1

# Her gece 02:00'de veritabanı bakımı
0 2 * * * /var/www/sapb1reportsv2/backend/scripts/db_maintenance.sh >> /var/log/db_maintenance.log 2>&1

# her Pazar 03:00’te çalıştırır sistem loglarini temizler
0 3 * * 0 /var/www/sapb1reportsv2/backend/scripts/ubuntu_sys_log_clean.sh

# Sistem her yeniden başlatıldığında, /var/www/sapb1reportsv2 klasörünün sahipliğini www-data'ya ayarlar
# ve tüm dosya ve klasörlerin izinlerini 755 olarak belirler.
@reboot sleep 60 && chown -R www-data:www-data /var/www/sapb1reportsv2 && chmod -R 755 /var/www/sapb1reportsv2

# Her 6 saatte bir tüm fstab girişlerini yeniden bağlamak için mount -a komutunu çalıştırır.
0 */6 * * * /var/www/sapb1reportsv2/backend/scripts/sambactrl.sh





####
 Alternatif: Crontab Yerine Systemd Kullanmak
Crontab’ın @reboot özelliği bazen güvenilir olmayabilir. Bunun yerine systemd kullanarak görevleri sistem açılışında kesin çalıştırabiliriz.

sudo nano /etc/systemd/system/custom-startup.service


[Unit]
Description=Custom Startup Tasks
After=network.target

[Service]
ExecStart=/var/www/sapb1reportsv2/backend/scripts/startup_tasks.sh
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target


Yeni bir startup script oluştur:
sudo nano /var/www/sapb1reportsv2/backend/scripts/startup_tasks.sh

#!/bin/bash
sleep 60
chown -R www-data:www-data /var/www/sapb1reportsv2
chmod -R 755 /var/www/sapb1reportsv2


 Script’i çalıştırılabilir yap:

 sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/startup_tasks.sh

 Servisi etkinleştir ve başlat:
sudo systemctl daemon-reload
sudo systemctl enable custom-startup.service
sudo systemctl start custom-startup.service

