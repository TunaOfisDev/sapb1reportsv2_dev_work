#!/bin/bash
# Hata durumunda script'in hemen durmasını sağlar
set -e

# --- AYARLAR ---
SRC_DIR="/var/www/sapb1reportsv2"
DEST_DIR="/home/userbt/Github/sapb1reportsv2_dev_work"
REMOTE_REPO="https://github.com/TunaOfisDev/sapb1reportsv2_dev_work.git"
BRANCH="main"
COMMIT_MSG="Dev snapshot - $(date '+%Y-%m-%d %H:%M:%S')"

echo "📍 Basit Senkronizasyon Scripti Başladı"
echo "➡️  Kaynak: $SRC_DIR"
echo "⬅️  Hedef : $DEST_DIR"

# --- ADIM 1: HEDEF KLASÖRÜ HAZIRLA ---
# Eğer hedef klasörde bir .git deposu yoksa, depoyu klonla.
if [ ! -d "$DEST_DIR/.git" ]; then
    echo "📂 Hedef klasörde Git deposu bulunamadı. Depo klonlanıyor..."
    # Klonlamadan önce olası bozuk kalıntıları temizle
    rm -rf "$DEST_DIR"
    git clone "$REMOTE_REPO" "$DEST_DIR"
else
    echo "✅ Mevcut Git deposu bulundu."
fi

# --- ADIM 2: DOSYALARI KOPYALA ---
echo "🔄 Dosyalar kaynaktan hedefe rsync ile kopyalanıyor..."
# rsync, sadece değişen dosyaları kopyalar.
# --exclude ile .git klasörünün ve diğer gereksiz dosyaların üzerine yazılmasını engelliyoruz.
rsync -av --delete \
    --exclude '.git' \
    --exclude '**/__pycache__' \
    --exclude '**/node_modules' \
    --exclude 'venv/' \
    --exclude '.env' \
    --exclude '*.pyc' \
    "$SRC_DIR/" "$DEST_DIR/"

# --- ADIM 3: DEĞİŞİKLİKLERİ GITHUB'A GÖNDER ---
# Hedef klasöre git
cd "$DEST_DIR"

echo "➕ Değişiklikler Git'e ekleniyor..."
git add .

# Sadece commit edilecek bir değişiklik varsa commit at
if git diff --cached --quiet; then
    echo "✨ Yeni değişiklik bulunamadı. Commit atlanıyor."
else
    echo "📝 Değişiklikler commit ediliyor..."
    git commit -m "$COMMIT_MSG"
fi

echo "⬆️ Değişiklikler GitHub'a gönderiliyor..."
git push origin "$BRANCH"

echo "✅ İşlem başarıyla tamamlandı."