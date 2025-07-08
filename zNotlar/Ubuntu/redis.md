
Redis şifre korumalı olduğu için önce kimlik doğrulama yapmanız gerekiyor. İşte Redis'i test etmek için doğru yöntem:

```bash
redis-cli -a Tuna2023* ping
```

İlk komut tek satırda hem kimlik doğrulama hem de ping gönderirken, ikinci yöntemde önce Redis CLI'a bağlanıp sonra kimlik doğrulama yapıyorsunuz.

TUNA2023* şifreniz olduğu görülüyor (system_health_check.sh scriptinizden bunu görebiliyorum). Eğer bu şifre doğruysa, "PONG" yanıtını almanız gerekir.

Ayrıca Redis status'unu doğrudan systemctl ile de kontrol edebilirsiniz:

```bash
sudo systemctl status redis-server
```

Bu komut, Redis servisinin çalışıp çalışmadığını ve herhangi bir hata olup olmadığını gösterecektir.


sudo nano /etc/redis/redis.conf
sudo cat /etc/redis/redis.conf

user@reportserver:~$ sudo cat /etc/redis/redis.conf

bind 127.0.0.1 -::1
protected-mode yes
port 6379
requirepass Tuna2023*
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised auto
pidfile /run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
always-show-logo no
set-proc-title yes
proc-title-template "{title} {listen-addr} {server-mode}"
locale-collate ""
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
rdb-del-sync-files no
dir /var/lib/redis
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync yes
repl-diskless-sync-delay 5
repl-diskless-sync-max-replicas 0
repl-diskless-load disabled
repl-disable-tcp-nodelay no
replica-priority 100
acllog-max-len 128
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
lazyfree-lazy-user-del no
lazyfree-lazy-user-flush no
oom-score-adj no
oom-score-adj-values 0 200 800
disable-thp yes
appendonly no
appendfilename "appendonly.aof"
appenddirname "appendonlydir"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
aof-timestamp-enabled no
 
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-listpack-entries 512
hash-max-listpack-value 64
list-max-listpack-size -2
list-compress-depth 0
set-max-intset-entries 512
set-max-listpack-entries 128
set-max-listpack-value 64
zset-max-listpack-entries 128
zset-max-listpack-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
jemalloc-bg-thread yes


















Ubuntu 22.04.3 LTS üzerinde Redis yüklemek için aşağıdaki adımları takip edebilirsin:

1. **Terminali Aç:** `Ctrl + Alt + T` tuş kombinasyonuyla veya uygulama menüsünden terminali aç.

2. **Redis Paketlerini Güncelle:** Paket listelerini güncellemek için aşağıdaki komutu çalıştır:

   ```sh
   sudo apt update
   ```

3. **Redis'i Yükle:** Redis'i yüklemek için aşağıdaki komutu kullan:

   ```sh
   sudo apt install redis-server
   ```

4. **Redis Sunucusunu Yapılandırma:**
   Redis varsayılan olarak non-persistent modda çalışır. Eğer verilerin disk üzerinde kalıcı olmasını istiyorsan, Redis yapılandırma dosyasını düzenlemen gerekir:

   ```sh
   sudo nano /etc/redis/redis.conf
   ```

   Açılan editörde, `supervised` yönergesini bul ve `no` yerine `systemd` ile değiştir. Bu, Redis'in systemd ile uyumlu bir şekilde çalışmasını sağlar:

   ```conf
   supervised systemd
   ```

   Değişiklikleri yaptıktan sonra `Ctrl + X` tuşlayarak çık ve değişiklikleri kaydetmeyi onayla.

5. **Redis Sunucusunu Başlatma ve Durumu Kontrol Etme:**
   Yapılandırmayı değiştirdikten sonra Redis sunucusunu başlat veya yeniden başlat:

   ```sh
   sudo systemctl restart redis.service
   ```

   Redis sunucusunun durumunu kontrol etmek için:

   ```sh
   sudo systemctl status redis
   ```

6. **Redis Testi:**
   Redis'in düzgün çalıştığını test etmek için:

   ```sh
   redis-cli ping
   ```

   Eğer Redis çalışıyorsa, bu komut `PONG` yanıtını döndürecektir.

7. **Redis'i Otomatik Başlatma:**
   Redis'in sistemi her başlattığında otomatik olarak çalışmasını sağlamak için:


  systemctl list-units --type=service | grep redis
  sudo systemctl enable redis-server
  sudo systemctl start redis-server
  sudo systemctl status redis-server


Bu adımları takip ederek, Redis'i Ubuntu 22.04.3 LTS sistemine başarıyla yüklemiş olursun. Redis, birçok modern web uygulamasının performansını ve ölçeklenebilirliğini artırmak için kritik bir araçtır. Redis'i Django ile kullanmak, özellikle büyük miktarda okuma işlemini hızlandırmak ve veri alışverişini iyileştirmek için etkili bir yol sağlar.

# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Cache time to live is 15 minutes.
CACHE_TTL = 60 * 15
