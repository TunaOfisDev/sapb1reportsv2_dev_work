1- user@reportserver:~$ cat /etc/postgresql/17/main/postgresql.conf
# =============================================================================
# TEMEL SISTEM AYARLARI - DEĞİŞTİRMEYİN
# =============================================================================
data_directory = '/var/lib/postgresql/17/main'
hba_file = '/etc/postgresql/17/main/pg_hba.conf'
ident_file = '/etc/postgresql/17/main/pg_ident.conf'
external_pid_file = '/var/run/postgresql/17-main.pid'
unix_socket_directories = '/var/run/postgresql'
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
dynamic_shared_memory_type = posix
cluster_name = '17/main'

# =============================================================================
# BAĞLANTI AYARLARI
# =============================================================================
listen_addresses = '*'
port = 5432
max_connections = 200
superuser_reserved_connections = 5

# =============================================================================
# BELLEK AYARLARI (18GB RAM için optimize)
# =============================================================================
shared_buffers = 6GB                    # RAM'in ~%33'ü
effective_cache_size = 14GB             # RAM'in ~%77'si
maintenance_work_mem = 1GB              # Bakım işlemleri için
work_mem = 64MB                         # Sorgu başına ayrılan bellek
temp_buffers = 64MB                     # Geçici tablolar için
temp_file_limit = 10GB                  # Geçici dosya limiti

# =============================================================================
# DISK ve I/O AYARLARI (SSD için optimize)
# =============================================================================
random_page_cost = 1.1                   # SSD için optimize
effective_io_concurrency = 200           # SSD için optimize
checkpoint_timeout = 10min
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 2GB
wal_buffers = 32MB

# =============================================================================
# WAL VE TRANSACTION AYARLARI
# =============================================================================
synchronous_commit = on                   # Veri güvenliği için
wal_level = replica                        # Replikasyon desteği için
wal_writer_delay = 10ms
commit_delay = 5000
commit_siblings = 5

# =============================================================================
# AUTOVACUUM AYARLARI
# =============================================================================
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 10s
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.02
vacuum_cost_delay = 10ms                  # SSD için optimize
vacuum_cost_limit = 1000                   # SSD için optimize

# =============================================================================
# PARALLEL SORGU AYARLARI (6 çekirdek için optimize edildi)
# =============================================================================
max_worker_processes = 6
max_parallel_workers = 6
max_parallel_workers_per_gather = 3
max_parallel_maintenance_workers = 2
parallel_tuple_cost = 0.1
parallel_setup_cost = 1000

# =============================================================================
# GÜNLÜKLEME AYARLARI
# =============================================================================
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 500         # 500ms'den uzun sorguları logla
log_checkpoints = on
log_connections = on
log_disconnections = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_lock_waits = on
log_statement = 'none'

# =============================================================================
# LOCALE VE KARAKTER SETİ AYARLARI
# =============================================================================
datestyle = 'iso, dmy'
timezone = 'Europe/Istanbul'
log_timezone = 'Europe/Istanbul'
lc_messages = 'tr_TR.UTF-8'
lc_monetary = 'tr_TR.UTF-8'
lc_numeric = 'tr_TR.UTF-8'
lc_time = 'tr_TR.UTF-8'
default_text_search_config = 'pg_catalog.turkish'

# =============================================================================
# DİĞER AYARLAR
# =============================================================================
include_dir = 'conf.d'



######

2- user@reportserver:~$ sudo cat /etc/postgresql/17/main/pg_hba.conf
# ==============================================================================
# PostgreSQL İstemci Kimlik Doğrulama Yapılandırması 
# ==============================================================================

# ------------------------------------------------------------------------------
# YEREL BAĞLANTILAR (Unix Domain Sockets)
# ------------------------------------------------------------------------------
local   all             postgres                                peer
local   all             all                                     scram-sha-256

# ------------------------------------------------------------------------------
# IPv4 BAĞLANTILARI
# ------------------------------------------------------------------------------
host    all             all             127.0.0.1/32            scram-sha-256
host    sapb1reports_v2 sapb1db         127.0.0.1/32            scram-sha-256
host    all             all             10.130.212.112/32       scram-sha-256
host    all             all             192.168.2.0/24          scram-sha-256
host    all             all             0.0.0.0/0               reject  # Yetkisiz dış erişimi engelle

# ------------------------------------------------------------------------------
# IPv6 BAĞLANTILARI
# ------------------------------------------------------------------------------
host    all             all             ::1/128                 scram-sha-256

# ------------------------------------------------------------------------------
# REPLİKASYON BAĞLANTILARI
# ------------------------------------------------------------------------------
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            scram-sha-256
host    replication     all             10.130.212.112/32       scram-sha-256
host    replication     replicator      10.130.212.112/32       scram-sha-256

# ------------------------------------------------------------------------------
# UYGULAMA ÖZEL BAĞLANTILAR
# ------------------------------------------------------------------------------
# SAP B1 Reports bağlantısı özel yapılandırması korundu



####
sudo systemctl restart postgresql@17-main
sudo systemctl status postgresql@17-main