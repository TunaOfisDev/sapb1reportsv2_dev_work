#### Adım 2: Postman ile Test
Bu yeni endpoint'i test etmek çok basittir:
1.  **Metod:** `POST`
2.  **URL:** `http://192.168.2.170/api/v2/productconfigv2/variants/VARIANT_ID/update-price-from-sap/`
      * `VARIANT_ID` kısmını, fiyatını güncellemek istediğin varyantın ID'si ile değiştir (örneğin: `108`).
3.  **Authorization:** "Bearer Token" sekmesine, geçerli JWT token'ını yapıştır.
4.  **Body:** Herhangi bir body göndermene gerek yok.

Bu isteği gönderdiğinde, sistem SAP'den fiyatı çekip varyantı güncelleyecek ve sana güncellenmiş varyantın tüm bilgilerini geri dönecektir.
### Yöntem 2: Mevcut Admin Action'ını Doğrudan Test Etme (Daha Karmaşık)
Bu yöntem, yeni kod eklemeden mevcut admin aksiyonunu test eder ama daha fazla ayar gerektirir.
#### Adım 1: Tarayıcıdan `csrftoken` ve `sessionid` Al
1.  Chrome'da Django admin paneline giriş yap.
2.  Varyantlar listesi sayfasına git (`.../admin/productconfigv2/variant/`).
3.  `F12` ile Geliştirici Araçları'nı aç ve "Network" sekmesine git.
4.  Sayfayı yenile (`F5`).
5.  Listede ilk çıkan `variant/` isteğine tıkla.
6.  "Headers" sekmesi altında, "Request Headers" bölümüne in ve `Cookie` satırını bul. Buradaki `csrftoken` ve `sessionid` değerlerini kopyala.

#### Adım 2: Postman ile İsteği Oluştur

1.  **Metod:** `POST`
2.  **URL:** `http://192.168.2.170/admin/productconfigv2/variant/` (API URL'i değil, admin sayfasının URL'i)
3.  **Headers:**
      * `Cookie`: `csrftoken=DEĞER; sessionid=DEĞER` (Tarayıcıdan kopyaladığın değerleri yapıştır).
      * `X-CSRFToken`: Sadece `csrftoken` değerini buraya yapıştır.
4.  **Body:**
      * `form-data` sekmesini seç.
      * Aşağıdaki 3 anahtarı ve değerlerini gir:
          * **action**: `update_prices_from_sap`
          * **\_selected\_action**: Güncellemek istediğin varyantın ID'si (örneğin: `108`)
          * **csrfmiddlewaretoken**: `csrftoken` değerini buraya da yapıştır.

Bu isteği gönderdiğinde, Postman admin paneli üzerinden bir form göndermiş gibi davranacak ve aksiyonu tetikleyecektir. Başarılı olursa, seni tekrar admin listeleme sayfasına yönlendiren bir `302 Found` yanıtı alırsın.