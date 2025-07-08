aksiyonlar

asagida ki islemeleri yapmadan once klasor yetkilerini user a ver `sudo chown -R user:user /var/www/sapb1reportsv2`

1- /home/user/Downloads/orderarchive_db  klasor olustur
2- /home/user/Downloads/orderarchive_db klasor icine uyumsoft siparis xlsx dosyasini sira ile koy
3- backend/orderarchive icinde sanal ortamda python split_excel.py komutu calistir bu komut ana dosyayi parcalara bolecek 10bin satirlik
4- backend/orderarchive/output_chunks icinde yeni parcali xlsx leri kontrol et
5- backend/orderarchive icinde sanal ortamda python load_data.py komutu calistir parcali xlsx dosyalarini iceri alinamsini bekle

6- tabloya tammen silmek icin 
(venv) user@user-Virtual-Machine:/var/www/sapb1reportsv2/backend$  python manage.py delete_invalid_records --all
belli bir order date silmek icin python manage.py delete_invalid_records --order_date=2025-01-01


OrderArchive API'sinin genel yapısını ve amacını açıklayayım:

Bu API, eski ERP sisteminizdeki müşteri sipariş detaylarını modern bir REST API aracılığıyla kullanıcılara sunmak için tasarlanmış. Sistem şu özelliklere sahip:

1. **Veri Yapısı:**
- 26 kolon içeren kapsamlı bir sipariş detay tablosu
- Yaklaşık 553.000 satır veri
- Önemli alanlar: sipariş numarası, tarih, müşteri bilgileri, ürün detayları, fiyatlandırma bilgileri vb.

2. **API Endpoints:**

A) **Ana Liste Endpoint (`/api/v2/orderarchive/`):**
- Sayfalama özelliği (her sayfada 100 kayıt)
- Toplam 5533 sayfa
- Her kayıt için detaylı sipariş bilgisi

B) **Arama Endpoint (`/api/v2/orderarchive/search/`):**
- Minimum 5 karakter ile arama yapılabilir
- Müşteri kodu, müşteri adı, ürün kodu ve ürün açıklamasında arama yapabilme

C) **Yıl Filtresi Endpoint (`/api/v2/orderarchive/year-filter/`):**
- Belirli bir yıla ait siparişleri filtreleme imkanı

3. **Optimizasyonlar:**
- Büyük veri seti için özel sayfalama
- Filtreleme ve sıralama özellikleri
- Verimli veri yükleme mekanizması (chunk'lar halinde)

4. **Veri Yönetimi:**
- Excel dosyalarından veri yükleme desteği
- Hatalı kayıtları temizleme araçları
- Otomatik tarih ve sayısal değer dönüşümleri

Bu API, büyük ölçekli sipariş verilerini yönetmek ve görüntülemek için optimize edilmiş, modern bir arayüz sunuyor.