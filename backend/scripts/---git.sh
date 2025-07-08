#!/bin/bash
# ==========================================
# SAP B1 Reports V2 – LIVE Git Sync  (Chunk-Safe, Clean Commit)
# ==========================================
set -euo pipefail

SRC_BASE="/var/www/sapb1reportsv2"
DEST_BASE="/home/user/Github/sapb1reportsv2_work_live"
GIT_META="/home/user/gitmeta/workLive.git"
EXCLUDES="$SRC_BASE/backend/scripts/rsync-exclude.txt"
REMOTE_REPO="git@github.com:TunaOfisDev/sapb1reportsv2_work_live.git"
BRANCH="main"

echo "📍  [LIVE SYNC] başladı"
echo "📂  DEST       : $DEST_BASE"
echo "🗃️  GIT META   : $GIT_META"

# ── 1) Repo köprüsü ───────────────────────────────────────────
if [[ ! -d $GIT_META ]]; then
  git clone --separate-git-dir="$GIT_META" "$REMOTE_REPO" "$DEST_BASE"
else
  echo "gitdir: $GIT_META" > "$DEST_BASE/.git"
fi
cd "$DEST_BASE"

# ── 2) Gereksiz klasörleri sil ────────────────────────────────
find . -maxdepth 1 -type d \
     \( -iname 'Backend' -o -iname 'Frontend' -o -iname 'Services' \
        -o -iname 'Database' -o -iname 'Ubuntu' -o -iname 'RaporNotlari' \) \
     ! -iname 'backend' ! -iname 'frontend' ! -iname 'zNotlar' \
     -exec rm -rf {} +

# ── 3) Rsync (backend · frontend · zNotlar) ───────────────────
for d in backend frontend zNotlar; do
  rsync -av --delete --exclude-from="$EXCLUDES" \
        "$SRC_BASE/$d/" "$DEST_BASE/$d/"
done

# ── 4) Değişiklikleri parça parça sahnele  ────────────────────
echo "➕  Git stage (chunk)…"

#   a) Silinen dosyalar
git ls-files -d -z | xargs -0 -r -n 200 git rm --cached --

#   b) Yeni ve değişen dosyalar
git ls-files -m -o --exclude-standard -z | xargs -0 -r -n 200 git add --

# ── 5) Commit oluştur ─────────────────────────────────────────
if ! git diff --cached --quiet; then
  SNAP="📦 live snapshot - $(date '+%Y-%m-%d %H:%M')"
  BODY="İçerik:"
  while IFS= read -r -d '' f; do
    BODY+=$'\n• '"$f"
  done < <(git diff --cached --name-only -z)

  git commit -m "$SNAP" -m "$BODY"
else
  echo "⚠️  Commit yapılacak değişiklik yok"
fi

# ── 6) Pull & Push ────────────────────────────────────────────
git pull --no-edit origin "$BRANCH" || echo "⚠️  Pull çakışması — elle çöz"
git push origin "$BRANCH"           || echo "❌  Push başarısız"

echo "🏁  [LIVE SYNC] tamamlandı"
