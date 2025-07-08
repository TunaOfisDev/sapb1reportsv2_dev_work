sudo visudo -f /etc/sudoers.d/sapb1reports bu şekilde vir visudo oluşturdum doğrumu
  GNU nano 7.2                                              /etc/sudoers.d/sapb1reports.tmp                                                        # /etc/sudoers.d/sapb1reports
user ALL=(ALL) NOPASSWD: /var/www/sapb1reportsv2/backend/scripts/postgresqldb_backup.sh
user ALL=(ALL) NOPASSWD: /bin/chown, /bin/chmod, /bin/mkdir, /usr/bin/tee, /bin/systemctl  
