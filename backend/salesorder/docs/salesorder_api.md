salesorder api amac
1- satış sipariş analizi için gerekli tüm alanları barındırır
2-Satış sipariş ORDR, RDR1, OITM, OITB, OSLP, OWDD, WDD1 ve OUSR gibi alanların verileirini barındırır
3- satış sipariş detay verilerini barındır. 
4- satış sipariş aşama ve durumlarını barındırır. Açık, kapalı,onay durum,  teslim tarihi yaklaşan gibi
5- özet raporların tamamın zaman dilimleri günlük, haftalık, aylık, çeyrek(quarter) ve yıllık filtreler sunar
6- muhatap bazında zaman dilimlerinde özet satış tutarı sunar
7- satış çalışanı bazında zaman dilimlerinde özet satış tutarı sunar
8- kalem gruplarına göre özet satış tutarı sunar
9- kpi lar sunar toplam net satış tutarı ve indirim yapılan toplam tutar ve kümülatif indirim oranı % sunar
*****************

`SalesOrder` API'sinin amacını ve algoritmasını detaylandıralım:

### `SalesOrder` API Algoritması:

1. **Tüm Alanların Barındırılması:**
   - API, `SalesOrder` modelinde tanımlanan tüm alanları kapsar. 
   - Veriler, ORDR, RDR1, OITM, OITB, OSLP, OWDD, WDD1, OUSR gibi tablolardan toplanan bilgileri içerir.
   - Bu, müşteriler, sipariş numaraları, sipariş tarihleri, teslim tarihleri, ürün kodları, ürün tanımları, fiyatlar, miktarlar, indirimler, onay durumları ve daha fazlasını içerir.

2. **Detay Verilerin Barındırılması:**
   - Her satış siparişi detayı, siparişin tüm yönlerini kapsar.
   - Ürün detayları, sipariş miktarları, fiyatlandırma bilgileri ve siparişin teslimat durumu gibi bilgileri içerir.

3. **Sipariş Aşama ve Durumları:**
   - Açık ve kapalı siparişler, onay durumları ve teslim tarihi yaklaşan siparişler gibi çeşitli sipariş durumları ve aşamalarını takip eder.
   - Kullanıcılar, siparişin mevcut durumunu ve aşamasını görüntüleyebilir ve analiz edebilir.

4. **Zaman Dilimlerine Göre Özet Raporlama:**
   - API, günlük, haftalık, aylık, çeyreklik ve yıllık raporlamalar için filtreleme özellikleri sunar.
   - Kullanıcılar, belirli bir zaman diliminde gerçekleşen satış siparişlerini inceleyebilir.

5. **Muhatap Bazında Satış Analizi:**
   - Her müşteri için belirli zaman dilimlerinde toplam satış tutarını sunar.
   - Bu, müşteriye özgü satış performansını analiz etmek için kullanılabilir.

6. **Satış Çalışanı Bazında Analiz:**
   - Satış personeline göre zaman dilimlerinde toplam satış tutarlarını sunar.
   - Bu, bireysel satış performansını değerlendirmek için kullanılır.

7. **Kalem Gruplarına Göre Satış Analizi:**
   - Ürün veya hizmet kategorilerine göre özet satış tutarlarını sunar.
   - Bu, hangi kategorilerin daha iyi performans gösterdiğini analiz etmek için kullanılabilir.

8. **Performans Göstergeleri (KPI'lar):**
   - Toplam net satış tutarı, indirim yapılan toplam tutar ve kümülatif indirim oranını yüzde olarak sunar.
   - Bu KPI'lar, genel satış performansını ve indirim stratejilerinin etkinliğini değerlendirmek için kullanılabilir.

### API Geliştirmesi için Adımlar:

1. **Endpointlerin Tanımlanması:**
   - CRUD operasyonları için standart RESTful endpoint'ler tanımlayın.
   - Özel sorgular ve filtreleme için ek endpoint'ler tanımlayın.

2. **Sorgu İşlemleri:**
   - Zaman dilimleri, müşteri kodları, satış personeli ve kalem gruplarına göre filtreleme yetenekleri ekleyin.
   - Karmaşık sorgular için Django'nun ORM'ini veya doğrudan SQL sorgularını kullanın.

3. **Veri Serileştirme:**
   - `SalesOrder` modelinden gelen verileri JSON formatına dönüştürmek için Django serileştiricileri (serializers) kullanın.

4. **Performans Optimizasyonu:**
   - Büyük veri setleri için sorgu optimizasyonları yapın.
   - Gerektiğinde pagination ve caching

 mekanizmalarını kullanın.

5. **Frontend Entegrasyonu:**
   - API'nizi React uygulaması ile entegre edin.
   - Kullanıcıların verileri kolayca sorgulayıp analiz edebilmeleri için kullanıcı dostu arayüzler geliştirin.

