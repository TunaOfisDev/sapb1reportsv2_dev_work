# Samba Servis Yapılandırma Klavuzu

Bu belge, sistemdeki Samba paylaşımlarının mount yapılarını, kimlik dosyalarını, yetkilendirme ayarlarını ve servis durumlarını içeren teknik bir özet sunar.

---

## 📦 Mount Noktaları (/etc/fstab)

```bash
//10.131.212.112/b1_shf/SAP/FILES/PATH/Images /mnt/product_picture cifs credentials=/etc/samba/credentials,iocharset=utf8,uid=1000,gid=1000,file_mode=0775,dir_mode=0775 0 0
//192.168.2.200/gorseller /mnt/gorseller cifs credentials=/etc/samba/credentials,vers=3.0,iocharset=utf8,ro,file_mode=0444,dir_mode=0555 0 0
//10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup cifs credentials=/etc/samba/credentials_pg,iocharset=utf8,sec=ntlm 0 0
```

### 🧩 Örnek Mount Tanımı (PostgreSQL Yedekleri için)

```ini
//10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup cifs credentials=/etc/samba/credentials_pg,iocharset=utf8,uid=1000,gid=1000,file_mode=0644,dir_mode=0755 0 0
```

### 🔧 Aktif CIFS/Samba Mountlar

```bash
//192.168.2.200/gorseller on /mnt/gorseller type cifs (rw,relatime,vers=default,cache=strict,username=tuna,uid=0,noforceuid,gid=0,noforcegid,addr=192.168.2.200,file_mode=0444,dir_mode=0555,iocharset=utf8,soft,nounix,serverino,mapposix,rsize=1048576,wsize=1048576,bsize=1048576,retrans=1,echo_interval=60,actimeo=1,closetimeo=1)
//10.131.212.112/b1_shf/SAP/FILES/PATH/Images on /mnt/product_picture type cifs (rw,relatime,vers=3.1.1,cache=strict,username=tuna,uid=1000,forceuid,gid=1000,forcegid,addr=10.131.212.112,file_mode=0775,dir_mode=0775,iocharset=utf8,soft,nounix,serverino,mapposix,rsize=4194304,wsize=4194304,bsize=1048576,retrans=1,echo_interval=60,actimeo=1,closetimeo=1)
```

## ⚙️ Systemd Mount Unit Dosyaları

```bash
/etc/systemd/system/mnt-gorseller.mount
/etc/systemd/system/multi-user.target.wants/mnt-gorseller.mount
```

## 🔐 Samba Credentials Dosyaları

### /etc/samba/credentials
```ini
```

### /etc/samba/credentials_pg
```ini
```

## 🧾 /etc/samba/smb.conf Yapılandırması

```ini
[global]
   workgroup = WORKGROUP
   server string = SAPB1 Samba Server
   netbios name = sapb1-dev-srv
   security = user
   map to guest = bad user
   dns proxy = no
   server role = standalone server
   log file = /var/log/samba/log.%m
   max log size = 1000
   logging = file
   panic action = /usr/share/samba/panic-action %d
   obey pam restrictions = yes
   unix password sync = yes
   passwd program = /usr/bin/passwd %u
   passwd chat = *New*password* %n\n *Retype*new*password* %n\n *updated*
   pam password change = yes
   usershare allow guests = no

# =================== Paylaşımlar ===================

[sapb1reportsv2]
   path = /var/www/sapb1reportsv2
   valid users = user
   read only = no
   force user = www-data
   create mask = 0775
   directory mask = 0775

[gorseller]
   path = /mnt/gorseller
   available = yes
   valid users = tuna
   read only = yes
   browseable = yes
   guest ok = no
   create mask = 0444
   directory mask = 0555

[product_picture]
   path = /mnt/product_picture
   valid users = tuna
   read only = yes
   browseable = yes
   guest ok = no
   create mask = 0444
   directory mask = 0555

[PostgresqlDb_backup]
   path = /srv/samba/PostgresqlDb_backup
   valid users = hanarapdb
   read only = yes
   browseable = yes
   guest ok = no
   create mask = 0755
   directory mask = 0755
   comment = PostgreSQL otomatik yedek klasörü
```

## 📡 Samba Servis Durumu

### smbd
```bash
● smbd.service - Samba SMB Daemon
     Loaded: loaded (/usr/lib/systemd/system/smbd.service; enabled; preset: enabled)
     Active: active (running) since Mon 2025-06-09 21:16:45 +03; 10min ago
       Docs: man:smbd(8)
             man:samba(7)
             man:smb.conf(5)
    Process: 9621 ExecCondition=/usr/share/samba/is-configured smb (code=exited, status=0/SUCCESS)
   Main PID: 9624 (smbd)
     Status: "smbd: ready to serve connections..."
      Tasks: 4 (limit: 9327)
```

### nmbd
```bash
● nmbd.service - Samba NMB Daemon
     Loaded: loaded (/usr/lib/systemd/system/nmbd.service; enabled; preset: enabled)
     Active: active (running) since Mon 2025-06-09 21:16:45 +03; 10min ago
       Docs: man:nmbd(8)
             man:samba(7)
             man:smb.conf(5)
    Process: 9612 ExecCondition=/usr/share/samba/is-configured nmb (code=exited, status=0/SUCCESS)
   Main PID: 9619 (nmbd)
     Status: "nmbd: ready to serve connections..."
      Tasks: 1 (limit: 9327)
```

## 🧰 Standart Samba Komutları ve Kurulum Yardımı

### 📦 Kurulum
```bash
sudo apt update && sudo apt install samba samba-common smbclient -y
```

### 🔐 Samba Kullanıcısı Ekleme
```bash
sudo smbpasswd -a <kullanici_adi>
```

### 🔄 Samba Servis Yönetimi
```bash
sudo systemctl restart smbd nmbd
sudo systemctl enable smbd nmbd
```

### 🧪 Test ve Sorun Giderme
```bash
testparm                     # smb.conf yapılandırma testi
sudo smbstatus              # açık oturumları gösterir
sudo journalctl -fu smbd    # canlı log
```

### 🔗 Paylaşımı Bağlamak İçin (Linux istemci)
```bash
sudo mount -t cifs //10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup -o credentials=/etc/samba/credentials_pg
```

### 📁 Sistemde Otomatik Mount (fstab)
```ini
//10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup cifs credentials=/etc/samba/credentials_pg,iocharset=utf8,uid=1000,gid=1000,file_mode=0644,dir_mode=0755 0 0
```

✅ Ek yönetim komutları ve yapılandırma önerileri klavuza eklendi.
