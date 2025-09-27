sudo chown -R www-data:www-data /var/www/sapb1reportsv2/backend/logs
sudo setfacl -m u:user:rwX /var/www/sapb1reportsv2/backend/logs


sudo chmod +x /var/www/sapb1reportsv2/backend/scripts/backend.sh


Elbette, bu yetki sorununu hemen düzeltelim.

Hata mesajı (`chown: invalid group: ‘www-data:sapb1’`) oldukça açık. Çalıştırdığınız `backend.sh` script'i, bu sunucuda mevcut olmayan bir kullanıcı (`www-data`) ve grup (`sapb1`) adına dosya sahipliğini değiştirmeye çalışıyor. Bu script muhtemelen farklı bir sunucu ortamından (üretim ortamı gibi) kopyalanmış.

Biz bu sunucuyu kurarken tüm dosya sahipliğini ve servisleri **`userbt`** kullanıcısı ve **`userbt`** grubu üzerinden yönettik. Dolayısıyla script'leri de bu yapıya uygun hale getirmeliyiz.

-----

### \#\# Adım 1: `backend.sh` Script'ini Düzeltme

Öncelikle hata aldığınız script'i düzenleyelim.

1.  **Script dosyasını açın:**

    ```bash
    nano /var/www/sapb1reportsv2/backend/scripts/backend.sh
    ```

2.  **Hatalı satırı bulun:** Dosyanın içinde aşağıdaki gibi bir satır göreceksiniz.

    ```bash
    sudo chown -R www-data:sapb1 backend/logs frontend/build
    ```

3.  **Satırı doğru kullanıcı ve grupla değiştirin:** `www-data:sapb1`'i `userbt:userbt` olarak güncelleyin.

    ```bash
    sudo chown -R userbt:userbt backend/logs frontend/build
    ```

4.  Dosyayı kaydedip (`Ctrl + X`, `Y`, `Enter`) kapatın.

-----

### \#\# Adım 2: `frontend.sh` Script'ini Düzeltme (Proaktif Düzeltme)

Paylaştığınız `frontend.sh` dosyasının içeriğinde de aynı hatalı `chown` komutu bulunuyor. Olası bir hatayı şimdiden önlemek için onu da düzeltelim.

1.  **Script dosyasını açın:**

    ```bash
    nano /var/www/sapb1reportsv2/backend/scripts/frontend.sh
    ```

2.  **Hatalı satırı bulun:**

    ```bash
    sudo chown -R www-data:sapb1 build
    ```

3.  **Satırı doğru kullanıcı ve grupla değiştirin:**

    ```bash
    sudo chown -R userbt:userbt build
    ```

4.  Dosyayı kaydedip kapatın.

-----

### \#\# Adım 3: Script'lere Çalıştırma İzni Verme

Genellikle dosya sistemine yeni kopyalanan script'lerin "çalıştırma" izni olmaz. Bu izni vererek gelecekteki "Permission denied" hatalarını da önleyelim.

Aşağıdaki komut, `scripts` klasöründeki tüm `.sh` uzantılı dosyalara çalıştırma izni verecektir.

```bash
chmod u+x /var/www/sapb1reportsv2/backend/scripts/*.sh
```

-----

### \#\# Sonuç: Tekrar Deneme

Artık her şey hazır. `backend.sh` script'ini tekrar çalıştırabilirsiniz.

```bash
cd /var/www/sapb1reportsv2/backend/scripts
sudo ./backend.sh
```

Bu sefer script'in yetki hatası vermeden başarıyla çalışması gerekiyor.