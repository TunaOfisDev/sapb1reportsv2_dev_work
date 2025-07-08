sudo chown -R www-data:www-data /var/www/sapb1reportsv2/backend/logs
sudo setfacl -m u:user:rwX /var/www/sapb1reportsv2/backend/logs


sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/permissions_fix.sh
