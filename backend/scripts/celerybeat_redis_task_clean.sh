#!/usr/bin/env bash
set -euo pipefail

# 📁 Ortam yolları
ENV_PATH="/var/www/sapb1reportsv2/backend/.env"
VENV_PATH="/var/www/sapb1reportsv2/venv"
CELERY_BIN="$VENV_PATH/bin/celery"
PROJECT_ROOT="/var/www/sapb1reportsv2/backend"
WORKER_NODE="worker1@sapb1-pro-srv"  # ← systemd celery.service içindeki -n değeriyle birebir aynı olmalı

# 🟡 Renkli log fonksiyonları
log()  { echo -e "\e[1;32m[✓]\e[0m $*"; }
warn() { echo -e "\e[0;33m[!]\e[0m $*"; }
die()  { echo -e "\e[0;31m[✗]\e[0m $*" >&2; exit 1; }

# 🔌 Redis CLI wrapper
RCLI() {
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" "$@"
}

# ⚙️ .env doğrulama
[[ -f "$ENV_PATH" ]] || die ".env dosyası bulunamadı: $ENV_PATH"
source <(grep -E '^(REDIS_HOST|REDIS_PORT|REDIS_PASS)=' "$ENV_PATH")

# 🧪 Sanal ortam ve PYTHONPATH ayarı
log "Python venv ortamı aktive ediliyor"
source "$VENV_PATH/bin/activate"
export PYTHONPATH="$PROJECT_ROOT"

# 🛑 Worker zarifçe durduruluyor
log "Celery worker node ($WORKER_NODE) zarifçe kapatılıyor"
if ! "$CELERY_BIN" -A sapreports control shutdown --timeout=60 -d "$WORKER_NODE"; then
    warn "Graceful shutdown başarısız, systemctl stop uygulanıyor"
    sudo systemctl stop celery || die "Celery servis durdurulamadı"
else
    log "Celery worker başarılı şekilde durduruldu"
fi

# ⏹️ Beat servisi durduruluyor
sudo systemctl stop celerybeat || die "Celery Beat durdurulamadı"

# 🔌 Redis bağlantısı kontrol ediliyor
log "Redis bağlantısı test ediliyor..."
RCLI ping | grep -q PONG || die "Redis bağlantısı başarısız"

# 📦 Kuyruk kontrolü
QUEUE_LEN=$(RCLI llen celery)
log "Aktif görev sayısı: $QUEUE_LEN"
[[ "$QUEUE_LEN" -eq 0 ]] && die "Kuyruk zaten boş; temizliğe gerek yok"

# ❓ Onay
read -r -p "Kuyruğu gerçekten boşaltmak istiyor musun? [y/N] " yn
[[ "$yn" =~ ^[Yy]$ ]] || die "İşlem kullanıcı tarafından iptal edildi"

# 🧹 Kuyruk temizleniyor
log "'celery' kuyruğu purge ediliyor"
"$CELERY_BIN" -A sapreports purge --force -Q celery || die "Purge işlemi başarısız"

# 🔁 Servisler başlatılıyor
log "Celery servisleri yeniden başlatılıyor"
sudo systemctl start celery || die "Celery başlatılamadı"
sudo systemctl start celerybeat || die "Celery Beat başlatılamadı"

log "Celery queue temizliği başarıyla tamamlandı ✅"
