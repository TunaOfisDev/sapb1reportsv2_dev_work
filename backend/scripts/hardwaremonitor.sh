#!/bin/bash

# Ubuntu Donanım İzleme Scripti
# Hazırlayan: ChatGPT

echo "==================================="
echo "       Ubuntu Donanım Bilgileri"
echo "==================================="

# İşlemci (CPU) Bilgileri
echo -e "\nİşlemci (CPU) Bilgileri:"
lscpu | grep -E 'Model name|CPU MHz|Socket|Core|Thread'

# RAM Bilgileri
echo -e "\nBellek (RAM) Bilgileri:"
free -h

# Hard Disk Bilgileri
echo -e "\nDisk (Harddisk) Bilgileri:"
df -h | grep '^/dev/'


# İşletim Sistemi Bilgileri
echo -e "\nİşletim Sistemi Bilgileri:"
lsb_release -a 2>/dev/null

# Sensör Bilgileri (CPU Sıcaklık vs.)
echo -e "\nSensör Bilgileri (CPU, Fan, Voltaj vs.):"
if command -v sensors &>/dev/null; then
    sensors
else
    echo "lm-sensors yüklü değil. Sensör bilgisi almak için:"
    echo "sudo apt install lm-sensors -y && sudo sensors-detect"
fi

# Ağ (Network) Bilgileri
echo -e "\n==================================="
echo "         Ağ (Network) Bilgileri"
echo "==================================="

# IP ve Ağ Arayüzleri
echo -e "\nAğ Arayüzleri ve IP Adresleri:"
ip -c a | grep -E '^[0-9]+|inet ' --color=never

# Varsayılan Ağ Geçidi
echo -e "\nVarsayılan Ağ Geçidi:"
ip route show default

# DNS Sunucuları
echo -e "\nDNS Sunucuları:"
systemd-resolve --status | grep 'DNS Servers' | awk '{print $3}' | sort | uniq

# Açık Portlar ve Aktif Bağlantılar
echo -e "\nAçık Portlar ve Aktif Bağlantılar:"
sudo netstat -tulnp | grep LISTEN

echo -e "\n✅ Donanım ve ağ bilgileri başarıyla alındı!"
