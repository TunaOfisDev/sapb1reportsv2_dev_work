#!/bin/bash
# ==========================================
# SAP B1 Reports V2 – WORK Git Sync (Chunk-Safe, Clean Commit)
# ==========================================
set -euo pipefail

# --- Configuration ---
SRC_BASE="/var/www/sapb1reportsv2"
DEST_BASE="/home/user/Github/sapb1reportsv2_dev_work"
GIT_META="/home/user/gitmeta/devWork.git"
EXCLUDES="$SRC_BASE/backend/scripts/rsync-exclude.txt"
REMOTE_REPO="git@github.com:TunaGitDev/sapb1reportsv2_dev_work.git"
BRANCH="main"
CHUNK_SIZE=1000  # Dosya gruplama boyutu

echo "📍 [WORK SYNC] başladı"
echo "📂 SRC        : $SRC_BASE"
echo "📂 DEST       : $DEST_BASE"
echo "🗃️ GIT META   : $GIT_META"

# --- 1: Initialize Git repository ---
if [[ ! -d "$GIT_META" ]]; then
  echo "🧱 [INIT] Git meta ilk kez kuruluyor..."
  git clone --separate-git-dir="$GIT_META" "$REMOTE_REPO" "$DEST_BASE"
else
  echo "🔗 [LINK] Mevcut gitdir bağlanıyor..."
  if [[ -d "$DEST_BASE/.git" ]]; then
    echo "🧹 [CLEAN] Önceki .git klasörü temizleniyor..."
    rm -rf "$DEST_BASE/.git"
  fi
  echo "gitdir: $GIT_META" > "$DEST_BASE/.git"
fi

# --- 2: Rsync files ---
for dir in backend frontend zNotlar .vscode; do
  echo "📁 Kopyalanıyor: $dir"
  rsync -av --delete --exclude-from="$EXCLUDES" "$SRC_BASE/$dir/" "$DEST_BASE/$dir/"
done

# --- 3: Change to destination directory ---
cd "$DEST_BASE" || { echo "❌ Dizin değiştirilemedi: $DEST_BASE"; exit 1; }

# --- 4: Git stage (chunk-safe) ---
echo "➕ Git stage (chunk) başlatılıyor…"

# a) Process deleted files in chunks
DELETED_FILES=$(git ls-files -d -z | wc -c)
if [[ "$DELETED_FILES" -gt 0 ]]; then
  echo "🗑️ Silinmiş dosya sayısı: $(git ls-files -d -z | tr -dc '\0' | wc -c)"
  git ls-files -d -z | xargs -0 -n "$CHUNK_SIZE" git rm --cached -- 2>/dev/null || {
    echo "⚠️ Silinmiş dosyaları işlerken hata oluştu, devam ediliyor..."
  }
else
  echo "ℹ️ Silinmiş dosya bulunamadı, git rm atlanıyor."
fi

# b) Process new and modified files in chunks
MODIFIED_FILES=$(git ls-files -m -o --exclude-standard -z | wc -c)
if [[ "$MODIFIED_FILES" -gt 0 ]]; then
  echo "📝 Yeni/değişmiş dosya sayısı: $(git ls-files -m -o --exclude-standard -z | tr -dc '\0' | wc -c)"
  git ls-files -m -o --exclude-standard -z | xargs -0 -n "$CHUNK_SIZE" git add --
else
  echo "ℹ️ Yeni veya değişmiş dosya bulunamadı, git add atlanıyor."
fi

# --- 5: Create commit if changes exist ---
if ! git diff --cached --quiet; then
  SNAP="🧪 dev work snapshot - $(date '+%Y-%m-%d %H:%M')"
  BODY="İçerik:"
  while IFS= read -r -d '' file; do
    BODY+=$'\n• '"$file"
  done < <(git diff --cached --name-only -z)

  git commit -m "$SNAP" -m "$BODY"
  echo "✅ Commit oluşturuldu: $SNAP"
else
  echo "⚠️ Commit yapılacak değişiklik yok"
fi

# --- 6: Pull & Push ---
if ! git pull --no-edit origin "$BRANCH"; then
  echo "⚠️ Pull çakışması — elle çözülmeli"
fi
if ! git push origin "$BRANCH"; then
  echo "❌ Push başarısız — logları kontrol et"
else
  echo "✅ Push tamamlandı"
fi

echo "🏁 [WORK SYNC] tamamlandı"