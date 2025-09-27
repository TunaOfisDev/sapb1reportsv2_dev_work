# backend/scripts/openvpn_status.sh

#!/bin/bash

echo "🔍 VPN Durum Raporu"

if ip a | grep -q "tun0"; then
  echo "✅ TUN cihazı: aktif"
else
  echo "❌ TUN cihazı: yok"
fi

echo ""
echo "📡 Bağlantı Testi (10.0.255.1):"
ping -c 1 -W 1 10.0.255.1 &> /dev/null && echo "✅ Ulaşılıyor" || echo "❌ Erişilemiyor"

echo ""
echo "📍 Route Bilgileri (VPN):"
ip route | grep tun0

echo ""
echo "🧾 VPN Log Son 5 Satır:"
tail -n 5 /var/www/sapb1reportsv2/backend/logs/openvpn_coslat.log
