Anladım, ayarları doğru bağlantı komutunuza göre yapılandıracağız. Aşağıdaki adımlarla tüm ayarları yeniden düzenleyebiliriz:
test
### 1. **Doğru Mount Komutu ile Bağlantı**

Aşağıdaki komutla paylaşıma doğru şekilde bağlanabilirsiniz:

```bash
sudo mount -t cifs -o username=tuna,password=tunaml370,vers=3.0 //192.168.2.200/gorseller /mnt/gorseller
```
//test
### 2. **Bağlantıyı /etc/fstab'a Ekleyerek Kalıcı Hale Getirme**

Sistemi her başlattığınızda bu bağlantının otomatik olarak mount edilmesini sağlamak için `/etc/fstab` dosyasına ayarları ekleyelim:

1. **/etc/fstab dosyasını açın:**

   ```bash
   sudo nano /etc/fstab
   ```

2. **Aşağıdaki satırı ekleyin:**

   ```bash
   //192.168.2.200/gorseller /mnt/gorseller cifs username=tuna,password=tunaml370,vers=3.0,iocharset=utf8,file_mode=0775,dir_mode=0775 0 0
   ```

3. **Değişiklikleri kaydedin ve çıkın** (Ctrl + O, ardından Ctrl + X).

4. **Bağlantıyı test edin:**

   ```bash
   sudo mount -a
   ```

Bu komut, `/etc/fstab`'a eklediğiniz tüm paylaşımları mount eder ve başarılı olup olmadığını kontrol edebilirsiniz.

### 3. **Kimlik Bilgilerini Gizli Tutmak İçin Credentials Dosyası Kullanma**

Parolanızı `/etc/fstab` dosyasına yazmak yerine, daha güvenli bir yol olan bir credentials dosyası oluşturabilirsiniz:

1. **Kimlik bilgileri dosyasını oluşturun:**

   ```bash
   sudo nano /etc/samba/credentials
   ```

2. **İçerisine kullanıcı adı ve şifreyi ekleyin:**

   ```bash
   username=tuna
   password=tunaml370
   ```

3. **Bu dosyanın izinlerini güvenli hale getirin:**

   ```bash
   sudo chmod 600 /etc/samba/credentials
   ```

4. **/etc/fstab dosyasındaki girişi şu şekilde güncelleyin:**

   ```bash
   //192.168.2.200/gorseller /mnt/gorseller cifs credentials=/etc/samba/credentials,vers=3.0,iocharset=utf8,file_mode=0775,dir_mode=0775 0 0
   ```

Bu yöntemle kullanıcı adı ve şifreyi doğrudan `/etc/fstab` dosyasına yazmadan, güvenli bir şekilde bağlantıyı sağlayabilirsiniz.

### 4. **Bağlantıyı Test Etme**

Eğer mount işlemi başarılı olursa, bağlantıyı kontrol etmek için `/mnt/gorseller` dizinindeki dosyaları listeleyebilirsiniz:

```bash
ls /mnt/gorseller
```

Eğer sorun devam ederse, bağlantı sorunlarını detaylandırmak için `dmesg` çıktısına veya Samba loglarına bakabiliriz.

***
sh lari sifresiz calistirmak icin
sudo visudo



sifre atama terminalden komutlari sira ile calistir

MY_SAMBA_PASSWORD="*******"
echo $MY_SAMBA_PASSWORD
(echo "$MY_SAMBA_PASSWORD"; echo "$MY_SAMBA_PASSWORD") | sudo smbpasswd -s hanarapdb


**************

Tamam, `/srv/samba/PostgresqlDb_backup` klasörünü silip yeniden oluşturalım ve gerekli izinleri verelim. Aşağıdaki adımları takip edelim:

1. Mevcut klasörü ve içeriğini silin:
    ```bash
    sudo rm -rf /srv/samba/PostgresqlDb_backup
    ```

2. Klasörü yeniden oluşturun:
    ```bash
    sudo mkdir -p /srv/samba/PostgresqlDb_backup
    ```

3. Klasör izinlerini ve sahipliğini ayarlayın:
    ```bash
    sudo chown -R nobody:nogroup /srv/samba/PostgresqlDb_backup
    sudo chmod -R 0755 /srv/samba/PostgresqlDb_backup
    ```

4. Samba yapılandırma dosyasını yeniden kontrol edin ve gerekirse yeniden başlatın:
    ```bash
    sudo nano /etc/samba/smb.conf
    ```

    İçeriğin aşağıdaki gibi olduğundan emin olun:
    ```ini
    [global]
       workgroup = WORKGROUP
       server string = Samba Server %v
       netbios name = ubuntu
       security = user
       map to guest = bad user
       dns proxy = no

    [PostgresqlDb_backup]
       path = /srv/samba/PostgresqlDb_backup
       valid users = hanarapdb
       read only = yes
       browsable = yes
       guest ok = no
       create mask = 0755
       directory mask = 0755

   [gorseller]
   path = /mnt/gorseller
   available = yes
   valid users = @sapb1db   
   read only = yes
   browseable = yes
   guest ok = no
   create mask = 0755
   directory mask = 0755

   


    ```

5. Samba servislerini yeniden başlatın:
    ```bash
    sudo systemctl restart smbd
    sudo systemctl restart nmbd
    ```

Bu adımlar tamamlandıktan sonra, `hanarapdb` kullanıcısının sadece okuma yetkisine sahip olması gerekecek. Artık Samba paylaşımınıza erişip doğru şekilde çalışıp çalışmadığını kontrol edebilirsiniz.


Samba paylaşımını, istemci makinelerde **otomatik olarak bağlamak** için (mount etmek) birkaç yöntem kullanabilirsiniz. Ubuntu gibi Linux sistemlerde, Samba paylaşımını sürekli ve otomatik olarak bağlayacak bir ayarlama yapmak için `fstab` veya `systemd` gibi araçlar kullanabilirsiniz. İşte bu süreci adım adım nasıl gerçekleştireceğinizi anlatacağım:

### 1. **Otomatik Mount Etmek İçin Bağlantı Noktası Oluşturun**
İlk olarak, Samba paylaşımını bağlayacağınız yerel bir klasör oluşturmanız gerekiyor. Bu klasörü Samba paylaşımlarına erişmek için kullanacağız.

```bash
sudo mkdir -p /mnt/gorseller
```

### 2. **Kimlik Doğrulama Bilgilerini Dosyada Saklama (Önerilir)**
Samba paylaşımlarına kimlik doğrulaması yaparak bağlanmak gerektiğinde, kimlik bilgilerinizi `fstab` dosyasına direkt olarak yazmak yerine, bir kimlik bilgisi dosyasında saklamak güvenlik açısından daha iyidir.

#### 2.1 Kimlik Bilgisi Dosyası Oluşturun
Örneğin `/etc/samba/credentials` dosyasına bağlantı bilgilerinizi kaydedin:

```bash
sudo nano /etc/samba/credentials
```

Bu dosyaya aşağıdaki bilgileri ekleyin:

```conf
username=sapb1db
password=your_password
```

Bu kimlik bilgilerini kaydettikten sonra dosyanın güvenlik izinlerini değiştirin:

```bash
sudo chmod 600 /etc/samba/credentials
```
- `chmod 600` komutu dosyanın yalnızca sahibi tarafından okunabilmesini sağlar, böylece kimlik bilgileriniz korunur.

### 3. **/etc/fstab Dosyasını Düzenleyin**
Samba paylaşımının otomatik olarak mount edilmesi için `/etc/fstab` dosyasına uygun bir satır eklemeniz gerekmektedir.

#### 3.1 fstab Dosyasını Düzenleyin
`/etc/fstab` dosyasını açarak düzenleyin:

```bash
sudo nano /etc/fstab
```

Dosyanın sonuna şu satırı ekleyin:

```fstab
//192.168.2.200/gorseller /mnt/gorseller cifs credentials=/etc/samba/credentials,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0

//192.168.2.200/GORSELLER /mnt/gorseller cifs credentials=/etc/samba-credentials,uid=1000,iocharset=utf8 0 0

```

Açıklamalar:
- `//192.168.2.200/gorseller`: Samba sunucusunun IP adresi ve paylaşılan klasör adı.
- `/mnt/gorseller`: Bu paylaşımın yerel olarak bağlanacağı dizin.
- `cifs`: Bu paylaşımı CIFS (Common Internet File System) protokolü kullanarak bağlayacağınızı belirtir.
- `credentials=/etc/samba/credentials`: Kimlik bilgilerini kullanmak için yukarıda oluşturduğunuz kimlik dosyasını belirttiniz.
- `iocharset=utf8`: UTF-8 karakter setini kullanarak Türkçe karakterleri doğru şekilde destekler.
- `file_mode=0755,dir_mode=0755`: Dosya ve klasör izinlerini belirler.

#### 3.2 fstab Mount Testi
Yapılandırmaların doğru çalışıp çalışmadığını test etmek için şu komutu çalıştırabilirsiniz:

```bash
sudo mount -a
```

Bu komut `/etc/fstab` dosyasındaki tüm girişleri mount etmeye çalışır ve eğer her şey doğru yapılandırıldıysa `/mnt/gorseller` dizini, Samba paylaşımına otomatik olarak bağlanmış olur.

### 4. **Systemd Üzerinden Alternatif Bir Yöntem (Otomatik Mount İçin)**
`fstab` dışında, `systemd` kullanarak da bir mount ünitesi oluşturabilirsiniz. Bu yöntem genellikle daha dinamik ve modüler bir yapı sunar.

#### 4.1 Mount Unit Dosyası Oluşturun
`/etc/systemd/system` altında bir mount unit dosyası oluşturun. Örneğin `/etc/systemd/system/mnt-gorseller.mount` adıyla bir dosya:

```bash
sudo nano /etc/systemd/system/mnt-gorseller.mount
```

Dosyaya şu içeriği ekleyin:

```conf
[Unit]
Description=Mount Samba Share gorseller
After=network-online.target
Wants=network-online.target

[Mount]
What=//192.168.2.200/gorseller
Where=/mnt/gorseller
Type=cifs
Options=credentials=/etc/samba/credentials,iocharset=utf8,file_mode=0755,dir_mode=0755

[Install]
WantedBy=multi-user.target
```

#### 4.2 Mount Unit'i Etkinleştirin
Aşağıdaki komutlarla mount unit dosyasını etkinleştirin ve mount edin:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mnt-gorseller.mount
sudo systemctl start mnt-gorseller.mount
```

Bu komutlar, sistem başladığında Samba paylaşımını otomatik olarak mount eder.

### 5. **Erişim Kontrolleri ve Sorun Giderme**
- **İzin Kontrolleri**: Eğer paylaşıma bağlandıktan sonra klasöre erişemiyorsanız, paylaşıma erişmeye çalışan kullanıcının yeterli izinlere sahip olup olmadığını kontrol edin.
- **Kimlik Bilgileri**: `/etc/samba/credentials` dosyasındaki kullanıcı adı ve parolanın geçerli olduğundan emin olun.
- **Günlükler (Logs)**: Mount işlemi başarısız olursa, `/var/log/syslog` veya `dmesg` üzerinden hataların detaylarına erişebilirsiniz.

### **Özetle**
1. `/mnt/gorseller` klasörünü oluşturun.
2. `/etc/samba/credentials` dosyasında Samba kimlik bilgilerinizi saklayın.
3. `/etc/fstab` dosyasını düzenleyerek Samba paylaşımını otomatik olarak mount edin.
4. `mount -a` komutuyla mount işlemine emin olun.
5. Alternatif olarak `systemd` mount unit dosyası kullanarak da otomatik mount yapabilirsiniz.

Bu ayarlamalarla `/mnt/gorseller` Samba paylaşımını Ubuntu sistemi üzerinde otomatik olarak mount edeceksiniz ve klasöre her erişim ihtiyacında manuel mount yapmanıza gerek kalmayacak.


username=tuna         
password=tunaml370

Bu hata, `mnt-gorseller.mount` dosyasının, `systemd` tarafından otomatik olarak oluşturulan geçici (transient) bir ünite olduğunu belirtiyor. Bu nedenle, bu mount birimini `enable` etmek mümkün olmuyor çünkü bu birim yalnızca geçici olarak, mevcut oturum süresince oluşturulmuş durumda. Bu hatayı düzeltmek için yapılması gereken birkaç adım var:

### Çözüm: Mount Ünite Dosyasını Kalıcı Hale Getirin

Geçici bir mount birimi yerine, kalıcı bir `systemd` mount birimi oluşturmalısınız. Bu işlemi doğru bir şekilde yapmak için aşağıdaki adımları izleyebilirsiniz.

#### 1. Mount Unit Dosyasını Doğru Yerde Oluşturun
Mount unit dosyasını `/etc/systemd/system` altında oluşturmanız gerekiyor. Daha önce yapılan işlemde, muhtemelen yanlış dizine ya da geçici bir mount ünitesi olarak eklenmiş olabilir.

Mount unit dosyasını `/etc/systemd/system` klasöründe oluşturun:

```bash
sudo nano /etc/systemd/system/mnt-gorseller.mount
```

Dosyanın içeriği şu şekilde olmalıdır:

```ini
[Unit]
Description=Mount Samba Share gorseller
After=network-online.target
Wants=network-online.target

[Mount]
What=//192.168.2.200/gorseller
Where=/mnt/gorseller
Type=cifs
Options=credentials=/etc/samba/credentials,iocharset=utf8,file_mode=0755,dir_mode=0755

[Install]
WantedBy=multi-user.target
```

### 2. Daemon Reload Komutunu Yeniden Çalıştırın
Bu değişikliklerin geçerli olması için `systemd` servisini yeniden yüklemeniz gerekiyor:

```bash
sudo systemctl daemon-reload
```

### 3. Mount Ünitesini Etkinleştirin ve Başlatın
Şimdi mount ünitesini etkinleştirip başlatabilirsiniz:

```bash
sudo systemctl enable mnt-gorseller.mount
```

Bu komut, mount işlemini sistem her başladığında otomatik olarak yapılacak şekilde ayarlayacaktır. Son olarak mount birimini hemen başlatın:

```bash
sudo systemctl start mnt-gorseller.mount
```

### 4. Durumunu Kontrol Edin
Mount işleminin başarılı olup olmadığını kontrol etmek için:

```bash
sudo systemctl status mnt-gorseller.mount
```

Bu komut, mount işlemi sırasında herhangi bir hata olup olmadığını ve mount biriminin durumunu gösterecektir.

### Alternatif Yöntem: /etc/fstab Kullanarak Mount Etmek
Eğer `systemd` mount üniteleriyle ilgili sorun yaşıyorsanız, `fstab` dosyasını kullanarak mount etmenin daha basit bir çözüm olabileceğini unutmayın.

`/etc/fstab` dosyasını düzenlemek ve mount birimini eklemek:

```bash
sudo nano /etc/fstab
```

Sonuna şu satırı ekleyin:

```fstab
//192.168.2.200/gorseller /mnt/gorseller cifs credentials=/etc/samba/credentials,iocharset=utf8,file_mode=0755,dir_mode=0755 0 0
```

Daha sonra mount işlemi gerçekleştirmek için:

```bash
sudo mount -a
```

Bu yöntem, sistem her başladığında `/etc/fstab` dosyasındaki ayarlar ile Samba paylaşımını otomatik olarak mount eder.

credential



Log dosyasındaki hata, `tuna` kullanıcısının "gorseller" paylaşımına erişim yetkisinin olmadığını gösteriyor (`NT_STATUS_ACCESS_DENIED`). Bu durum, Samba paylaşımında belirtilen `valid users` ayarlarının doğru yapılandırılmadığını veya `tuna` kullanıcısının paylaşıma erişim iznine sahip olmadığını gösteriyor.

### 1. **Samba Paylaşımında İzinleri Kontrol Edin**
Samba yapılandırma dosyasında, `tuna` kullanıcısının `gorseller` paylaşımına erişimi olduğundan emin olalım.

#### `/etc/samba/smb.conf` Dosyasını Kontrol Edin:
Dosyayı düzenleyin ve ilgili paylaşımı kontrol edin:

```bash
sudo nano /etc/samba/smb.conf
```

`gorseller` paylaşımı şu şekilde olmalıdır:

```ini
[gorseller]
   path = /mnt/gorseller
   available = yes
   valid users = tuna
   read only = yes
   browseable = yes
   guest ok = no
   create mask = 0444
   directory mask = 0555
```

- `valid users = tuna`: `tuna` kullanıcısının bu paylaşımda yetkili olduğundan emin olun. Eğer bu satır eksikse, ekleyin.

### 2. **Dosya İzinlerini Kontrol Edin**
Paylaşılan dizinin (`/mnt/gorseller`) doğru sahiplik ve izinlere sahip olduğundan emin olun. Samba'nın, kullanıcının okuma erişimine sahip olduğundan emin olması gerekir.

```bash
sudo chown root:tuna /mnt/gorseller
sudo chmod 755 /mnt/gorseller
```

Bu komutlar, `tuna` kullanıcısına dizin üzerinde gerekli okuma iznini verir.

### 3. **Samba Servisini Yeniden Başlatma**
Yapılandırma dosyasında değişiklik yaptıktan sonra, Samba servisini yeniden başlatın:

```bash
sudo systemctl restart smbd
sudo systemctl restart nmbd
```

### 4. **Kullanıcı Gruplarını Kontrol Edin**
Eğer `valid users` kısmında bir grup kullanıyorsanız (örneğin `@users` gibi), `tuna` kullanıcısının o grupta olduğundan emin olun:

```bash
groups tuna
```

Eğer kullanıcı grupta değilse, kullanıcıyı gruba ekleyin:

```bash
sudo usermod -aG groupname tuna
```

### 5. **Paylaşım İzinlerini Doğrulama**
Paylaşıma erişim için Samba tarafından belirtilen dizin izinlerinin doğru olduğundan emin olun. Eğer kullanıcı `valid users` listesinde değilse veya grup erişimi doğru ayarlanmamışsa, bu hatayı alabilirsiniz.

### 6. **Mount İşlemini Tekrar Deneme**
Yukarıdaki ayarları yaptıktan sonra mount komutunu tekrar deneyin:

```bash
sudo mount -t cifs -o username=tuna,password=tunaml370,iocharset=utf8,ro,file_mode=0444,dir_mode=0555,vers=3.0 //192.168.2.200/gorseller /mnt/gorseller
```

Bu adımlar `tuna` kullanıcısının paylaşım erişimini sağlamalıdır. Eğer sorun devam ederse, loglarda ek hata mesajları üzerinden devam edebiliriz.



    sudo nano /etc/samba/smb.conf
    ```

    İçeriğin aşağıdaki gibi olduğundan emin olun:
    ```ini
   [global]
      workgroup = WORKGROUP
      server string = Samba Server %v
      netbios name = ubuntu
      security = user
      map to guest = bad user
      dns proxy = no

   [PostgresqlDb_backup]
      path = /srv/samba/PostgresqlDb_backup
      valid users = hanarapdb
      read only = yes
      browsable = yes
      guest ok = no
      create mask = 0755
      directory mask = 0755

   [gorseller]
      path = /mnt/gorseller
      available = yes
      valid users = @sapb1db   
      read only = yes
      browseable = yes
      guest ok = no
      create mask = 0755
      directory mask = 0755
