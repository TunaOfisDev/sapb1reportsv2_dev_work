Eski veritabanını tamamen silip, yedeği yeniden temiz bir şekilde yüklemek için aşağıdaki adımları takip edebilirsiniz.

sudo -u www-data /var/www/sapb1reportsv2/venv/bin/python manage.py makemigrations
sudo -u www-data /var/www/sapb1reportsv2/venv/bin/python manage.py migrate

### 1. **PostgreSQL'de Oturumları Sonlandırma**
Öncelikle, eski veritabanını kullanan tüm oturumları sonlandırmanız gerekir.

```sql
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'sapb1reports_v2'
  AND pid <> pg_backend_pid();
```

---

### 2. **Veritabanını Silme**
Aşağıdaki komutla veritabanını silin:

```sql
DROP DATABASE sapb1reports_v2;
```

Eğer hata alırsanız, oturumların tamamen kapatıldığından emin olun ve tekrar deneyin.

---

### 3. **Yeni Veritabanı Oluşturma**
Yeni veritabanını Türkçe dil desteğiyle oluşturun:

```sql turkce karakter destekli db semasi olusturmak
CREATE DATABASE sapb1reports_v2
WITH 
    OWNER = sapb1db
    ENCODING = 'UTF8'
    LC_COLLATE = 'tr_TR.UTF-8'
    LC_CTYPE = 'tr_TR.UTF-8'
    TEMPLATE = template0;
```

---

### 4. **Yedeği Geri Yükleme**
Terminalden aşağıdaki komutu çalıştırarak yedeği geri yükleyin:

```bash
PGPASSWORD='12345' pg_restore -U sapb1db -d sapb1reports_v2 -v /home/user/Downloads/backup_db/sapb1reports_v2.backup
```

---

### 5. **Erişim Yetkilerini Verme**
Eğer gerekliyse, tüm yetkileri tekrar verin:

```sql
GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;
```

---

### 6. **Kontroller**
Geri yükleme sırasında herhangi bir hata mesajı alırsanız, sorunu detaylandıran logları kontrol edin. Geri yüklemenin başarılı olduğunu doğrulamak için tablo içeriklerini kontrol edin:

```sql
\c sapb1reports_v2
\dt
SELECT COUNT(*) FROM <table_name>;
```

---

Bu işlem, eski veritabanını tamamen temizleyip yedeği sıfırdan yüklemek için yeterlidir. Eğer daha fazla sorunla karşılaşırsanız, log detaylarını paylaşarak daha fazla destek alabilirsiniz. 




Step 1 — Installing PostgreSQL
To install PostgreSQL, first refresh your server’s local package index:

sudo apt update

Then, install the Postgres package along with a -contrib package that adds some additional utilities and functionality:

sudo apt install postgresql postgresql-contrib

Press Y when prompted to confirm installation. If you are prompted to restart any services, press ENTER to accept the defaults and continue.

Step 2 — Using PostgreSQL Roles and Databases
By default, Postgres uses a concept called “roles” to handle authentication and authorization. These are, in some ways, similar to regular Unix-style users and groups.

Upon installation, Postgres is set up to use ident authentication, meaning that it associates Postgres roles with a matching Unix/Linux system account. If a role exists within Postgres, a Unix/Linux username with the same name is able to sign in as that role.

The installation procedure created a user account called postgres that is associated with the default Postgres role. There are a few ways to utilize this account to access Postgres. One way is to switch over to the postgres account on your server by running the following command:

sudo -i -u postgres
Then you can access the Postgres prompt by running:

psql
This will log you into the PostgreSQL prompt, and from here you are free to interact with the database management system right away.

To exit out of the PostgreSQL prompt, run the following:

\q
This will bring you back to the postgres Linux command prompt. To return to your regular system user, run the exit command:

exit

### PostgreSQL Veritabanı ve Kullanıcı Oluşturma

Öncelikle, PostgreSQL veritabanında yeni bir veritabanı ve kullanıcı oluşturmanız gerekiyor. Terminalde PostgreSQL komut satırı aracına (`psql`) erişmek için aşağıdaki komutu kullanabilirsiniz:

```bash
sudo -u postgres psql
```

Sonrasında, yeni bir veritabanı ve kullanıcı oluşturun:

```sql
CREATE DATABASE sapb1reports_v2;
CREATE USER sapb1db WITH ENCRYPTED PASSWORD '12345';
GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;
```

`senin_guvenli_sifren` kısmını, güçlü ve güvenli bir şifre ile değiştirmeyi unutmayın.

### Django `settings.py` Ayarları

Daha sonra, Django projenizin `settings.py` dosyasını açın ve veritabanı konfigürasyonunu güncelleyin:

```python
# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sapb1reports_v2',
        'USER': 'sapb1db',
        'PASSWORD': 'senin_guvenli_sifren',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

Bu ayarlar, Django'nun yerel makinenizde çalışan PostgreSQL veritabanınızı kullanmasını sağlayacak. `HOST` genellikle `localhost` olarak ayarlanır, `PORT` ise PostgreSQL varsayılan portu olan `5432`'dir. Eğer PostgreSQL farklı bir portta çalışıyorsa, `PORT` alanını buna göre güncelleyin.

Ayarları yaptıktan sonra, veritabanı şemalarınızı oluşturmak için Django'nun `migrate` komutunu kullanmalısınız:

```bash
python manage.py migrate
```

Bu komut, `settings.py` dosyasındaki konfigürasyonlara göre veritabanı tablolarını oluşturacaktır.



1. **`pg_hba.conf` Dosyasını Düzenleyin:**
   PostgreSQL'in `pg_hba.conf` dosyasını düzenlemek için aşağıdaki komutu kullanın:
   ```bash
   sudo nano /etc/postgresql/14/main/pg_hba.conf
   ```

2. **Gerekli Erişim Kurallarını Ekleyin:**
   `pg_hba.conf` dosyasına, `sapb1db` kullanıcısının `sapb1reports_v2` veritabanına erişimine izin veren bir kural ekleyin. Dosyanın sonuna şu satırları ekleyebilirsiniz:
   ```
   # 'sapb1db' kullanıcısı için erişim kuralı
   host    sapb1reports_v2    sapb1db    127.0.0.1/32    md5
   ```

3. **PostgreSQL Servisini Yeniden Başlatın:**
   Değişiklikleri uygulamak ve yeni erişim kurallarını etkinleştirmek için PostgreSQL servisini yeniden başlatın:
   ```bash
   sudo systemctl restart postgresql
   ```

Bu adımlar, `sapb1db` kullanıcısının `sapb1reports_v2` veritabanına yerel ağ üzerinden bağlanabilmesi için gerekli erişim kurallarını sağlayacaktır. Değişikliklerin ardından, Django uygulamanızın bu veritabanına bağlanması gerektiğini unutmayın.

postgresql table delete and create add user 

cd /
sudo -u postgres psql
DROP DATABASE sapb1reports_v2;

CREATE DATABASE sapb1reports_v2;
CREATE USER sapb1db WITH ENCRYPTED PASSWORD '12345';
GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;



tablo silme
postgres=# \c sapb1reports_v2
You are now connected to database "sapb1reports_v2" as user "postgres".
sapb1reports_v2=# \dt
sapb1reports_v2=# DROP TABLE productconfig_productconfig;
DROP TABLE
sapb1reports_v2=# 


DROP TABLE IF EXISTS                                      
productconfigv2_product,                                   
productconfigv2_productspecification,                      
productconfigv2_specification,                             
productconfigv2_specificationoption,                       
productconfigv2_specoption,                                
productconfigv2_variant,                                   
productconfigv2_variant_selected_options                  
CASCADE;

DELETE FROM django_migrations WHERE app = 'productconfigv2';





******
Tabii, fake migrate işlemi yapabiliriz. Bu, veritabanı tablolarını oluşturmadan migrasyonları uygulanmış olarak işaretler. Bu, özellikle mevcut bir veritabanı şeması ile Django modellerini senkronize etmek istediğinizde kullanışlıdır.

Fake migrate işlemi için şu adımları izleyin:

1. Önce, tüm migrasyonları görmek için şu komutu çalıştırın:

   ```
   python manage.py showmigrations filesharehub
   ```

   Bu, uygulanmamış migrasyonları gösterecektir.

2. Ardından, fake migrate işlemini gerçekleştirin:

   ```
   python manage.py migrate filesharehub --fake
   ```

   Bu komut, tüm migrasyonları uygulanmış olarak işaretleyecektir, ancak gerçekte veritabanında herhangi bir değişiklik yapmayacaktır.

3. Eğer belirli bir migrasyona kadar fake migrate yapmak istiyorsanız, şu komutu kullanabilirsiniz:

   ```
   python manage.py migrate filesharehub <migration_name> --fake
   ```

   Burada `<migration_name>`, migrate etmek istediğiniz son migrasyonun adıdır.

4. İşlem tamamlandıktan sonra, tekrar migrasyonların durumunu kontrol edin:

   ```
   python manage.py showmigrations filesharehub
   ```

   Tüm migrasyonlar uygulanmış olarak işaretlenmiş olmalıdır.

5. Son olarak, Django sunucunuzu yeniden başlatın.

Bu işlemden sonra, admin panelinde hala sorun yaşıyorsanız, şu adımları deneyin:

1. `filesharehub` uygulamasının `INSTALLED_APPS` listesinde olduğundan emin olun.
2. `admin.py` dosyasında `Directory` modelinin doğru şekilde kaydedildiğinden emin olun.
3. Django cache'ini temizleyin:
   ```
   python manage.py clear_cache
   ```
4. Statik dosyaları yeniden toplayın:
   ```
   python manage.py collectstatic
   ```

Eğer hala sorun devam ediyorsa, lütfen `models.py`, `admin.py` ve `settings.py` dosyalarınızın ilgili kısımlarını paylaşın. Bu bilgiler, sorunu daha detaylı analiz etmemize yardımcı olacaktır.

Şimdi durumu daha iyi anlıyorum. Veritabanında productconfig tabloları hiç oluşturulmamış ama django migrations klasöründe eski migration dosyaları var. Bu durumu çözmek için:

1. Öncelikle şu komutu deneyin:
```bash
python manage.py migrate --fake productconfig zero
```

2. Sonra migrations klasörünü temizleyin:
```bash
rm -rf backend/productconfig/migrations/*
touch backend/productconfig/migrations/__init__.py
```

3. Yeni migration'ları oluşturun:
```bash
python manage.py makemigrations productconfig
```

4. Son olarak migrate edin:
```bash
python manage.py migrate productconfig --fake-initial
```

`--fake-initial` parametresi özellikle önemli burada. Bu parametre Django'ya "bu ilk migration'ı gerçekten çalıştırma, sadece çalıştırılmış gibi işaretle" demek oluyor.

Eğer bu adımlar da hata verirse, şu yöntemi deneyebilirsiniz:

1. settings.py dosyasından geçici olarak productconfig uygulamasını kaldırın (INSTALLED_APPS listesinden)
2. Migrations klasörünü temizleyin
3. settings.py'a productconfig uygulamasını geri ekleyin
4. Sonra sırasıyla:
```bash
python manage.py makemigrations productconfig
python manage.py migrate --fake productconfig
```

Bu işlemler sonrasında yeni tablolar oluşturulacak ve migration kayıtları düzgün bir şekilde oluşturulmuş olacak.





4. Arama Performansını İyileştirme (GIN Index ve pg_trgm)

Eğer büyük veri setlerinde arama yapıyorsanız, PostgreSQL’in pg_trgm eklentisi ile arama performansını artırabilirsiniz.
4.1 pg_trgm Eklentisini Yükleme

Eklentiyi yükleyin:

CREATE EXTENSION IF NOT EXISTS pg_trgm;

4.2 GIN Index Ekleyin

Arama yapılan alanlar için GIN index oluşturun:

CREATE INDEX customer_name_trgm_idx
ON orderdetail
USING gin (customer_name gin_trgm_ops);

Bu işlemden sonra ILIKE ve LIKE sorgularınız hızlanacaktır.

Canlı ortamınızda eş zamanlı kullanıcı sayısının 25 olması, PostgreSQL yapılandırmanızı optimize etmek için oldukça iyi bir bilgi. Bu kullanıcı sayısına göre ayarlarınızı biraz daha dengeleyebiliriz. 

Aşağıda, mevcut ayarlarınızı 25 eş zamanlı kullanıcıya uygun hale getirecek öneriler yer alıyor:

---

### **Önerilen Ayarlar**

1. **`shared_buffers`**
   - Şu an: **1GB**
   - Önerilen: **1GB** (Şimdilik ideal. Kullanıcı sayınız 50'yi geçerse 2GB’a çıkarabilirsiniz.)
   - Bu değer, PostgreSQL’in bellekte saklayacağı veritabanı sayfalarının miktarını belirler. 1GB, 16GB RAM'e sahip bir sunucu için yeterli.

2. **`work_mem`**
   - Şu an: **32MB**
   - Önerilen: **16-32MB**
     - **16MB**: Daha fazla eş zamanlı sorgu çalıştırıldığında bellekte aşırı yüklenme olmaz.
     - **32MB**: Daha karmaşık sorgular ve daha az kullanıcı ile daha hızlı sorgu performansı sağlar.
   - **Hesaplama**:
     25 kullanıcı x 32MB = 800MB bellek kullanımı.
     Bellek kısıtlamaları nedeniyle daha düşük değerler seçilebilir.

3. **`maintenance_work_mem`**
   - Şu an: **256MB**
   - Önerilen: **256MB**
   - Bu değer, bakım işlemleri (indeks oluşturma, `VACUUM`, `ANALYZE`) sırasında kullanılır. Şu anki değer yeterlidir.

4. **`effective_cache_size`**
   - Şu an: **4GB**
   - Önerilen: **4GB**
     - Bu değer, PostgreSQL’in sorgu planlaması sırasında kullanılabilir bellek miktarını tahmin etmesini sağlar.
     - **4GB**, toplam RAM’inizin %50-75’i olduğu için uygundur.

---

### **Neden Bu Ayarlar?**

- **25 Eş Zamanlı Kullanıcı**:
  - Kullanıcı başına tahsis edilen `work_mem` sayesinde her kullanıcının sorgusu için yeterli bellek ayrılır.
- **16GB RAM**:
  - RAM kullanımını dengeleyerek, sistemin diğer servislerinin de sorunsuz çalışmasını sağlıyoruz.
- **Sunucu Kaynakları**:
  - Bellek ve işlemci kaynaklarını aşırı kullanmadığınız için sistem genelinde kararlılık sağlanır.

---

### **Ayarları Güncellemek**

PostgreSQL yapılandırmasını güncellemek için:

1. **`postgresql.conf` Dosyasını Düzenleyin**:
   ```bash
   sudo nano /etc/postgresql/14/main/postgresql.conf
   ```

2. **Ayarları Güncelleyin**:
   ```conf
   shared_buffers = 1GB
   work_mem = 16MB
   maintenance_work_mem = 256MB
   effective_cache_size = 4GB
   ```

3. **PostgreSQL’i Yeniden Başlatın**:
   ```bash
   sudo systemctl restart postgresql
   ```

---

### **Performansı İzleme ve Test Etme**

1. **Bağlantı Sayısı**:
   - PostgreSQL’e bağlanan kullanıcı sayısını kontrol edin:
     ```sql
     SELECT count(*) FROM pg_stat_activity;
     ```

2. **Sorgu Performansı**:
   - Önemli sorguları test edin ve zamanlamasını analiz edin:
     ```sql
     EXPLAIN ANALYZE SELECT * FROM orderarchive_orderdetail WHERE customer_name ILIKE '%test%';
     ```

3. **Bellek Kullanımı**:
   - PostgreSQL’in bellek kullanımını izlemek için:
     ```sql
     SELECT name, setting FROM pg_settings WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem', 'effective_cache_size');
     ```

---

### **Sonuç**

Bu yapılandırma, **25 kullanıcıya kadar eş zamanlı sorguları** ve **orta karmaşıklıktaki işlemleri** destekleyecek şekilde optimize edilmiştir. Zamanla kullanıcı artışı veya karmaşık sorgularla karşılaşırsanız, özellikle `work_mem` ve `shared_buffers` değerlerini artırmayı düşünebilirsiniz. Ancak şu anki ayarlarınız canlı ortamda stabil bir performans sunacaktır.