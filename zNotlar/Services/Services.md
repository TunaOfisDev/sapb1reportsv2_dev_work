## /var/www/sapb1reportsv2/zNotlar/Services/Services.md
Aşağıda **SAP B1 Reports V2** projen için aktif olarak kullanılan tüm sistem servislerini ve bu servislerin **rollerini** detaylı olarak listeledim. Bu liste; hem yazılım altyapısı, hem de sunucu tarafındaki `systemd`/OS bağımlılıklarını kapsar:

---

## 🧩 **Kullanılan Sistem Servisleri ve Altyapılar**

| Servis / Teknoloji             | Görev / Rolü                                                                | Sistem Desteği / Kurulum              |
| ------------------------------ | --------------------------------------------------------------------------- | ------------------------------------- |
| **Redis**                      | Celery queue, cache backend (`CACHES`, `Celery Broker/Backend`, `Channels`) | `systemctl enable redis`              |
| **PostgreSQL**                 | Django ORM ile çalışılan ana veri tabanı                                    | `.env → PGDB_`                        |
| **SAP HANA**                   | SAP’dan veri çekmek için bağlantı (raw query API)                           | `HANADB_HOST`, `HANADB_SCHEMA` vs.    |
| **MSSQL (ODBC + mssql-tools)** | Logo veritabanına erişim (`LOGO_DB_*`)                                      | `ODBC Driver 17 + sqlcmd`             |
| **Samba**                      | Ağdaki `/mnt/gorseller`, `/mnt/product_picture` gibi dizinlerin mount’u     | `fstab`, `systemd mount unit`         |
| **Nginx**                      | Reverse proxy (`/api/`, `/admin`, `/media`, `/backend_static`, `/`)         | `nginx.service`                       |
| **Gunicorn**                   | Django WSGI sunucusu olarak backend servisini çalıştırır                    | `gunicorn.sock` üzerinden Nginx proxy |
| **Daphne**                     | ASGI sunucusu: `Channels` WebSocket altyapısını sağlar                      | `daphne.sock` üzerinden Nginx proxy   |
| **Celery**                     | Zamanlanmış ve async görevlerin çalıştırılması                              | `celery.service`                      |
| **Celery Beat**                | Görevlerin zamanlamasını yöneten zamanlayıcı                                | `celerybeat.service`                  |
| **Supervisor veya systemd**    | Celery worker/beat süreçlerinin kalıcı şekilde servis olarak yönetimi       | `/etc/systemd/system/*.service`       |
| **SMTP (Yandex SMTP)**         | Rapor mail gönderimi (`send_mail`, `mailservice`)                           | `EMAIL_HOST`, `EMAIL_PORT`, TLS/SSL   |

---

## 🛠️ **Kodda Gömülü Yapılar & Bağımlılıklar**

| Modül / Konsept                       | Açıklama                                                                                    |
| ------------------------------------- | ------------------------------------------------------------------------------------------- |
| `.env` + `os.getenv`                  | Tüm yapılandırmalar `.env` üzerinden çekiliyor (şifreler, host, bağlantılar)                |
| `django-celery-beat`                  | `DatabaseScheduler` ile veri tabanına kayıtlı job’ların takvimsel çalıştırılması sağlanıyor |
| `django-redis`                        | Hem `CACHES` hem `CHANNEL_LAYERS` Redis ile yapılandırılmıştır                              |
| `report_orchestrator` + `mailservice` | Rapor motoru + otomatik mail servisi olarak çalışıyor                                       |
| `loguru` + `RotatingFileHandler`      | Her modül için ayrı `.log` dosyasına yazan, limitli, döner log sistemi kurulu               |

---

## 📡 Sistem Entegrasyonları

| Sistem                           | Açıklama                                                                                     |
| -------------------------------- | -------------------------------------------------------------------------------------------- |
| **SAP Business One (HANA)**      | Doğrudan SQL/HTTP istekleriyle veri çekme (örn: `sofitel_supplier_balance_report`)           |
| **Logo ERP (MSSQL)**             | ODBC ile bağlanılan Logo veri kaynakları (maliyet, borç, ödeme, vs.)                         |
| **Network Folder (Samba Mount)** | Ürün görseli, broşür vs. kaynaklarının çekildiği ortak paylaşım alanı                        |
| **Mail Sunucusu (SMTP)**         | HTML gövdeli raporlar, hata bildirimleri, kullanıcı formları bu kanal üzerinden gönderiliyor |

---

## ✅ Sistemde `systemd` ile Çalışanlar

```bash
sudo systemctl status redis
sudo systemctl status celery
sudo systemctl status celerybeat
sudo systemctl status nginx
sudo systemctl status postgresql
```

İsteğe bağlı olarak eklenebilecek (varsa):

```bash
sudo systemctl status daphne
sudo systemctl status samba
```

---

## 🎯 Sonuç

Senin sistemin artık:

* **servis tabanlı çalışıyor**
* **kendi kendini onarabiliyor (retry, log, uyarı)**
* **mail + cache + websocket + queue entegrasyonlu**
* **prod ortamda sürdürülebilir ve ölçeklenebilir**

Ve en önemlisi: **senin tam kontrolünde.**

İstersen bu tabloyu `.md` ya da `.xlsx` formatında dışarı da verebilirim. Hazırsan CI/CD tarafına da geçebiliriz.
