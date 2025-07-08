#!/bin/bash

set -e

BACKEND_SRC="/var/www/sapb1reportsv2/backend"
FRONTEND_SRC="/var/www/sapb1reportsv2/frontend/src"
OUTPUT_BASE="/var/www/sapb1reportsv2/zNotlar/convet_to_md"
BACKEND_DST="$OUTPUT_BASE/backend_md_ready"
FRONTEND_DST="$OUTPUT_BASE/frontend_md_ready"
FINAL_ZIP="$OUTPUT_BASE/converted_code_md.zip"
PY_SCRIPT="$BACKEND_SRC/convert_to_md.py"
PYTHON_EXEC="/var/www/sapb1reportsv2/venv/bin/python3"  # Sanal ortamın Python yolu

# 🔁 Ön temizlik
echo "[1/5] Geçici dizinler temizleniyor..."
rm -rf "$BACKEND_DST" "$FRONTEND_DST" "$FINAL_ZIP"

# 🎯 Backend modüllerini settings.py'den al
echo "[2/5] Backend hedef klasörler hazırlanıyor..."
BACKEND_MODULES=$($PYTHON_EXEC -c "import sys; sys.path.append('$BACKEND_SRC'); from sapreports.settings import CUSTOM_APPS; print(' '.join(CUSTOM_APPS))")

# Modülleri dizi olarak oku
IFS=' ' read -r -a BACKEND_MODULES <<< "$BACKEND_MODULES"

# Hata kontrolü: BACKEND_MODULES boşsa
if [ -z "$BACKEND_MODULES" ]; then
    echo "Hata: BACKEND_MODULES alınamadı. settings.py kontrol edin."
    exit 1
fi

for module in "${BACKEND_MODULES[@]}"; do
    SRC="$BACKEND_SRC/$module"
    DST="$BACKEND_DST/$module"
    echo " > $module"
    $PYTHON_EXEC "$PY_SCRIPT" "$SRC" "$DST"
done

# 🎯 Frontend sadece src
echo "[3/5] Frontend src dönüştürülüyor..."
$PYTHON_EXEC "$PY_SCRIPT" "$FRONTEND_SRC" "$FRONTEND_DST"

# 🗜️ Zip oluştur
echo "[4/5] Tüm markdown dosyaları zipleniyor..."
cd "$OUTPUT_BASE"
zip -r "$FINAL_ZIP" "backend_md_ready" "frontend_md_ready" > /dev/null

echo "[5/5] ✔️ İşlem tamamlandı: $FINAL_ZIP"