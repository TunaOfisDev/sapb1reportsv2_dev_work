
hana rapor db backup
\\10.130.212.112\PostgresqlDb_backup
user: hanarapdb
pass: 12345


# PostgreSQL 17.2 Veritabanı Silme, Oluşturma ve Yedekten Geri Dönme İş Talimatı

## A. Veritabanı Silme

1. Süper kullanıcı olarak PostgreSQL'e bağlanın:
   ```bash
   sudo -u postgres psql
   ```

2. Mevcut bağlantıları sonlandırın:
   ```sql
   SELECT pg_terminate_backend(pg_stat_activity.pid)
   FROM pg_stat_activity
   WHERE pg_stat_activity.datname = 'sapb1reports_v2'
   AND pid <> pg_backend_pid();
   ```

3. Veritabanını silin:
   ```sql
   DROP DATABASE IF EXISTS sapb1reports_v2;
   ```

4. PostgreSQL komut satırından çıkın:
   ```sql
   \q
   ```

## B. Yeni Veritabanı Oluşturma

1. Süper kullanıcı olarak PostgreSQL'e bağlanın:
   ```bash
   sudo -u postgres psql
   ```

2. Kullanıcı yoksa oluşturun:
   ```sql
   CREATE USER sapb1db WITH ENCRYPTED PASSWORD '12345';
   ```

3. Türkçe karakter destekli veritabanını oluşturun:
   ```sql
   CREATE DATABASE sapb1reports_v2
   WITH 
   OWNER = postgres
   ENCODING = 'UTF8'
   LC_COLLATE = 'tr_TR.UTF-8'
   LC_CTYPE = 'tr_TR.UTF-8'
   TEMPLATE = template0;
   ```

4. Yetkilendirmeleri yapın:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE sapb1reports_v2 TO sapb1db;
   \c sapb1reports_v2
   GRANT ALL ON SCHEMA public TO sapb1db;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sapb1db;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sapb1db;
   ```

5. PostgreSQL komut satırından çıkın:
   ```sql
   \q
   ```

## C. Kimlik Doğrulama Ayarlarını Yapılandırma

1. PostgreSQL kimlik doğrulama yapılandırma dosyasını düzenleyin:
   ```bash
   sudo nano /etc/postgresql/17/main/pg_hba.conf
   ```

2. Aşağıdaki satırı bulun:
   ```
   local   all             all                                     peer
   ```

3. Bu satırı şöyle değiştirin:
   ```
   local   all             all                                     md5
   ```

4. Değişiklikleri kaydedip çıkın (CTRL+O, Enter, CTRL+X).

5. PostgreSQL servisini yeniden başlatın:
   ```bash
   sudo systemctl restart postgresql
   ```

## D. Yedekten Geri Yükleme

### Seçenek 1: SQL Formatındaki Yedeği Geri Yükleme

1. Yedek dosyasının izinlerini kontrol edin ve gerekirse düzeltin:
   ```bash
   sudo chmod a+r /home/user/Downloads/backup_db/sapb1reports_v2.sql
   ```

2. SQL yedeğini geri yükleyin:
   ```bash
   PGPASSWORD='12345' psql -U sapb1db -d sapb1reports_v2 -f /home/user/Downloads/backup_db/sapb1reports_v2.sql
   ```

### Seçenek 2: Custom Format Yedeği Geri Yükleme

1. Yedek dosyasının izinlerini kontrol edin ve gerekirse düzeltin:
   ```bash
   sudo chmod a+r /home/user/Downloads/backup_db/sapb1reports_v2.dump
   ```

2. Custom format yedeği geri yükleyin:
   ```bash
   PGPASSWORD='12345' pg_restore -h localhost -p 5432 -U sapb1db -d sapb1reports_v2 -v /home/user/Downloads/backup_db/sapb1reports_v2.dump
   ```

## E. Geri Yükleme Kontrolü

1. Veritabanına bağlanın:
   ```bash
   PGPASSWORD='12345' psql -U sapb1db -d sapb1reports_v2
   ```

2. Tabloları listeleyin:
   ```sql
   \dt
   ```

3. Tablo sayısını kontrol edin:
   ```sql
   SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
   ```

4. Örnek bir tablonun kayıt sayısını kontrol edin (tablo_adı kısmını uygun bir tablo adıyla değiştirin):
   ```sql
   SELECT COUNT(*) FROM tablo_adı;
   ```

5. PostgreSQL komut satırından çıkın:
   ```sql
   \q
   ```

## F. Sorun Giderme

Geri yükleme sırasında hatalarla karşılaşırsanız:

1. Hata mesajlarını kontrol edin ve kaydedin.

2. Veritabanını yeniden oluşturun ve alternatif yedek formatını deneyin (SQL yerine dump veya dump yerine SQL).

3. Geri yükleme için `-c` veya `--clean` parametresini deneyin:
   ```bash
   PGPASSWORD='12345' pg_restore -h localhost -p 5432 -U sapb1db -d sapb1reports_v2 -v --clean /home/user/Downloads/backup_db/sapb1reports_v2.dump
   ```

4. Yalnızca verileri geri yükleyin:
   ```bash
   PGPASSWORD='12345' pg_restore -h localhost -p 5432 -U sapb1db -d sapb1reports_v2 -v --data-only /home/user/Downloads/backup_db/sapb1reports_v2.dump
   ```












Eğer Samba'da belirli bir kullanıcı için şifreyi unuttuysanız, kullanıcıya yeniden bir şifre atayabilirsiniz. Samba üzerinde şifre ataması yapmak için aşağıdaki adımları takip edebilirsiniz:

1. **Terminali açın** ve root yetkisi alın:
   ```bash
   sudo su
   ```

2. **Samba kullanıcısına yeni bir şifre atayın**:
   Aşağıdaki komut ile "hanarapdb" kullanıcısına yeni bir şifre belirleyebilirsiniz:
   ```bash
   smbpasswd -a hanarapdb
   ```

3. Şifre sorma ekranında yeni bir şifre girin ve onaylayın.

Bu işlemden sonra, `hanarapdb` kullanıcısı yeni şifresi ile paylaşıma erişebilir. Eğer kullanıcı zaten tanımlıysa, sadece şifreyi değiştirmek için yukarıdaki komutu kullanabilirsiniz.

Yedekleme işlemini başlatmak için aşağıdaki adımları takip edebilirsiniz:

### PostgreSQL Yedeği Alma
1. **Doğru Dizin ve Yetkiler**  
   Hedef dizinin mevcut ve yazılabilir olduğundan emin olun:
   ```bash
   mkdir -p /home/user/Downloads/backup_db
   chmod 755 /home/user/Downloads/backup_db
   ```

2. **Yedekleme Komutu**  
   PostgreSQL yedeğini almak için aşağıdaki komutu kullanabilirsiniz:
   ```bash
   PGPASSWORD='12345' pg_dump -U sapb1db -F c -d sapb1reports_v2 -f /home/user/Downloads/backup_db/sapb1reports_v2.backup
   ```

   - **`-F c`**: Özel format (`custom format`) için. Daha hızlı geri yükleme sağlar.
   - **`-f`**: Çıkış dosyasının yolunu belirtir (`sapb1reports_v2.backup`).

3. **Başarı Durumu Kontrolü**  
   Yedekleme işleminin tamamlanıp tamamlanmadığını kontrol edin:
   ```bash
   ls -lh /home/user/Downloads/backup_db/sapb1reports_v2.backup
   ```

4. **Hata Durumunda Günlük Kontrolü**  
   Eğer hata alırsanız, günlük dosyasını kontrol edin veya daha ayrıntılı bilgi için `-v` (verbose) seçeneğini ekleyin:
   ```bash
   PGPASSWORD='12345' pg_dump -U sapb1db -F c -d sapb1reports_v2 -f /home/user/Downloads/backup_db/sapb1reports_v2.backup -v
   ```

Bu adımları takip ederek yedekleme işlemini başarıyla tamamlayabilirsiniz. Eğer hata alırsanız, lütfen hata mesajını paylaşın, çözüm için yardımcı olayım.