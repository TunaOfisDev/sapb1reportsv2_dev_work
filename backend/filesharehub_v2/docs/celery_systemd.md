---

## 🧠 Teşhis: Celery’i root kullanıcı olarak çalıştırıyordun ama…

Python venv içindeki `celery` komutu, `sudo` ile başlatıldığında:

```bash
sudo celery -A filesharehub_v2 worker --loglevel=info
```

➡️ **virtualenv ortamını, environment variable’ları (ör: `MEDIA_ROOT`), hatta Django ayarlarını bile eksik alıyor.**
Bu nedenle de:

* `celery` çalışıyor gibi görünüyordu,
* ama aslında `thumbnail_path` oluşturulamıyor ve hiçbir `.jpg` üretilmiyordu,
* Redis'e key gitmiyor, disk’e dosya yazılmıyordu.

---

## ✅ Çözüm: **Her zaman doğru kullanıcı (www-data) + doğru venv ile başlat!**

Senin çalışan komutun tam olarak doğru:

```bash
sudo -u www-data ../venv/bin/celery -A filesharehub_v2 worker --loglevel=info
```

Bu sayede:

* ✅ `venv` içinden çalıştırılıyor (`../venv/bin/celery`)
* ✅ `www-data` yetkileriyle çalışıyor (media'ya yazabiliyor)
* ✅ `.env` ve `settings.py` doğru kaynaklarla yükleniyor
* ✅ `MEDIA_ROOT` dizinine `.jpg` dosyaları yazılıyor
* ✅ Redis cache key’leri oluşuyor

---

## 🛠️ Tavsiye: Sistemi kalıcı ve düzgün hale getir

### 1. 🔁 Systemd servis dosyası oluştur

sudo nano `/etc/systemd/system/filesharehub-celery.service` içine:

```ini
[Unit]
Description=Celery Worker - FileShareHub V2
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/sapb1reportsv2/backend
Environment="DJANGO_SETTINGS_MODULE=sapreports.settings"
ExecStart=/var/www/sapb1reportsv2/venv/bin/celery -A filesharehub_v2 worker --loglevel=ERROR
Restart=always

[Install]
WantedBy=multi-user.target

```

Aktifleştir:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable filesharehub-celery
sudo systemctl start filesharehub-celery
```

> Artık sistem yeniden başlasa bile Celery otomatik çalışır ve hep doğru kullanıcı ile.

---

### 2. 🔍 Gelişmiş izleme (isteğe bağlı)

`supervisor` ile log rotasyonu + email bildirimli crash takibi ekleyebilirsin. Ancak `systemd` senin için şimdilik fazlasıyla yeterli.

---

## 🚀 Özet

| Durum                                 | Açıklama                                       |
| ------------------------------------- | ---------------------------------------------- |
| `test.jpg` ve `test_write.jpg`        | Django shell’den oluşturuldu, yazma sorunu yok |
| Celery thumbnail üretmiyor            | Çünkü root veya eksik ortamla çalışıyordu      |
| `sudo -u www-data ../venv/bin/celery` | 🟢 Doğru yöntem — çalıştı ve thumbs oluştu     |
| Yapılacak                             | `systemd` servisi tanımla, kalıcı hale getir   |

Hazırsan `filesharehub-celery.service`’i birlikte yazalım veya doğrudan uygulayalım.
İzleme/loglama da istersen entegre ederiz.
