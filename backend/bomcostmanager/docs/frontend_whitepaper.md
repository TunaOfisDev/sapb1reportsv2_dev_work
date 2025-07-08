Aşağıda, **BOM Cost Manager** projesi için hazırlanmış React tabanlı frontend whitepaper’ını bulabilirsiniz. Bu whitepaper, proje mimarisini, dosya yapısını, temel bileşenleri ve işlev akışını kapsamlı şekilde açıklamaktadır.

---

# BOM Cost Manager React Frontend Whitepaper

## 1. Proje Amacı

**BOM Cost Manager**, SAP Business One ERP’nin ham madde (BOM) maliyetlerini detaylı ve esnek biçimde analiz edebilmek için geliştirilen bir uygulamadır. Bu sistemde:
- SAP Business One’dan çekilen ürün ağacı (BOM) verileri, öncelikle Django REST API aracılığıyla PostgreSQL veritabanına kaydedilir.
- Frontend tarafında, React kullanılarak, kullanıcıların ürün listesinden (mamul listesi) seçim yapması ve ilgili ürün ağacının detaylı maliyet analizini görmesi sağlanır.
- Kullanıcı, BOM yapısındaki ham madde fiyatlarını override edebilir ve ayrıca, ek olarak; işçilik, genel üretim gideri, lisans ve komisyon gibi faktörleri (opsiyonel) uygulayarak nihai maliyet hesaplamasını gerçekleştirebilir.
- Versiyonlama sayesinde, her hesaplama senaryosu kayıt altına alınır ve ileride karşılaştırma yapılabilir.

Bu yapı, özellikle yüksek enflasyonlu ortamlarda, maliyet planlaması ve raporlama açısından son derece kritik bilgiler sunar.

---

## 2. Genel Mimari

### 2.1. Uygulama Akışı

1. **Ürün Listesi ve Seçim:**  
   - Kullanıcı, SAP Business One’dan çekilen ürün ağacına (mamul listesi) ait verileri görür.  
   - Ürün listesi, React tabanlı dinamik bir tablo (Reactable gibi) kullanılarak sunulur.  
   - Kullanıcı, listeden bir ürün (mamul) seçtiğinde, o ürünün BOM (patlatılmış ürün ağacı) detaylarını görmek üzere ilgili sayfaya yönlendirilir.

2. **BOM Maliyet Görünümü:**  
   - Seçilen ürün için, patlatılmış BOM yapısı (ham maddeler, yarım mamuller, vs.) iki ana tabloda sunulur:
     - **Statik Bilgiler Tablosu:** Ürünün temel özellikleri ve SAP’den çekilen statik veriler.
     - **Dinamik (Editable) BOM Tablosu:** Kullanıcının override değerler girebileceği, ham madde fiyatlarını düzenleyebileceği ve ek faktörleri (işçilik, genel gider, lisans, komisyon) uygulayabileceği tablo.
   - Hesaplama mekanizması, her satırdaki override fiyatları ve çarpanların uygulanmasıyla, bileşen bazında ve toplamda yeni maliyeti (updated cost) hesaplar.

3. **Versiyonlama ve Kayıt:**  
   - Kullanıcı, hesaplanan yeni maliyeti kaydederek bir “senaryo” (BOMRecord) oluşturabilir.
   - Bu sayede geçmiş hesaplamalar saklanır ve ileride farklı senaryolar karşılaştırılabilir.

---

## 3. Dosya Yapısı

Aşağıda, projenin **frontend** tarafı için oluşturulan dosya yapısı ve içerikleri özetlenmiştir:

```
frontend/src/components/BomCostManager/
├── containers/                      # Sayfa kapsayıcı bileşenleri (Container Components)
│   ├── BomCostTableContainer.js     # BOM maliyet tablosunu yöneten kapsayıcı
│   ├── ProductListContainer.js      # Ürün listesini yöneten kapsayıcı
│   └── VersionHistoryContainer.js   # Versiyon geçmişini yöneten kapsayıcı
├── css/                             # Stil dosyaları
│   ├── BomCostManager.css           # BOM Cost Manager’a ait temel stiller
│   └── Responsive.css               # Responsive (mobil uyumlu) düzenlemeler
├── hooks/                           # Özel React hook’ları
│   ├── useFetchBomCost.js           # BOM maliyet verilerini çekme ve hesaplama için hook
│   └── useProductSelection.js       # Ürün seçimi ve yönetimi için hook
├── redux/                           # Redux state yönetimi için yapı
│   ├── actions/                     # Redux action tanımları
│   │   ├── bomCostActions.js        # BOM maliyet işlemleri için action’lar
│   │   └── productActions.js         # Ürün işlemleri için action’lar
│   ├── reducers/                    # Redux reducer’ları
│   │   ├── bomCostReducer.js        # BOM maliyet verilerini yöneten reducer
│   │   ├── productReducer.js         # Ürün verilerini yöneten reducer
│   │   └── rootReducer.js            # Tüm reducer’ları birleştiren root reducer
│   └── bomcoststore.js              # Redux store yapılandırması
├── services/                        # Frontend servisleri: API çağrıları (Örneğin, axios wrappers)
├── utils/                           # Yardımcı fonksiyonlar
│   ├── calculateCost.js             # Maliyet hesaplama işlemleri
│   └── formatDate.js                # Tarih formatlama yardımcı fonksiyonları
└── views/                           # Sunum (presentational) bileşenler
    ├── BomCostEditModal.js          # BOM bileşen override düzenleme modal penceresi
    ├── BomCostView.js               # BOM maliyet analiz ekranı (ana rapor görünümü)
    └── ProductListView.js           # Ürün listesi görünümü
```

### Açıklamalar

- **Containers:**  
  Uygulamanın veri yönetimi ve state ile etkileşiminden sorumlu kapsayıcı bileşenlerdir. Örneğin, `BomCostTableContainer.js` BOM tablosunun yüklenmesi, filtreleme, sıralama gibi işlevleri kontrol eder.

- **CSS:**  
  Uygulamanın stil ve responsive (mobil uyumlu) düzenlemelerini içerir.

- **Hooks:**  
  Özel hook’lar; örneğin, `useFetchBomCost` BOM maliyet verilerini çekme, hesaplama ve override güncellemelerini yönetir. `useProductSelection` ise ürün listesi ve seçim işlemlerini yöneten hook’tur.

- **Redux:**  
  Uygulamanın global state yönetimi için Redux kullanılmıştır. Action ve reducer’lar, BOM maliyet verileri, ürün listesi, filtreleme, sıralama, vs. gibi state’leri kontrol eder. `bomcoststore.js` store yapılandırmasını içerir.

- **Services:**  
  Frontend tarafında, API çağrılarını gerçekleştiren modüller bulunur. Örneğin, `bcm_bomCostApi.js` ve `bcm_productApi.js` dosyaları, Django REST API ile iletişim kurarak veriyi alır ve gönderir.

- **Utils:**  
  Yardımcı fonksiyonlar; hesaplama, tarih formatlama gibi işlemleri gerçekleştirir.

- **Views:**  
  Kullanıcıya sunulan arayüz bileşenleri. Örneğin, `BomCostView.js` BOM maliyet analiz raporunu, `BomCostEditModal.js` ise düzenleme formunu barındırır.

---

## 4. Ana Özellikler ve İşlevsellik

### 4.1. Ürün Listesi ve Seçim

- **ProductListView.js:**  
  - Ürün listesini, filtreleme, arama ve sıralama özellikleriyle kullanıcıya sunar.
  - Kullanıcı bir ürünü seçtiğinde, seçili ürün detayları Redux üzerinden güncellenir ve BOM analizi ekranına yönlendirilir.

### 4.2. BOM Maliyet Analizi

- **BomCostView.js:**  
  - Seçilen ürünün BOM bileşenlerini tablolarda gösterir.
  - Dinamik tablo, Reactable gibi hafif ve esnek bir tablo kütüphanesi ile oluşturulabilir. Bu tablo, satır bazında editable alanlar (ör. yeni fiyat, çarpanlar) içerir.
  - Kullanıcı, ham madde override fiyatlarını girdikten sonra, ek olarak işçilik, genel üretim gideri, lisans ve komisyon çarpanlarını girerek nihai maliyeti (updated_cost) hesaplatabilir.
  - Hesaplama fonksiyonları `calculateCost.js` üzerinden çalışır.

### 4.3. Versiyonlama

- **VersionHistoryContainer.js ve ilgili view:**  
  - Kullanıcı, yaptığı override ve hesaplamaları “senaryo” olarak kaydeder.
  - Bu kayıtlar, `BOMRecord` modeli ile ilişkilendirilir ve geçmiş hesaplamalar arasında karşılaştırma yapmaya imkan tanır.

### 4.4. API Entegrasyonu

- **API Servisleri:**  
  - `bcm_bomCostApi.js` ve `bcm_productApi.js`, Django REST API ile etkileşim kurarak gerekli verileri alır, gönderir ve günceller.
  - Bu servisler, Axios gibi bir HTTP istemci kullanarak backend API endpoint’lerine istek yapar.

### 4.5. State Yönetimi

- **Redux:**  
  - Global state yönetimi, ürün verileri, BOM bileşenleri, filtre, sıralama ve override bilgileri gibi verileri yönetmek için kullanılır.
  - Actions, Reducers ve Store, tüm veri akışını merkezi olarak kontrol eder.

### 4.6. Özel Hook’lar

- **useFetchBomCost:**  
  - BOM bileşenlerini çekme, hesaplama ve override güncellemeleri için özelleştirilmiş hook.
- **useProductSelection:**  
  - Ürün seçimi, arama, filtreleme ve sıralama işlemlerini yönetir.

---

## 5. Kullanıcı Deneyimi ve Esneklik

- **Editable Tablolar:**  
  - Kullanıcılar, Reactable (veya benzeri) kütüphane kullanılarak oluşturulan tablolar üzerinde ham madde fiyatlarını, çarpanları kolayca düzenleyebilir.
- **Dinamik Hesaplama:**  
  - Girilen override değerlerine ve çarpanlara göre anlık maliyet hesaplaması yapılır.
- **Versiyon Kaydı:**  
  - Her hesaplama senaryosu (override ve çarpan değerleri) kayıt altına alınır. Bu sayede geçmiş senaryoları karşılaştırma imkanı sağlanır.
- **Responsive Tasarım:**  
  - CSS dosyaları ve responsive düzenlemeler sayesinde uygulama, masaüstü ve mobil cihazlarda uyumlu çalışır.

---

## 6. Gelecek Geliştirme Potansiyeli

- **Ek Özellikler:**  
  - Kullanıcı, isteğe bağlı olarak ek çarpanlar (ör. lisans ve komisyon) tanımlayabilir.
  - Daha gelişmiş raporlama ve grafik gösterimleri eklenebilir.
- **Performans Optimizasyonları:**  
  - Redux ve custom hook’lar ile veri akışı optimize edilebilir, özellikle büyük veri setlerinde performans artırılabilir.
- **Kullanıcı Yetkilendirmesi:**  
  - Role dayalı yetkilendirme ile sadece belirli kullanıcıların override yapması veya kayıt oluşturması sağlanabilir.
- **API Geliştirmeleri:**  
  - Backend tarafıyla entegre çalışan daha kapsamlı hata yönetimi ve geri bildirim mekanizmaları eklenebilir.

---

## 7. Sonuç

**BOM Cost Manager** React frontend, SAP Business One’dan çekilen verilerin kullanıcılara esnek ve interaktif bir şekilde sunulmasını sağlar.  
- **Ürün Listesi:** Kullanıcılar, basit arayüz üzerinden ürünleri seçerek BOM maliyet detaylarına ulaşır.  
- **BOM Analizi:** Patlatılmış ürün ağacındaki her bir kalemin maliyetini, override değerleri ve ek çarpanlarla (işçilik, genel üretim gideri, lisans, komisyon) yeniden hesaplayabilir.  
- **Versiyonlama:** Hesaplama senaryoları kayıt altına alınarak, gelecekte karşılaştırma ve analiz yapılabilir.  
- **Modüler Yapı:** Frontend, containers, hooks, Redux, services, utils ve views gibi ayrık modüller sayesinde esnek, ölçeklenebilir ve bakım kolaylığı sunan bir mimariye sahiptir.

Bu whitepaper, projenin React frontend mimarisinin temel prensiplerini ve dosya yapılandırmasını özetlemektedir. Uygulamanın karmaşık maliyet hesaplama sürecini kullanıcı dostu ve etkileşimli bir hale getirmek için modern React tekniklerini, state yönetimini ve API entegrasyonunu etkin şekilde kullanıyoruz.

> **Not:** Projede kullanılan Reactable kütüphanesi, küçük ölçekli ve esnek tablo çözümleri sunarak, dinamik veri düzenleme, filtreleme ve arama özelliklerini kolayca entegre etmemize olanak tanımaktadır. Bu sayede, hem verilerin okunabilirliği artırılıyor hem de kullanıcı deneyimi geliştiriliyor.

--- 

Bu whitepaper, BOM Cost Manager'ın frontend tarafı için temel mimari yaklaşımı, dosya yapısını ve iş akışını detaylandırır. Projenin ilerleyen aşamalarında, yeni özellikler eklenerek kullanıcı deneyimi ve performans daha da optimize edilebilir.