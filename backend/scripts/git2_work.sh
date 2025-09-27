#!/bin/bash
set -euo pipefail

# --- DEĞİŞKENLER ---
DEST_BASE="/home/userbt/Github/sapb1reportsv2_dev_work"
GIT_META="/home/userbt/gitmeta/devWork.git"
BRANCH="main"

# Kişisel Repo Bilgileri
PERSONAL_REMOTE_NAME="personal"
PERSONAL_REMOTE_REPO="git@github.com-personal:selimkocak/sapb1reportsv2_dev_work.git"

echo "📍 [KİŞİSEL SYNC] başladı"
echo "📂 Çalışma Dizini: $DEST_BASE"

# Git işlemleri
cd "$DEST_BASE"

# Reponun var olup olmadığını kontrol et
if [[ ! -f ".git" ]] || [[ ! -d "$GIT_META" ]]; then
    echo "❌ HATA: Git reposu bulunamadı. Önce git1_work.sh script'ini çalıştırdığınızdan emin olun."
    exit 1
fi

echo "🔄 Kişisel repo durumu kontrol ediliyor..."
# 'personal' adında bir remote var mı diye kontrol et
if ! git remote | grep -q "^${PERSONAL_REMOTE_NAME}$"; then
  echo "✨ Kişisel remote '${PERSONAL_REMOTE_NAME}' ekleniyor..."
  git remote add "$PERSONAL_REMOTE_NAME" "$PERSONAL_REMOTE_REPO"
else
  echo "👍 Kişisel remote '${PERSONAL_REMOTE_NAME}' zaten mevcut."
fi

# Göndermeden önce şirket reposundaki son değişiklikleri çekerek yerel repoyu güncelle
echo "⬇️ Pull (Şirket Reposu: origin) - En güncel hali almak için..."
git pull origin "$BRANCH"

echo "⬆️ Push (KİŞİSEL Repo: ${PERSONAL_REMOTE_NAME})..."
git push "$PERSONAL_REMOTE_NAME" "$BRANCH"

echo "✅ [KİŞİSEL SYNC] başarıyla tamamlandı"