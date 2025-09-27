# 🧠 Redis Servis Yapılandırma Klavuzu

Bu belge, **SAPB1ReportsV2** sunucusundaki Redis servisinin yapılandırma dosyalarını, şifreleme durumunu, port erişimini ve servis denetimini içerir.

---

## 🧾 Redis Servisi (systemd)

Servis dosyasını görmek için:
```bash
sudo systemctl cat redis
```

---

## 🔧 redis.conf Detayları

Dosya yolu:
```bash
/etc/redis/redis.conf
```

Temel ayarlar:
```ini
bind 127.0.0.1
port 6379
requirepass Tuna2023*
```

---

## 🔐 .env Üzerinden REDIS_PASS

```env
REDIS_PASS="Tuna2023*"
```

---

## 🔌 Port Dinleme Durumu

```bash
LISTEN 0      511        127.0.0.1:6379       0.0.0.0:*    users:(("redis-server",pid=894,fd=6))                                                                                                                                          
```

---

## 🧪 redis-cli Ping Testi

```bash
redis-cli -a ******** ping
```

Sonuç:
```bash
PONG
```

---

## 📦 Servis Yönetimi

```bash
sudo systemctl start redis
sudo systemctl stop redis
sudo systemctl restart redis
sudo systemctl status redis
sudo systemctl enable redis
```

---

## 📄 Log Takibi

```bash
journalctl -u redis -f
journalctl -u redis --since today
```

---

## 🧠 Ek Notlar

- Redis varsayılan olarak sadece `127.0.0.1` üzerinden dinler.
- Parola doğrulama açıksa `.env` içindeki `REDIS_PASS` kullanılır.
- Uzak bağlantılar için `bind 0.0.0.0` risklidir, dikkatli kullanılmalıdır.
- Bazı sistemlerde servis adı `redis-server` olabilir.

