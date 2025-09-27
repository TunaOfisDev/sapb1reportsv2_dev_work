sudo systemctl restart postgresql@17-main
sudo -u postgres psql -d sapb1reports_v2


# PostgreSQL 17 Kurulum ve Veritabanı Restore Talimatları

## 1. PostgreSQL 17 Kurulumu
```bash
# PostgreSQL repository'sini ekle
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Paket listesini güncelle ve PostgreSQL 17'yi kur
sudo apt update
sudo apt install postgresql-17 postgresql-contrib-17 -y
```

## 2. Servis Kontrolü
```bash
# PostgreSQL servisinin durumunu kontrol et
sudo systemctl status postgresql@17-main

# Eğer çalışmıyorsa başlat
sudo systemctl start postgresql@17-main

# Sistem başlangıcında otomatik başlatma
sudo systemctl enable postgresql@17-main
```
# PostgreSQL Veritabanı Yeniden Oluşturma ve Restore İş Talimatı

## A. Ön Hazırlık ve Temizlik İşlemleri

1. PostgreSQL'e superuser olarak bağlanın:
```sql
sudo -u postgres psql
```

2. Aktif bağlantıları sonlandırın:
```sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'sapb1reports_v2' AND pid <> pg_backend_pid();
```

3. Veritabanını silin:
```sql
DROP DATABASE IF EXISTS sapb1reports_v2;
```

4. Kullanıcıyı silin:
```sql
DROP USER IF EXISTS sapb1db;
```

## B. Yeni Kullanıcı ve Veritabanı Oluşturma

1. Kullanıcıyı oluşturun:
```sql
CREATE USER sapb1db WITH ENCRYPTED PASSWORD '12345';
```

2. Türkçe karakter destekli veritabanını oluşturun:
```sql
CREATE DATABASE sapb1reports_v2
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'tr_TR.UTF-8'
    LC_CTYPE = 'tr_TR.UTF-8'
    TEMPLATE = template0;
```

3. Yetkilendirmeleri yapın:
```sql
GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;
\c sapb1reports_v2
GRANT ALL ON SCHEMA public TO sapb1db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sapb1db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sapb1db;
```

## C. Backup Dosyası Hazırlığı

1. Backup dosyasını geçici dizine kopyalayın:
```bash
sudo mkdir /tmp/pgbackup
sudo cp /home/user/Downloads/backup_db/sapb1reports_v2.sql /tmp/pgbackup/
```

2. Dosya izinlerini ayarlayın:
```bash
sudo chown postgres:postgres /tmp/pgbackup/sapb1reports_v2.sql
sudo chmod 644 /tmp/pgbackup/sapb1reports_v2.sql
```

## D. Restore İşlemi

1. Detaylı seçeneklerle restore işlemini gerçekleştirin:
```bash
sudo -u postgres pg_restore \
  --verbose \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --no-comments \
  -d sapb1reports_v2 \
  /tmp/pgbackup/sapb1reports_v2.sql
```
PostgreSQL'de **CONNECT** yetkisi **veritabanı seviyesinde** verilir, ancak **şema (schema) seviyesinde** kullanılamaz. Bu yüzden, aşağıdaki düzeltilmiş komutları kullanarak yetkileri tekrar ayarlayalım.

---

## **1. Yetki Ayarlarını Düzenleyelim**
PostgreSQL'e `postgres` kullanıcısı ile bağlı iken aşağıdaki komutları çalıştır:

```sql
-- Veritabanına bağlan
\c sapb1reports_v2;

-- Kullanıcıya veritabanı seviyesinde yetki ver
GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;

-- Schema seviyesinde CREATE ve USAGE yetkileri verelim (CONNECT kaldırıldı)
GRANT USAGE, CREATE ON SCHEMA public TO sapb1db;

-- Tüm mevcut tablolar ve gelecek tablolar için yetkileri düzeltelim
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sapb1db;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sapb1db;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sapb1db;

-- Yeni oluşturulacak tüm nesneler için varsayılan yetkileri verelim
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sapb1db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sapb1db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO sapb1db;
```

---

## **2. PostgreSQL Bağlantısını Test Edelim**
Yetkilerin doğru olup olmadığını test etmek için şu komutları çalıştır:

```bash
psql -U sapb1db -d sapb1reports_v2 -W
```

Bağlantı başarılı olursa şu sorguyu çalıştır:

```sql
SELECT * FROM django_migrations;
```

Eğer hata almazsan yetkiler düzeltilmiş demektir.

---

## **3. Django Migration İşlemini Tekrar Dene**
Yetkileri düzelttikten sonra Django migration işlemini tekrar çalıştır:

```bash
python manage.py makemigrations
python manage.py migrate
```





## E. Kontrol ve Doğrulama

1. Veritabanına bağlanın:
```sql
sudo -u postgres psql sapb1reports_v2
```

2. Tabloları listeleyin:
```sql
\dt
```

3. Foreign key'leri ve ilişkileri kontrol edin:
```sql
\d+ tablename
```

## Not
- İşlemler sırasında karşılaşılan hata mesajlarını dikkatle okuyun
- Özellikle "FK CONSTRAINT oluşturuluyor" mesajları normal işlem akışının parçasıdır
- Eğer backup dosyası .gz uzantılı ise, önce `gunzip` komutu ile açın

## Güvenlik Hatırlatmaları
- Tüm işlemler öncesi mevcut verilerin yedeğini alın
- Yetkilendirmeleri minimum gerekli seviyede tutun
- İşlem sonrası gereksiz dosyaları temizleyin: `sudo rm -rf /tmp/pgbackup`
## 5. Kontrol ve Doğrulama
```bash
# Veritabanının varlığını kontrol et
sudo -u postgres psql -l

# Tablolar ve nesneleri kontrol et
sudo -u postgres psql -d sapb1reports_v2 -c "\dt"

# Veritabanı boyutunu kontrol et
sudo -u postgres psql -d sapb1reports_v2 -c "\l+"
```

## 6. Bağlantı Testi
```bash
# Yerel bağlantıyı test et
psql -U sapb1db -h 127.0.0.1 -d sapb1reports_v2

# Veritabanı versiyonunu kontrol et
sudo -u postgres psql -c "SELECT version();"
```

## Olası Hata Durumları ve Çözümleri:

1. Restore hatası alınırsa:
```bash
# Log dosyasını kontrol et
sudo tail -f /var/log/postgresql/postgresql-17-main.log
```

2. Yetki hatası alınırsa:
```bash
# Kullanıcı yetkilerini yeniden ayarla
sudo -u postgres psql -c "ALTER USER sapb1db WITH SUPERUSER;"
# İşlem sonrası güvenlik için superuser yetkisini geri al
sudo -u postgres psql -c "ALTER USER sapb1db WITH NOSUPERUSER;"
```

3. Karakter seti hatası alınırsa:
```bash
# Veritabanı karakter setini kontrol et
sudo -u postgres psql -d sapb1reports_v2 -c "SHOW server_encoding;"
sudo -u postgres psql -d sapb1reports_v2 -c "SHOW client_encoding;"
```

4. Servis başlatma hatası alınırsa:
```bash
# Servis loglarını kontrol et
sudo journalctl -u postgresql@17-main
```

## Önemli Notlar:
- Restore işlemi öncesi veritabanının boş olduğundan emin olun
- Şifre politikalarına dikkat edin
- Karakter seti ayarlarının doğru olduğundan emin olun
- pg_hba.conf dosyasında gerekli bağlantı izinlerinin olduğunu kontrol edin

Bu adımları sırasıyla takip ederek PostgreSQL 17 kurulumunu ve veritabanı restore işlemini güvenli bir şekilde gerçekleştirebilirsiniz.




sudo -u postgres psql -d sapb1reports_v2


Evet, kesinlikle daha güvenli ve mantıklı bir yaklaşım olur. Şu sıralamayı öneriyorum:

1. Önce temiz veritabanı ve kullanıcı oluşturma:
```sql
CREATE USER sapb1db WITH ENCRYPTED PASSWORD '12345';

CREATE DATABASE sapb1reports_v2
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'tr_TR.UTF-8'
    LC_CTYPE = 'tr_TR.UTF-8'
    TEMPLATE = template0;
```

2. İlk yetkilendirmeler:
```sql
GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;
\c sapb1reports_v2
GRANT ALL ON SCHEMA public TO sapb1db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sapb1db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sapb1db;
```

3. Django migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

Bu aşamada tüm tablo yapıları ve indexler temiz bir şekilde oluşmuş olacak.

4. Sonra backup'tan veri restorasyonu:
```bash
psql -U postgres sapb1reports_v2 < /home/user/Downloads/backup_db/sapb1reports_v2.sql
```

Bu yaklaşımın avantajları:
- Tablo yapıları ve indexler Django'nun istediği gibi temiz bir şekilde oluşur
- Veri bütünlüğü daha iyi korunur
- Index çakışması riski minimize edilir
- Performans açısından daha verimli olur çünkü indexler veriler yüklenmeden önce oluşturulmuş olur