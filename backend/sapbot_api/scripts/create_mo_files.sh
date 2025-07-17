#!/bin/bash
# create_mo_files.sh

echo "SAPBot API .mo dosyaları oluşturuluyor..."

cd /var/www/sapb1reportsv2/backend/sapbot_api

# İngilizce
msgfmt locale/en/LC_MESSAGES/django.po -o locale/en/LC_MESSAGES/django.mo

# Türkçe  
msgfmt locale/tr/LC_MESSAGES/django.po -o locale/tr/LC_MESSAGES/django.mo

# İzinleri ayarla
sudo chown -R www-data:sapb1 locale/
sudo chmod -R 644 locale/*/*/*.mo

echo "✅ .mo dosyaları oluşturuldu!"