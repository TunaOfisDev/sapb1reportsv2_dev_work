# 🐘 PostgreSQL Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** projesinde kullanılan PostgreSQL servisinin yapılandırmasını, bağlantı testlerini ve log denetimlerini içerir.

---

## 🧾 Servis Bilgisi

```bash
sudo systemctl cat postgresql
```

Birincil unit dosyası:
```bash
/usr/lib/systemd/system/postgresql.service
```

---

## ⚙️ Konfigürasyon Dosyaları

- postgresql.conf: `/etc/postgresql/17/main/postgresql.conf`
- pg_hba.conf: `/etc/postgresql/17/main/pg_hba.conf`

```ini
listen_addresses = '*'
port = 5432				# (change requires restart)
```

---

## 🔐 pg_hba.conf Kuralları

```ini
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            scram-sha-256
host    replication     all             ::1/128                 scram-sha-256
host    all             all             192.168.1.0/24           md5
```

---

## 🔁 Django Uyumlu Ayarlar

.env dosyasındaki veritabanı bilgileri:
```env
PGDB_NAME=sapb1reports_v2
PGDB_USER=sapb1db
PGDB_PASSWORD=*****
PGDB_HOST=localhost
PGDB_PORT=5432
```

settings.py içeriğinde:
```python
'OPTIONS': {
    'options': '-c client_encoding=UTF8'
}
```

---

## 🧪 Bağlantı Testi

```bash
PGPASSWORD="12345" psql -h "localhost" -p "5432" -U "sapb1db" -d "sapb1reports_v2" -c 'SELECT version();'
```

Sonuç:
```bash
                                                              version                                                              
-----------------------------------------------------------------------------------------------------------------------------------
 PostgreSQL 17.5 (Ubuntu 17.5-1.pgdg24.04+1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0, 64-bit
(1 row)
```

---

## 📦 Servis Yönetimi

```bash
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
sudo systemctl status postgresql
sudo systemctl enable postgresql
```

---

## 📝 Log Takibi

```bash
journalctl -u postgresql -f
journalctl -u postgresql --since today
```

---

## 🛡️ Yedekleme ve Yapılandırma Yenileme

```bash
sudo cp "/etc/postgresql/17/main/postgresql.conf" "/etc/postgresql/17/main/postgresql.conf.bak"
sudo cp "/etc/postgresql/17/main/pg_hba.conf" "/etc/postgresql/17/main/pg_hba.conf.bak"
```

Veritabanına bağlı kalmadan reload:
```sql
SELECT pg_reload_conf();
```

---

