#!/bin/bash
set -euo pipefail

SRC_BASE="/var/www/sapb1reportsv2"
DEST_BASE="/home/user/Github/sapb1reportsv2_dev_work"
GIT_META="/home/user/gitmeta/devWork.git"
EXCLUDES="$SRC_BASE/backend/scripts/rsync-exclude.txt"
REMOTE_REPO="git@github.com:TunaOfisDev/sapb1reportsv2_dev_work.git"
BRANCH="main"

echo "📍 [WORK SYNC] başladı"
echo "📂 SRC        : $SRC_BASE"
echo "📂 DEST       : $DEST_BASE"
echo "🗃️ GIT META   : $GIT_META"

# GIT bağla
if [[ ! -d "$GIT_META" ]]; then
  git clone --separate-git-dir="$GIT_META" "$REMOTE_REPO" "$DEST_BASE"
else
  echo "🔗 Bağlanıyor: mevcut git meta"
  rm -rf "$DEST_BASE/.git"
  echo "gitdir: $GIT_META" > "$DEST_BASE/.git"
fi

# Rsync
for d in backend frontend zNotlar .vscode; do
  echo "📁 Senkronize: $d"
  rsync -av --delete --exclude-from="$EXCLUDES" "$SRC_BASE/$d/" "$DEST_BASE/$d/"
done

# Git işlemleri
cd "$DEST_BASE"

# YENİ: Git komutu çalıştırmadan önce reponun sağlığını kontrol et
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "❌ HATA: Geçerli bir Git reposu değil veya bozuk. Lütfen manuel kontrol edin: $DEST_BASE"
  echo "👉 Çözüm önerisi: 'rm -rf $GIT_META' komutu ile bozuk meta veriyi silip script'i yeniden çalıştırın."
  exit 1
fi

echo "➕ Git stage başlatılıyor..."
git add -A

if git diff --cached --quiet; then
  echo "⚠️ Commit yapılacak bir şey yok"
else
  COMMIT_MSG="🧪 dev work snapshot - $(date '+%Y-%m-%d %H:%M')"
  git commit -m "$COMMIT_MSG"
fi

echo "⬇️ Pull yapılıyor..."
git pull --no-rebase --autostash origin "$BRANCH"

echo "⬆️ Push yapılıyor..."
git push origin "$BRANCH"

echo "✅ [WORK SYNC] başarıyla tamamlandı"
