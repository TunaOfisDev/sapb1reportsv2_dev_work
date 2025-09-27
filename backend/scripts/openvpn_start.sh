#!/bin/bash
# path: backend/scripts/openvpn_start.sh

set -e

VPN_CONFIG="/etc/openvpn/coslat.conf"
PID_FILE="/run/openvpn_coslat.pid"
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/openvpn_coslat.log"

echo "🔍 OpenVPN durum kontrol ediliyor..."

# Çalışıyorsa tekrar başlatma
if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" > /dev/null 2>&1; then
    echo "🔒 OpenVPN zaten çalışıyor (PID: $(cat $PID_FILE))."
    exit 0
fi

echo "🚧 Eski TUN arayüzü (tun0) temizleniyor..."
sudo ip link delete tun0 2>/dev/null || true
sudo ip addr flush dev tun0 2>/dev/null || true

echo "🚀 OpenVPN bağlantısı başlatılıyor..."
sudo openvpn \
  --config "$VPN_CONFIG" \
  --daemon \
  --writepid "$PID_FILE" \
  --log "$LOG_FILE"

sleep 1

if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" > /dev/null 2>&1; then
    echo "✅ OpenVPN başarıyla başlatıldı (PID: $(cat $PID_FILE))"
    echo "📜 Log: $LOG_FILE"
else
    echo "❌ OpenVPN başlatılamadı. Log dosyasını kontrol edin: $LOG_FILE"
    exit 1
fi
