#!/bin/bash

OUTPUT_FILE="/var/www/sapb1reportsv2/zNotlar/Services/structural_samba_service.md"

echo "🚀 Samba servis bilgileri analiz ediliyor..."

# Başlık
echo "# Samba Servis Yapılandırma Klavuzu" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Bu belge, sistemdeki Samba paylaşımlarının mount yapılarını, kimlik dosyalarını, yetkilendirme ayarlarını ve servis durumlarını içeren teknik bir özet sunar." >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Mount bilgileri
echo "## 📦 Mount Noktaları (/etc/fstab)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
grep -E 'cifs|smbfs' /etc/fstab >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Örnek fstab satırı
echo "### 🧩 Örnek Mount Tanımı (PostgreSQL Yedekleri için)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```ini' >> "$OUTPUT_FILE"
echo "//10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup cifs credentials=/etc/samba/credentials_pg,iocharset=utf8,uid=1000,gid=1000,file_mode=0644,dir_mode=0755 0 0" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Aktif mountlar
echo "### 🔧 Aktif CIFS/Samba Mountlar" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
mount | grep -E 'type cifs|type smbfs' >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# systemd mount unit dosyaları
echo "## ⚙️ Systemd Mount Unit Dosyaları" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
find /etc/systemd/system -name "*.mount" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Samba kimlik dosyaları
echo "## 🔐 Samba Credentials Dosyaları" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### /etc/samba/credentials" >> "$OUTPUT_FILE"
echo '```ini' >> "$OUTPUT_FILE"
grep -v "password" /etc/samba/credentials 2>/dev/null >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### /etc/samba/credentials_pg" >> "$OUTPUT_FILE"
echo '```ini' >> "$OUTPUT_FILE"
grep -v "password" /etc/samba/credentials_pg 2>/dev/null >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# smb.conf
echo "## 🧾 /etc/samba/smb.conf Yapılandırması" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```ini' >> "$OUTPUT_FILE"
cat /etc/samba/smb.conf >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Samba servis durumu
echo "## 📡 Samba Servis Durumu" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### smbd" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
systemctl status smbd | head -n 10 >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### nmbd" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
systemctl status nmbd | head -n 10 >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Standart yönetim ve kurulum komutları
echo "## 🧰 Standart Samba Komutları ve Kurulum Yardımı" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 📦 Kurulum" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "sudo apt update && sudo apt install samba samba-common smbclient -y" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🔐 Samba Kullanıcısı Ekleme" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "sudo smbpasswd -a <kullanici_adi>" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🔄 Samba Servis Yönetimi" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "sudo systemctl restart smbd nmbd" >> "$OUTPUT_FILE"
echo "sudo systemctl enable smbd nmbd" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🧪 Test ve Sorun Giderme" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "testparm                     # smb.conf yapılandırma testi" >> "$OUTPUT_FILE"
echo "sudo smbstatus              # açık oturumları gösterir" >> "$OUTPUT_FILE"
echo "sudo journalctl -fu smbd    # canlı log" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🔗 Paylaşımı Bağlamak İçin (Linux istemci)" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "sudo mount -t cifs //10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup -o credentials=/etc/samba/credentials_pg" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 📁 Sistemde Otomatik Mount (fstab)" >> "$OUTPUT_FILE"
echo '```ini' >> "$OUTPUT_FILE"
echo "//10.130.212.112/PostgresqlDb_backup /mnt/PostgresqlDb_backup cifs credentials=/etc/samba/credentials_pg,iocharset=utf8,uid=1000,gid=1000,file_mode=0644,dir_mode=0755 0 0" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "✅ Ek yönetim komutları ve yapılandırma önerileri klavuza eklendi." >> "$OUTPUT_FILE"


echo "✅ Tamamlandı: Samba yapılandırması '$OUTPUT_FILE' dosyasına eksiksiz olarak kaydedildi."

