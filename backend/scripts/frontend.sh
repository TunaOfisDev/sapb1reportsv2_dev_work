#!/bin/bash
# Frontend build ve deploy scripti – TARZ Stabil Sürüm
set -euo pipefail

# ─────────── Renkli Çıktılar ───────────
GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m'
success_msg() { echo -e "${GREEN}$1${NC}"; }
error_msg() { echo -e "${RED}$1${NC}" >&2; }
trap 'error_msg "❌ Hata! Kod: $? Komut: $BASH_COMMAND Satır: $LINENO"; exit 1' ERR

# ─────────── Hazırlık ───────────
cd /var/www/sapb1reportsv2/frontend || exit 1
success_msg "📁 frontend dizinine geçildi."

# ─────────── Ortam Değişkenleri ───────────
export NODE_ENV=production
export GENERATE_SOURCEMAP=false
export INLINE_RUNTIME_CHUNK=false
export CI=false
export NODE_OPTIONS="--max-old-space-size=8192"

# ─────────── NPM Kurulumları ───────────
if [ ! -d "node_modules" ]; then
  success_msg "📦 NPM bağımlılıkları yükleniyor..."
  npm install --no-fund --no-audit
fi

# Esbuild kontrolü
if [ ! -d "node_modules/esbuild" ]; then
  success_msg "⚙️ Esbuild paketleri yükleniyor..."
  npm install --save-dev esbuild esbuild-loader craco-esbuild @craco/craco --no-fund --no-audit
fi

# ─────────── Build İşlemi ───────────
success_msg "🏗️ React build başlatılıyor..."
npm run build
cp build/index.html build/404.html

# Build klasörünün www-data erişimine açılması
sudo chown -R userbt:userbt build
sudo chmod -R 775 build
success_msg "🔧 build yetkileri www-data:sapb1 olarak ayarlandı."

# ─────────── GZIP + Brotli ───────────
for dir in js css; do
  static_dir="build/static/$dir"
  if [ -d "$static_dir" ]; then
    find "$static_dir" -type f -name "*.$dir" -exec gzip -9 -k {} \;
    success_msg "📦 $dir dosyaları gzip ile sıkıştırıldı."

    find "$static_dir" -type f -name "*.$dir" -exec brotli --no-copy-stat -9 -f {} \;
    success_msg "📦 $dir dosyaları brotli ile sıkıştırıldı."
  fi
done

# ─────────── NGINX Kontrol & Restart ───────────
if sudo nginx -t; then
  success_msg "✅ Nginx konfigürasyonu doğru."
  sudo systemctl restart nginx
  sudo systemctl enable nginx
  systemctl is-active --quiet nginx && success_msg "🌐 Nginx çalışıyor." || error_msg "Nginx başlatılamadı!"
else
  error_msg "🚫 Nginx konfigürasyon hatası!"
  exit 1
fi

success_msg "🚀 Frontend script tamamlandı."
