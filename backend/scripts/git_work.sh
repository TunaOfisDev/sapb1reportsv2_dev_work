#!/bin/bash
set -euo pipefail

# --- DEĞİŞKENLER ---
SRC_BASE="/var/www/sapb1reportsv2"
DEST_BASE="/home/user/Github/sapb1reportsv2_dev_work"
GIT_META="/home/user/gitmeta/devWork.git"
EXCLUDES="$SRC_BASE/backend/scripts/rsync-exclude.txt"
BRANCH="main"

# 1. Şirket Reposu Bilgileri
COMPANY_REMOTE_REPO="git@github.com-company:TunaOfisDev/sapb1reportsv2_dev_work.git"

# 2. Kişisel Repo Bilgileri
PERSONAL_REMOTE_NAME="personal"
PERSONAL_REMOTE_REPO="git@github.com-personal:selimkocak/sapb1reportsv2_dev_work.git"


echo "📍 [WORK SYNC] başladı"
echo "📂 SRC         : $SRC_BASE"
echo "📂 DEST        : $DEST_BASE"
echo "🗃️ GIT META    : $GIT_META"

# GIT bağla
if [[ ! -d "$GIT_META" ]]; then
  echo "✨ Git meta bulunamadı. Temiz bir klonlama başlatılıyor..."
  rm -rf "$DEST_BASE"
  git clone --separate-git-dir="$GIT_META" "$COMPANY_REMOTE_REPO" "$DEST_BASE"
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

# DÜZELTME: Hatalı '2-1' yönlendirmesi '2>&1' olarak düzeltildi.
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "❌ HATA: Geçerli bir Git reposu değil veya bozuk: $DEST_BASE"
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

echo "⬇️ Pull (Şirket Reposu: origin)..."
git pull --no-rebase --autostash origin "$BRANCH"

echo "⬆️ Push (Şirket Reposu: origin)..."
git push origin "$BRANCH"

# --- KİŞİSEL REPOYA PUSH ETME ---
echo "🔄 Kişisel repo durumu kontrol ediliyor..."
if ! git remote | grep -q "^${PERSONAL_REMOTE_NAME}$"; then
  echo "✨ Kişisel remote '${PERSONAL_REMOTE_NAME}' ekleniyor..."
  git remote add "$PERSONAL_REMOTE_NAME" "$PERSONAL_REMOTE_REPO"
else
  echo "👍 Kişisel remote '${PERSONAL_REMOTE_NAME}' zaten mevcut."
fi

echo "⬆️ Push (Kişisel Repo: ${PERSONAL_REMOTE_NAME})..."
git push "$PERSONAL_REMOTE_NAME" "$BRANCH"

echo "✅ [WORK SYNC] başarıyla tamamlandı (Şirket + Kişisel)"