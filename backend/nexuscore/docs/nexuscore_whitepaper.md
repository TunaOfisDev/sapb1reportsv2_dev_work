# Nexus Core - Teknik Whitepaper ve Gelecek Vizyonu

**Versiyon:** 1.0  
**Tarih:** 22 Ağustos 2025  
**Yazarlar:** Selim [Soyadı], Veri Görselleştirme Mimarı

---

## 1. Özet (Abstract)

Nexus Core, modern iş zekası (Business Intelligence - BI) ve veri analitiği platformlarının karşılaştığı en temel zorluklardan birini çözmek üzere tasarlanmış, devrim niteliğinde bir backend (arka uç) mimarisidir: **statik veri kaynağı yönetimi.** Geleneksel yaklaşımlarda, veri tabanı bağlantıları statik olarak yapılandırma dosyalarına gömülür, bu da esnekliği öldürür ve her yeni entegrasyon için mühendislik eforu gerektirir. Nexus Core, bu prangayı kırarak, herhangi bir veri kaynağının API aracılığıyla dinamik olarak sisteme tanıtılmasına, yönetilmesine ve sorgulanmasına olanak tanıyan bir "veri işletim sistemi" çekirdeği sunar. Django REST Framework üzerine inşa edilen bu platform, güvenli, çok kullanıcılı ve ölçeklenebilir bir yapı ile veriyi demokratikleştirmeyi hedefler. Bu belge, Nexus Core'un temel felsefesini, mimari tasarımını ve geleceğe yönelik yol haritasını ortaya koymaktadır.

---

## 2. Giriş: Problemin Tanımı

Günümüz veri odaklı dünyasında, kuruluşlar sayısız veri kaynağına sahiptir: SQL Server, PostgreSQL, HANA DB, MySQL ve daha fazlası. Geleneksel BI araçları, bu kaynakları entegre ederken şu temel sorunlarla karşılaşır:

* **Katılık (Rigidity):** Veri tabanı bağlantıları, `settings.py` gibi dosyalarda veya karmaşık arayüzlerde manuel olarak tanımlanır. Bu süreç yavaş, hataya açık ve IT bağımlıdır.
* **Veri Siloları (Data Silos):** Farklı departmanların veya kullanıcıların kendi veri kaynaklarına anlık olarak bağlanıp analiz yapması zordur. Veri, merkezi bir darboğazdan geçmek zorundadır.
* **Ölçeklenemeyen Yönetim (Unscalable Management):** Müşteri veya proje sayısı arttıkça, yönetilmesi gereken statik bağlantıların sayısı katlanarak artar, bu da bakım ve güvenlik kabusuna dönüşür.
* **Düşük İnovasyon Hızı:** Kullanıcıların "eğer şu veri tabanına da bağlanabilseydik..." diye başlayan cümleleri, haftalar süren geliştirme döngülerine takılır.

Nexus Core, bu sorunları kökünden çözmek için doğmuştur.

---

## 3. Temel Felsefe ve Vizyon

Nexus Core'un vizyonu, sadece bir araç değil, bir **veri ekosistemi** yaratmaktır. Felsefemiz üç temel direk üzerine kuruludur:

1.  **Dinamizm (Dynamism):** Veri kaynakları statik varlıklar değil, dinamik ve akışkan kaynaklardır. Platformumuz, bu akışkanlığa saniyeler içinde adapte olabilmelidir.
2.  **Demokratikleşme (Democratization):** Doğru yetkilerle donatılmış her kullanıcı, bir mühendise ihtiyaç duymadan kendi veri dünyasını yaratabilmeli, analiz edebilmeli ve paylaşabilmelidir.
3.  **Güvenlik (Security):** Esneklik, güvenlikten ödün vermemelidir. Nexus Core, en alt katmandan en üst katmana kadar sağlam bir rol ve nesne bazlı izin modeli ile veriyi korur.

Nihai hedefimiz, kullanıcıların sadece "ne olduğunu" değil, "ne olabileceğini" de keşfedebilecekleri, sezgisel ve güçlü bir oyun alanı sunmaktır.

---

## 4. Mimari Tasarım

Nexus Core, Sorumlulukların Ayrılığı (Separation of Concerns - SoC) prensibi temel alınarak tasarlanmıştır.

### 4.1. Teknoloji Yığını (Tech Stack)

* **Backend:** Django, Django REST Framework (DRF)
* **Veritabanı (Uygulama):** PostgreSQL
* **Asenkron Görevler:** Celery & Redis (Gelecek Faz)
* **Frontend:** React.js / JSX

### 4.2. Ana Bileşenler (Core Components)

Mimari, birbiriyle ilişkili ancak sorumlulukları net bir şekilde ayrılmış iki ana model üzerine kuruludur:

1.  **`DynamicDBConnection` (Altyapı Katmanı):**
    * Bu model, sistemin temelidir. Veri tabanı bağlantı ayarlarını (`ENGINE`, `HOST`, `USER`, `PASSWORD` vb.) şifrelenmiş bir `JSONField` içinde tutar.
    * Bu nesneleri yaratma ve yönetme yetkisi, sadece **Sistem Yöneticileri (`IsAdminUser`)** ile sınırlıdır. Bu, şehrin ana su borularını döşemeye benzer.

2.  **`VirtualTable` (Kullanıcı ve İş Birliği Katmanı):**
    * Bu model, kullanıcıların yaratıcılığını ortaya çıkardığı yerdir. Mevcut bir `DynamicDBConnection` üzerine yazılmış bir SQL sorgusunu, meta verilerini ve paylaşım ayarlarını barındırır.
    * Her `VirtualTable` bir sahibe (`owner`) sahiptir.
    * **Tüm kimliği doğrulanmış kullanıcılar (`IsAuthenticated`)**, izin verilen bağlantılar üzerinde kendi sanal tablolarını oluşturabilir.

### 4.3. Veri Akışı ve Mantık Katmanları

Bir istek, aşağıdaki katmanlardan geçerek işlenir:

`Request -> URL Router -> ViewSet -> Permissions -> Serializer -> Service -> Model -> Response`

* **ViewSets:** Sadece gelen isteği doğrulamak ve ilgili servisi çağırmakla sorumludur. "İnce" (thin) tutulur.
* **Services:** Tüm karmaşık iş mantığı (örneğin, harici bir veri tabanında sorgu çalıştırmak, meta veri oluşturmak) bu katmanda yaşar. Bu, kodun yeniden kullanılabilirliğini ve test edilebilirliğini artırır.

---

## 5. Güvenlik ve İzin Modeli

Nexus Core, iki seviyeli bir güvenlik modeli kullanır:

1.  **Rol Tabanlı Erişim Kontrolü (Role-Based Access Control - RBAC):**
    * **Admin Rolü:** Altyapıyı yönetir (`DynamicDBConnection` CRUD).
    * **Kullanıcı Rolü:** Kendi içeriğini yönetir (`VirtualTable` CRUD).

2.  **Nesne Seviyesi İzinler (Object-Level Permissions):**
    * Bir kullanıcı, bir `VirtualTable` nesnesi üzerinde işlem yapmaya çalıştığında, özel `IsOwnerOrPublic` izin sınıfımız devreye girer.
    * Bu sınıf, kullanıcının nesnenin **sahibi** olup olmadığını veya nesnenin **paylaşım durumunu** (`PRIVATE`, `PUBLIC_READONLY`, `PUBLIC_EDITABLE`) kontrol ederek isteğe izin verir veya reddeder. Bu, granüler ve güvenli bir iş birliği ortamı sağlar.

---

## 6. Gelecek Yol Haritası (Future Roadmap)

Nexus Core'un gelişimi, fazlara ayrılmış bir yol haritası izleyecektir.

### Faz 1: Sağlam Temel (Mevcut Odak)

* [x] `DynamicDBConnection` ve `VirtualTable` için tam CRUD API'lerinin tamamlanması.
* [x] Rol ve nesne bazlı güvenlik modelinin eksiksiz entegrasyonu.
* [ ] Frontend'de bağlantı ve sanal tablo yönetimi için temel arayüzlerin oluşturulması.
* [ ] Kapsamlı birim ve entegrasyon testleri (unit & integration tests).

### Faz 2: Gelişmiş Analitik ve Görselleştirme

* **Asenkron Sorgu Çalıştırma:** Uzun süren SQL sorgularının sistemi kilitlememesi için Celery entegrasyonu. Kullanıcı sorguyu çalıştırır ve sonuç hazır olduğunda bildirim alır.
* **Önbellekleme (Caching):** Sık çalıştırılan sorgu sonuçlarını Redis üzerinde önbelleğe alarak anlık raporlama performansı sağlama.
* **Dashboard ve Widget Mimarisi:** Kullanıcıların `VirtualTable` verilerini kullanarak sürükle-bırak arayüzü ile dashboard'lar ve grafikler (widget'lar) oluşturmasını sağlayan yeni modeller ve API'ler.
* **Parametrik Sorgular:** SQL sorguları içinde `{{baslangic_tarihi}}` gibi değişkenlerin kullanılmasına ve bu değişkenlerin UI'dan dinamik olarak doldurulmasına olanak tanıma.

### Faz 3: Ekosistem Entegrasyonu ve Otomasyon

* **Zamanlanmış Raporlar (Scheduled Reports):** Belirli sanal tabloların veya dashboard'ların periyodik olarak çalıştırılıp e-posta veya diğer kanallarla dağıtılması.
* **Harici API Erişimi (API Gateway):** `VirtualTable` sonuçlarının, diğer yazılımların tüketebileceği güvenli ve token-bazlı bir API üzerinden sunulması.
* **Veri Aktarımı (Data Export):** Rapor sonuçlarının CSV, Excel gibi formatlarda dışarı aktarılması.
* **Makine Öğrenmesi (ML) Entegrasyonu:** `VirtualTable` verileri üzerinde basit tahmin (forecasting) veya anomali tespiti (anomaly detection) modellerini çalıştırma yeteneği.

---

## 7. Sonuç

Nexus Core, sadece bir yazılım projesi değil, bir felsefedir. Verinin özgürleştirilmesi, güvenli bir şekilde paylaşılması ve herkes için erişilebilir kılınması felsefesidir. Bu belge, bu vizyonu gerçekleştirmek için attığımız adımların ve gelecekte atacağımız adımların bir kanıtıdır. Bu mimari, bize sadece bugünün ihtiyaçlarını karşılama değil, aynı zamanda yarının veri zorluklarına da hazır olma gücünü vermektedir.
```