#!/bin/bash

# ================================================
# SAPB1 PostgreSQL 17 Health Monitor (TARZ Edition)
# ================================================
# Bu script canlı sistem için disk, bağlantı, WAL ve autovacuum
# gibi temel izleme çıktısını doğrudan terminale yazdırır.
# Log dosyası oluşturmaz, cron için de uygundur.
# ================================================

# 🔹 Renkli terminal çıktısı (isteğe bağlı)
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}===== [1] PostgreSQL Servis Durumu =====${NC}"
systemctl is-active --quiet postgresql@17-main && echo -e "${GREEN}PostgreSQL Aktif${NC}" || echo -e "${YELLOW}PostgreSQL PASİF!${NC}"

echo -e "\n${CYAN}===== [2] Aktif Bağlantılar (${USER}) =====${NC}"
sudo -u postgres psql -Atc "SELECT client_addr, usename, datname, state, backend_start FROM pg_stat_activity WHERE state != 'idle';"

echo -e "\n${CYAN}===== [3] Bağlantı Sayısı / max_connections =====${NC}"
sudo -u postgres psql -Atc "SELECT COUNT(*) || ' / ' || current_setting('max_connections') FROM pg_stat_activity;"

echo -e "\n${CYAN}===== [4] Autovacuum Gecikmiş Tablolar =====${NC}"
sudo -u postgres psql -c "
SELECT relname AS tablo, n_dead_tup AS ölü_satır, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 10;
"

echo -e "\n${CYAN}===== [6] DB Disk Kullanımı (/main) =====${NC}"
sudo du -sh /var/lib/postgresql/17/main

echo -e "\n${CYAN}===== [6] DB Disk Kullanımı (/main) =====${NC}"
du -sh /var/lib/postgresql/17/main

echo -e "\n${CYAN}===== [7] CPU & Bellek Kullanımı (postgres) =====${NC}"
ps -u postgres -o pid,comm,%cpu,%mem --sort=-%cpu | head -n 10

echo -e "\n${CYAN}===== [8] En Son Restart Zamanı =====${NC}"
sudo -u postgres psql -Atc "SELECT pg_postmaster_start_time();"

echo -e "\n${CYAN}===== [9] Aktif Sorguların Süresi > 2sn =====${NC}"
sudo -u postgres psql -c "
SELECT pid, now() - query_start AS süre, state, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '2 seconds'
ORDER BY süre DESC;
"
