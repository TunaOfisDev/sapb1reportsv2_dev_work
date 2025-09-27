#!/bin/bash

# Thumbnail üretim durumu kontrol ve tetikleyici scripti
# Kullanım: ./thumbnail-debug.sh <file_id>

set -euo pipefail

GREEN='\033[1;32m'
RED='\033[0;31m'
NC='\033[0m'
MEDIA_ROOT="/var/www/sapb1reportsv2/backend/media"
LOG_FILE="/var/www/sapb1reportsv2/backend/logs/filesharehubv2.log"

success() { echo -e "${GREEN}$1${NC}"; }
fail()    { echo -e "${RED}$1${NC}"; }
abort()   { fail "$1"; exit 1; }

# 🔹 Parametre kontrolü
FILE_ID="${1:-}"
[ -z "$FILE_ID" ] && abort "Kullanım: ./thumbnail-debug.sh <file_id>"

# 🔹 Django shell üzerinden thumbnail path kontrol et
THUMB_PATH=$(python3 manage.py shell -c "from filesharehub_v2.models.filerecord import FileRecord; \
try:
 f=FileRecord.objects.get(file_id=$FILE_ID); print(f.thumbnail_path)
except:
 print('NOT_FOUND')" 2>/dev/null)

if [[ "$THUMB_PATH" == "NOT_FOUND" ]]; then
  abort "🔴 file_id=$FILE_ID için veritabanında kayıt bulunamadı!"
fi

FULL_PATH="$MEDIA_ROOT/$THUMB_PATH"

# 🔹 Dosya var mı kontrol et
if [ -f "$FULL_PATH" ]; then
  FILE_SIZE=$(du -h "$FULL_PATH" | cut -f1)
  success "🟢 Thumbnail dosyası var: $FULL_PATH ($FILE_SIZE)"
else
  fail "🟠 Thumbnail dosyası yok: $FULL_PATH"
  echo "⏳ Üretim Celery ile tetikleniyor..."
  python3 manage.py shell -c "from filesharehub_v2.tasks.generate_thumbnail import generate_thumbnail; generate_thumbnail.delay($FILE_ID)"
  echo "📜 Log takibi için:"
  echo "tail -f $LOG_FILE | grep $FILE_ID"
fi
