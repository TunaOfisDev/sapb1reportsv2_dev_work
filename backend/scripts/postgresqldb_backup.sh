#!/bin/bash
set -e

# Yedekleme klasörü
BACKUP_DIR=/srv/samba/PostgresqlDb_backup

# Django projesinin kök dizinine geçiş yap ve sanal ortamı aktifleştir
cd /var/www/sapb1reportsv2 || { echo "HATA: Proje dizinine geçilemedi"; exit 1; }
source venv/bin/activate

# .env dosyasını yükle
set -a
source /var/www/sapb1reportsv2/backend/.env
set +a

# SECRET_KEY ayarını kontrol et
if [ -z "$SECRET_KEY" ]; then
  echo "HATA: SECRET_KEY atanmamış. .env dosyasını kontrol edin."
  exit 1
fi

# PYTHONPATH ayarını yaparak Django ayar dosyasını bulmasını sağla
export PYTHONPATH=/var/www/sapb1reportsv2/backend

# Veritabanı bilgilerini al
PGDB_NAME=$(python3 -c "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'sapreports.settings'; import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['NAME'])")
PGDB_USER=$(python3 -c "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'sapreports.settings'; import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['USER'])")
PGDB_PASSWORD=$(python3 -c "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'sapreports.settings'; import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['PASSWORD'])")
PGDB_HOST=$(python3 -c "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'sapreports.settings'; import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['HOST'])")
PGDB_PORT=$(python3 -c "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'sapreports.settings'; import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['PORT'])")

# Sanal ortamı devre dışı bırak
deactivate

# Yedekleme klasörünün varlığını kontrol et ve yoksa oluştur
if [ ! -d "$BACKUP_DIR" ]; then
  sudo mkdir -p "$BACKUP_DIR" || { echo "HATA: Yedekleme dizini oluşturulamadı! Dir:($BACKUP_DIR)"; exit 1; }
fi
if [ ! -w "$BACKUP_DIR" ]; then
  echo "HATA: Yedekleme dizinine ($BACKUP_DIR) yazma izni yok!"
  exit 1
fi

# Yedekleme dosyası adı
DATE_FORMAT=$(date +'%Y-%m-%d_%H-%M-%S')
BACKUP_FILE=$BACKUP_DIR/${PGDB_NAME}_${DATE_FORMAT}

# Yedekleme işlemi
export PGPASSWORD=$PGDB_PASSWORD

# Custom format yedek (binary)
if ! pg_dump -h "$PGDB_HOST" -p "$PGDB_PORT" -U "$PGDB_USER" -d "$PGDB_NAME" -n public -F c -b -v --no-owner --no-acl -f "${BACKUP_FILE}.dump"; then
  echo "HATA: Özel format yedekleme başarısız"
  unset PGPASSWORD
  exit 1
fi

# Plain-SQL yedek
if ! pg_dump -h "$PGDB_HOST" -p "$PGDB_PORT" -U "$PGDB_USER" -d "$PGDB_NAME" -n public -F p --verbose --no-owner --no-acl -f "${BACKUP_FILE}.sql"; then
  echo "HATA: SQL format yedekleme başarısız"
  unset PGPASSWORD
  exit 1
fi

# SQL yedek dosyasını sıkıştır
if ! gzip "${BACKUP_FILE}.sql"; then
  echo "HATA: SQL yedekleme dosyası sıkıştırılamadı"
  unset PGPASSWORD
  exit 1
fi

# PGPASSWORD değişkenini temizle
unset PGPASSWORD

# Eski yedekleri temizle (son 5 yedeği sakla)
find "$BACKUP_DIR" -name "*.dump" -type f -printf '%T@ %p\n' | sort -n | head -n -5 | cut -d' ' -f2- | xargs -r rm -f
find "$BACKUP_DIR" -name "*.sql.gz" -type f -printf '%T@ %p\n' | sort -n | head -n -5 | cut -d' ' -f2- | xargs -r rm -f

# Yedekleme özeti
DUMP_SIZE=$(du -h "${BACKUP_FILE}.dump" | cut -f1)
SQL_SIZE=$(du -h "${BACKUP_FILE}.sql.gz" | cut -f1)
TOTAL_FILES=$(find "$BACKUP_DIR" -type f | wc -l)

echo "Yedekleme özeti:"
echo "- Özel format (.dump): ${BACKUP_FILE}.dump ($DUMP_SIZE)"
echo "- SQL format (.sql.gz): ${BACKUP_FILE}.sql.gz ($SQL_SIZE)"
echo "- Toplam yedek dosyası: $TOTAL_FILES"
echo "PostgreSQL 17.2 DB yedekleme script'i başarıyla tamamlandı"

exit 0