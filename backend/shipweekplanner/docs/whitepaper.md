### Proje: ShipWeekPlanner API

#### Proje Tanımı
**Başlık:** Haftalık Sevk Planı API  
**Amaç:** Kullanıcılara, yılın haftalarını gösteren bir takvim arayüzü sunarak, seçilen hafta için düzenlenebilir bir datatable üzerinde sevk planlarını görüntüleme, düzenleme ve analiz imkanı sağlamak. Ayrıca planlanan tarih ile sevk tarihi arasındaki farkları analiz ederek kalite kontrol süreçlerine katkı sağlamak.

#### Fonksiyonel Gereksinimler
1. **Takvim Görünümü:** Yılın haftalarını gösteren ve haftalara tıklayarak sevk planlarını düzenleyebileceğiniz bir arayüz.
2. **Veri Girişi ve Düzenleme:** Her hafta için sevk bilgileri, sipariş numarası, müşteri adı, sipariş tarihi, sevk tarihi, satış temsilcisi, sevk açıklamaları ve notlar ile düzenlenebilir.
3. **Veri Aktarımı:** SevkTarih'i boş olan siparişleri bir sonraki haftaya kopyalama.
4. **Kalite Kontrol Analizi:** Planlanan tarih ile gerçekleşen sevk tarihi arasındaki farkı ölçerek kalite kontrol raporlaması oluşturma.

#### Teknolojik Yığın
- **Backend:**
  - Django REST Framework: API yönetimi için.
  - PostgreSQL: Veritabanı.
  - Django Models: Sevk planları ve kalite kontrol için veritabanı modelleri.
  
- **Frontend:**
  - React.js: Kullanıcı arayüzü.
  - Redux: Durum yönetimi.
  - Material-UI: Arayüz bileşenleri.

#### Model Yapısı
- **ShipmentOrder**: 
  - **order_number:** Sipariş numarası (benzersiz)
  - **customer_name:** Müşteri adı
  - **order_date:** Sipariş tarihi
  - **planned_dates:** Planlanan tarihler (JSON listesi)
  - **planned_date_mirror:** Kullanıcı tarafından girilen tarih (tek seferlik)
  - **planned_date_real:** Planlanan tarihlerden sonuncusu (gerçek planlanan tarih)
  - **shipment_date:** Sevk tarihi
  - **sales_person:** Satış temsilcisi
  - **shipment_details:** Sevk açıklamaları
  - **shipment_notes:** Sevk notları
  - **order_status:** Açık veya Kapalı

#### Model API Endpoints
- **GET `/shipmentorders/`:** Tüm sevk planlarını getirir.
- **POST `/shipmentorders/`:** Yeni bir sevk planı ekler.
- **PUT `/shipmentorders/{id}/`:** Belirli bir sevk planını günceller.
- **DELETE `/shipmentorders/{id}/`:** Belirli bir sevk planını siler.
- **GET `/weekly/`:** Haftalık sevk planlarını getirir.
- **POST `/copy-next-week/`:** SevkTarih'i boş olan siparişleri bir sonraki haftaya kopyalar.

#### API Örnek Yanıt
```json
[
    {
        "id": 2,
        "order_number": "3311",
        "customer_name": "İSTANBUL AVM",
        "order_date": "2024-10-18",
        "planned_dates": [
            "2024-10-30",
            "2024-11-20",
            "2024-11-26"
        ],
        "planned_date_mirror": null,
        "planned_date_real": "2024-11-26",
        "shipment_date": "2024-10-18",
        "sales_person": "CATAK",
        "shipment_details": "SEVK AÇIKLALMALARI2",
        "shipment_notes": "SEVK NOTLARI 2",
        "created_at": "2024-10-18T11:06:50.097840Z",
        "updated_at": "2024-10-18T12:56:47.879757Z"
    }
]
```

#### Kalite Kontrol Analizi
Planlanan tarihler ile sevk tarihleri arasındaki farkları ölçerek sevkiyatların zamanında yapılıp yapılmadığını kontrol edebilirsiniz. Analiz aşamaları:

1. **Planlanan ve Sevk Tarihi Karşılaştırması:**
   - **planned_date_real** ile **shipment_date** arasında fark hesaplanır.
   - Gecikme olup olmadığı kontrol edilir ve raporlanır.
   
2. **Raporlama ve Görselleştirme:**
   - Raporlama modülleriyle gecikmeleri, performansları izlemek.
   - Gecikmelerin düzenli bir şekilde analiz edilerek operasyonel süreçlerin iyileştirilmesi.

#### Kalite Kontrol Önerileri
1. **Zamanında Sevk Analizi:**
   - Gerçekleşen sevk tarihi ile son planlanan tarih (planned_date_real) arasındaki fark ölçülerek raporlanır.
   - Örneğin, pozitif farklar gecikmeleri, negatif farklar erken sevkleri gösterebilir.

2. **Operasyonel İyileştirme:**
   - Gecikmeler düzenli olarak analiz edilerek operasyon süreçleri yeniden optimize edilebilir.

#### Kullanıcı Arayüzü Tasarımı
- **Takvim Görünümü:** Yılın haftalarını gösteren ve sevk planlarının takibini kolaylaştıran interaktif bir takvim.
- **Düzenlenebilir Tablo:** Seçilen haftadaki sevk siparişlerini düzenleyebileceğiniz bir tablo.
- **"Copy and Save Next Weekend" Butonu:** SevkTarih'i boş olan siparişleri bir sonraki haftaya kopyalayabilen fonksiyonel bir buton.

#### Güvenlik
- Kimlik doğrulama JWT tabanlı olacak ve kullanıcı yetkilendirme yapılacaktır.
- Veriler HTTPS üzerinden güvenli bir şekilde aktarılacaktır.

#### Geliştirme Planı
1. **Backend API'lerin Geliştirilmesi:** Django REST Framework ile API'nin oluşturulması.
2. **Frontend ile Entegrasyon:** React.js ile kullanıcı arayüzünün inşa edilmesi.
3. **Test ve Dağıtım:** Birim testleri, entegrasyon testleri ve kalite kontrol süreçleri.

#### Dağıtım
- Docker konteynerleri kullanarak bulut platformlarına dağıtım.
- AWS, Google Cloud veya Azure gibi bulut hizmetleri üzerinde ölçeklenebilir bir yapı.

Bu whitepaper, ShipWeekPlanner projesinin her aşamasını özetliyor ve gelecekteki kalite kontrol süreçlerine yönelik altyapıyı da içeriyor.











************************
***************************
Bu projede yapılacaklar ve teknik gereksinimleri ayrıntılı olarak belirleyelim. Projeniz için bir whitepaper oluştururken önce genel bir taslak çıkartacağız:

### Proje Tanımı
- **Başlık:** Haftalık Sevk Planı API
- **Amaç:** Kullanıcıya, yılın haftalarını gösteren bir takvim arayüzü sunarak, seçilen hafta için düzenlenebilir bir datatable üzerinde sevk planlarını görüntüleme ve düzenleme imkanı sağlamak.

### Fonksiyonel Gereksinimler
1. **Takvim Görünümü:** Kullanıcılara yılın haftalarını gösteren interaktif bir takvim.
2. **Veri Girişi ve Düzenleme:** Seçilen hafta için sevk bilgilerinin düzenlenebileceği bir datatable.
3. **Veri Aktarımı:** SevkTarih'i boş olan siparişleri sonraki haftaya kopyalama özelliği.

### Teknolojik Yığın
- **Backend:**
  - Django REST Framework: API servisleri için.
  - Model: Siparişler, sevk bilgileri ve kullanıcı bilgileri.
  - Veritabanı: PostgreSQL.
- **Frontend:**
  - React.js: Kullanıcı arayüzü için.
  - Redux: Durum yönetimi için.
  - Material-UI: Arayüz bileşenleri.

### API Endpoints
- `GET /weeks/`: Yılın haftalarını listele.
- `GET /shipments/{week}/`: Belirli bir haftadaki sevk bilgilerini getir.
- `POST /shipments/{week}/`: Belirli bir haftaya yeni bir sevk bilgisi ekle.
- `PUT /shipments/{week}/{id}/`: Belirli bir haftadaki mevcut sevk bilgisini güncelle.
- `POST /shipments/copy/{week}/`: Seçilen haftadaki boş `SevkTarih` alanına sahip verileri sonraki haftaya kopyala.

### Güvenlik
- Kimlik doğrulama ve yetkilendirme: JWT tabanlı kimlik doğrulama.
- Veri güvenliği ve gizliliği: HTTPS ile şifrelenmiş veri transferi.

### Kullanıcı Arayüzü Tasarımı
- **Takvim Görünümü:** Yılın haftalarını gösteren interaktif bir takvim.
- **Düzenlenebilir Tablo:** Seçilen hafta için düzenlenebilir veri tablosu.
- **Fonksiyonel Butonlar:** Verileri sonraki haftaya kopyalamak için "Copy and Save Next Weekend" butonu.

### Geliştirme ve Dağıtım Planı
- Geliştirme süreci: İki aşamada planlanır, ilk olarak backend API'ler, ardından frontend uygulaması.
- Test süreçleri: Birim testleri, entegrasyon testleri ve kullanıcı kabul testleri.
- Dağıtım: Docker konteynerleri üzerinden AWS veya benzeri bir cloud hizmeti üzerinde.

Bu whitepaper taslağı üzerinden ilerleyerek, projenin detaylarını daha da netleştirebiliriz. Özellikle API ve veritabanı modelleri üzerinde daha fazla ayrıntıya girebiliriz. Bu taslağa göre bir ilerleme planı çıkarabilir ve projenizi adım adım hayata geçirebiliriz.


ornek tablo haftalik sevk plani
SiparisNo	MuhatapAd	SiparisTarih	SevkTarih	Satici	SevkAciklamalari	SevkNotlar
3310	FORD OTOSAN	3.09.2024	14.10.2024	YBACACI	ESKİŞEHİR UFUK 	3 masa 2 keson
3311	FORD OTOSAN	4.09.2024	15.10.2024	YBACACI	ESKİŞEHİR UFUK 	4 masa 2 keson
3312	FORD OTOSAN	5.09.2024		YBACACI	ESKİŞEHİR UFUK 	5 masa 2 keson
3313	FORD OTOSAN	15.09.2024		YBACACI	ESKİŞEHİR UFUK 	6 masa 2 keson



 Planlanan tarih ile sevk tarihi arasındaki farkları kullanarak kalite kontrol süreçlerini analiz edebilirsiniz. Bu, sevk işlemlerinin zamanlamasını takip etmek ve planlama süreçlerinin ne kadar doğru olduğunu ölçmek için oldukça faydalı olacaktır.

Bu farkları analiz ederek:

    Sevkiyatların zamanında yapılıp yapılmadığını kontrol edebilirsiniz.
    Sevkiyat gecikmelerini analiz ederek, operasyonel süreçleri iyileştirme fırsatları bulabilirsiniz.
    Kalite kontrol raporları oluşturarak performansı düzenli olarak izleyebilirsiniz.

Bir sonraki adımda, bu farkları ölçmek için örneğin:

    Gerçekleşen sevk tarihi ile planlanan tarih arasındaki farkı hesaplayarak gecikmeleri tespit edebiliriz.
    Raporlama ve görselleştirme araçlarıyla bu analizleri yönetebilirsiniz.