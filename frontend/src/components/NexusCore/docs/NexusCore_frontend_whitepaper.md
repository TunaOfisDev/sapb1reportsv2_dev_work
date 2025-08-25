# Nexus Core - Frontend Mimarisi ve Kullanıcı Deneyimi Whitepaper

**Versiyon:** 1.0  
**Tarih:** 25 Ağustos 2025  
**Yazarlar:** Selim [Soyadı], Veri Görselleştirme Mimarı

---

## 1. Özet (Abstract)

Nexus Core Frontend, backend'de inşa edilen güçlü ve dinamik veri yönetimi altyapısını, son kullanıcı için sezgisel, hızlı ve güçlü bir arayüze dönüştürmeyi hedefler. Bu mimari, React.js üzerine kurulu olup, **iki ana kullanıcı rolünü** temel alır: Altyapıyı yöneten **Yöneticiler (Admins)** ve veriyi analiz edip sorgulayan **Kullanıcılar (Users)**. Her rol için özel olarak tasarlanmış, temiz ve amaca yönelik bir çalışma alanı sunulacaktır. Modüler bileşen yapısı, yeniden kullanılabilir hook'lar ve merkezi bir stil yönetimi ile hem geliştirici deneyimini (Developer Experience) hem de kullanıcı deneyimini (User Experience - UX) en üst seviyeye çıkarmak temel amaçtır. Bu belge, ortaya çıkacak olan kullanıcı arayüzünün (UI) felsefesini, ana sayfalarını ve kullanıcı akışlarını detaylandırmaktadır.

---

## 2. Tasarım Felsefesi ve UI/UX Hedefleri

Kullanıcı arayüzümüz, backend'in "her şey mümkün" felsefesini, "her şey basit" deneyimiyle birleştirecektir.

* **Modülerlik ve Tutarlılık:** Arayüz, `Button`, `Card`, `Modal` gibi temel yapı taşlarından oluşur. `styles/_variables.scss` dosyasında tanımlanan merkezi tasarım dili (renkler, boşluklar vb.) sayesinde tüm uygulama boyunca görsel bir bütünlük sağlanır.
* **Kullanıcı Odaklılık:** Karmaşık işlemler (yeni bir veri kaynağı eklemek, SQL sorgusu yazmak) basit ve anlaşılır formlar aracılığıyla gerçekleştirilir. Arayüz daima sade, odaklanmış ve amaca yönelik olacaktır.
* **Reaktif ve Bilgilendirici:** Kullanıcı yaptığı her işlemin sonucunu anında görmelidir. `useApi` hook'u ile yönetilen **Yükleniyor (Loading)** durumları, `useNotifications` hook'u ile gösterilen **Başarı** ve **Hata** bildirimleri, kullanıcıyı asla belirsizlik içinde bırakmaz.

---

## 3. Ana Sayfalar ve Kullanıcı Akışları

Nexus Core arayüzü, kullanıcının rolüne göre iki ana çalışma alanına ayrılır.

### 3.1. Yönetici Kokpiti: `ConnectionManager`

Bu arayüz, sadece sistem yöneticilerinin erişebileceği, projenin altyapısının yönetildiği teknik kontrol odasıdır.

* **Amaç:** Yöneticilerin, sisteme yeni veri tabanı bağlantıları eklemesini, mevcut olanları yönetmesini ve test etmesini sağlamak.
* **Ana Bileşenler:** `Card`, `Button`, `Modal`, `ConnectionList`, `ConnectionForm`.
* **Görsel Konsept:** Temiz, liste tabanlı bir ayarlar sayfası. 
* **Kullanıcı Akışı:**
    1.  Yönetici, Nexus Core ana ekranına geldiğinde bu sayfayı görür.
    2.  Büyük bir `Card` bileşeni içinde, mevcut tüm veri tabanı bağlantıları (`DynamicDBConnection`) listelenir.
    3.  Her bir bağlantının yanında başlığı, veri tabanı türü (`db_type` için ikonlarımızla birlikte) ve aktif olup olmadığını gösteren bir durum göstergesi bulunur.
    4.  Her bağlantı satırının sağında "Test Et", "Düzenle" ve "Sil" aksiyonlarını içeren `Button`'lar yer alır.
    5.  `Card`'ın başlığında (`headerActions` prop'u ile) "Yeni Bağlantı Ekle" butonu bulunur.
    6.  Bu butona tıklandığında, ekranın üzerinde bir `Modal` açılır. Bu modal, `ConnectionForm` bileşenini içerir.
    7.  Yönetici, formda **Başlık**, **Veri Tabanı Türü** ve en önemlisi **JSON Yapılandırması** alanlarını doldurur.
    8.  "Kaydet" butonuna basıldığında, `createConnection` API çağrısı yapılır. Bu çağrı, backend'de bağlantıyı test eder.
    9.  İşlem başarılı olursa, kullanıcıya "Bağlantı başarıyla oluşturuldu!" bildirimi (`Notification`) gösterilir, modal kapanır ve arkadaki bağlantı listesi otomatik olarak yenilenir. Hata olursa, form üzerinde veya bildirim olarak hata mesajı gösterilir.

### 3.2. Kullanıcı Oyun Alanı: `VirtualTableWorkspace`

Bu arayüz, standart kullanıcıların veri ile etkileşime girdiği, sorgular oluşturup sonuçlarını analiz ettiği yaratıcı ve dinamik bir çalışma alanıdır.

* **Amaç:** Kullanıcıların, yöneticiler tarafından eklenmiş veri kaynakları üzerinde kendi SQL sorgularını (`VirtualTable`) oluşturmasını, kaydetmesini, paylaşmasını, çalıştırmasını ve sonuçlarını bir tabloda görmesini sağlamak.
* **Ana Bileşenler:** `VirtualTableList`, `QueryEditorModal`, `DataTable`.
* **Görsel Konsept:** İki ana bölümden oluşan bir çalışma alanı. Üst bölümde kullanıcının kayıtlı sorgu listesi, alt bölümde ise seçili sorgunun veri sonuçlarını gösteren büyük bir data grid'i. 
* **Kullanıcı Akışı:**
    1.  Kullanıcı bu sayfaya geldiğinde, `VirtualTableList` bileşeni ile karşılanır. Bu liste, kullanıcının sahip olduğu veya kendisine paylaşılan tüm sanal tabloları bir `Card` içinde listeler.
    2.  Her bir sanal tablonun yanında başlığı ve paylaşım durumu (ikonlarımızla birlikte: `lock.svg` -> Özel, `eye.svg` -> Salt Okunur vb.) görünür.
    3.  Listenin başında "Yeni Sorgu Oluştur" butonu bulunur. Bu butona basıldığında `QueryEditorModal` açılır.
    4.  Kullanıcı bu modalda; sorgusuna bir **Başlık** verir, izin verilen **Veri Kaynaklarından** birini seçer, **SQL Sorgusunu** yazar ve **Paylaşım Ayarını** seçer.
    5.  "Oluştur" butonuna basıldığında, backend sorguyu ve meta veriyi kaydeder. Modal kapanır, kullanıcıya başarı bildirimi gösterilir ve liste yenilenir.
    6.  Kullanıcı, listedeki herhangi bir sorgunun yanındaki **"Çalıştır"** (`play-circle.svg` ikonlu) butonuna tıklar.
    7.  Bu eylem, `executeVirtualTable` API çağrısını tetikler. Arayüzde, sayfanın alt bölümündeki `DataTable` bileşeninde bir **Yükleniyor...** (`Spinner`) animasyonu belirir.
    8.  API'den veri (kolonlar ve satırlar) başarıyla döndüğünde, `Spinner` kaybolur ve veri, `DataTable` bileşeni içinde temiz bir tablo olarak gösterilir. Tablonun üzerinde, "Sonuçlar: Aylık Satış Raporu" gibi bir başlık belirir.
    9.  Eğer sorgu çalışırken bir hata oluşursa, `DataTable` alanında bir hata mesajı gösterilir.

---

## 4. Sonuç

Nexus Core Frontend mimarisi, güçlü backend altyapısını son kullanıcı için somut ve değerli bir deneyime dönüştürmek üzere tasarlanmıştır. Rol bazlı, temiz ve reaktif arayüzler sayesinde, hem yöneticiler altyapıyı zahmetsizce yönetebilecek hem de kullanıcılar veri analizinin ve keşfinin keyfini çıkarabilecektir. Bu whitepaper, bu vizyonu hayata geçirmek için izleyeceğimiz yol haritasını ve mimari kararları belgelemektedir.