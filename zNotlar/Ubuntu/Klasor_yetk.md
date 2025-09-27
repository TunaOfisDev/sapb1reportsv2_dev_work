

sudo -u www-data bash
sanal ortami yeninden etikinlestir
www-data@reportserver:~/sapb1reportsv2$ source venv/bin/activate
(venv) www-data@reportserver:~/sapb1reportsv2$ 

ls -ld /var/www/sapb1reportsV2/venv
sudo chmod -R 775 /var/www/sapb1reportsV2     
sudo usermod -a -G www-data user
sudo setfacl -m u:user:rwx /var/www/sapb1reportsV2  

Projenin bulunduğu dizindeki tüm klasör ve dosyalar için `user` kullanıcısına tam okuma, yazma ve silme yetkisi vermek istiyorsanız, `chmod` ve `chown` komutlarını kullanabilirsiniz. Bu işlemi yapmadan önce, bu tür izin değişikliklerinin güvenlik riskleri taşıyabileceğini ve yalnızca gerektiğinde yapılması gerektiğini unutmamak önemlidir. İzinleri değiştirmeden önce yedekleme yapmanızı öneririm.

Terminalde aşağıdaki komutları kullanabilirsiniz:

```bash
# Kullanıcı sahipliğini değiştirmek için
sudo chown -R user:user /var/www/sapb1reportsv2
cd /var/www/sapb1reportsv2/frontend
npm run build
cd

sudo chown -R www-data:www-data /var/www/sapb1reportsv2
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status nginx
sudo systemctl status gunicorn

sudo systemctl stop gunicorn
sudo systemctl stop nginx

sudo systemctl status gunicorn


sudo chmod -R 777 /var/www/sapb1reportsv2/venv

# Tüm izinleri vermek için
sudo chmod -R 777 /var/www/sapb1reportsv2/
```

Burada `-R` parametresi, komutun rekürsif olarak çalışmasını sağlar; yani belirtilen dizin ve içindeki tüm alt dizinler ile dosyalar üzerinde işlem yapar. `user:user` ise `kullanıcı_adı:grup_adı` formatındadır ve her ikisi de `user` olarak belirtildiği için, hem kullanıcı adı hem de grup adı olarak `user` kullanılır.

`chmod 777` komutu ise okuma (`r`), yazma (`w`) ve çalıştırma (`x`) izinlerini kullanıcı, grup ve diğer herkese verir. Ancak, bu çok geniş izinler demektir ve güvenlik açısından önerilmez. Eğer bu izinleri yalnızca `user` kullanıcısına vermek istiyorsanız ve başkalarının erişimini sınırlamak istiyorsanız, `700` kullanabilirsiniz:

```bash
sudo chmod -R 700 /home/user/sapb1reportsV2/
```

Bu durumda yalnızca `user` tam erişim hakkına sahip olur.

Her zaman olduğu gibi, böyle bir değişiklik yapmadan önce dikkatli olmak ve yaptığınız değişikliklerin sisteminizin diğer bölümlerini nasıl etkileyebileceğini düşünmek önemlidir. İşlemleri yaparken dikkatli ol ve herhangi bir aksamada, sana yardımcı olabilecek daha fazla bilgi için buradayım. Başarılar Selim!



Linux'ta bir kullanıcıya belirli bir dizinde tam erişim yetkisi vermek için `chmod` ve `chown` komutlarını kullanabilirsiniz. Ayrıca, yeni oluşturulan dosya ve klasörler için varsayılan izinleri ayarlamak amacıyla `setfacl` komutunu kullanarak dosya erişim kontrol listeleri (ACL'ler) ayarlayabilirsiniz.

sudo setfacl -m u:user:rw /home/user/sapb1reportsV2


İşte adım adım talimatlar:

1. **Mevcut Dosya ve Klasörlere Sahiplik Atama:**
   Klasör ve içeriğinin sahipliğini "user" kullanıcısına atayarak başlayabilirsiniz. Bunu yapmak için aşağıdaki komutu kullanın:

   
   sudo chown -R user:user /home/user/sapb1reports_v2
   ```

   Bu komut, `sapb1reports_v2` klasörünü ve içeriğini rekürsif olarak (`-R` seçeneği ile) "user" kullanıcısına ve grubuna atar.

2. **Mevcut Dosya ve Klasörlere Tam Yetki Verme:**
   Kullanıcıya ve grubuna klasör ve dosyalar üzerinde tam yetki vermek için aşağıdaki komutu kullanabilirsiniz:

   
   sudo chmod -R 770 /home/user/sapb1reports_v2
   ```

   `770` izin kodu, sahip ve grup üyelerine okuma, yazma ve çalıştırma izni verirken, diğerlerine hiçbir izin vermez.

3. **Yeni Dosya ve Klasörler İçin Varsayılan Yetkileri Ayarlama:**
   `setfacl` komutu ile `sapb1reports_v2` dizinine eklenen yeni dosya ve klasörler için varsayılan izinleri ayarlayabilirsiniz. Böylece, yeni oluşturulan her öğe otomatik olarak belirlediğiniz izinleri alacaktır:

   sudo setfacl -m u:user:rw /home/user/sapb1reportsV2

   sudo setfacl -d -m u:user:rwx /home/user/sapb1reports_v2
   sudo setfacl -d -m g:user:rwx /home/user/sapb1reports_v2
   ```

   `-d` seçeneği varsayılan izinleri belirtir, `-m` seçeneği izinleri değiştirmek için kullanılır, `u:user:rwx` ve `g:user:rwx` komutları ise "user" kullanıcısına ve grubuna okuma (`r`), yazma (`w`) ve çalıştırma (`x`) izinleri verir.

4. **Doğrulama:**
   İzinleri ve ACL'leri doğrulamak için, klasörde `getfacl` komutunu kullanabilirsiniz:

   
   getfacl /home/user/sapb1reports_v2
   ```

Bu adımlarla "user" kullanıcısına `/home/user/sapb1reports_v2` klasörü altında tam erişim yetkisi verilmiş olacak ve yeni oluşturulan dosya ve klasörlere de aynı yetkiler otomatik olarak uygulanacaktır.


npm run build yetki sorunlari
once yetkiler user uzerine al sonra www-data ya geri ver aksi halde sorun olur
sudo chown -R user:user /var/www/sapb1reportsV2/frontend/build/
sudo chown -R user:user /var/www/sapb1reportsV2/frontend/node_modules/.cache

sudo chown -R www-data:www-data /var/www/sapb1reportsV2/frontend/build/
sudo chown -R www-data:www-data /var/www/sapb1reportsV2/frontend/node_modules/.cache