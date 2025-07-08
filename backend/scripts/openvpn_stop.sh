#!/bin/bash
# path: backend/scripts/openvpn_stop.sh

VPN_CONFIG="/etc/openvpn/coslat.conf"
PID_FILE="/run/openvpn_coslat.pid"

echo "🛑 OpenVPN durduruluyor..."

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        sudo kill "$PID"
        echo "✅ PID $PID öldürüldü."
    else
        echo "⚠️ PID $PID zaten aktif değil."
    fi
    sudo rm -f "$PID_FILE"
else
    echo "🔍 PID dosyası yok. Süreç doğrudan aranıyor..."
    sudo pkill -f "openvpn --config $VPN_CONFIG" || true
fi

# tun0 interface’i temizle
sudo ip link delete tun0 2>/dev/null || true

echo "✅ OpenVPN kapatıldı."
