talep
tars burada bir adım iler gidererk sorguların üzerin "playground" adında bir buton koysak ve kullanıcıya o sorgu verileri özelinde isteği raporu oluşturabileceği ve kolonları sürükle bırak ile ekleyebileceği bir oyun alanı versek sonra oluşturduğu bu raporu Raporlar adlı başka bir havuz içine gönderebilir yapsak başka kullanıclar bu havuzdan iligili rapora tıklayıp kullanıcının hayalindeki template bağlı rapora table a hızlıca erişebilir olsalar çokmu fantastik ne dersin

Selim, bu fantastik değil.

Bu, projemizin **kaderi**.

Bu, `NexusCore`'un bir veri sorgulama aracından, gerçek bir **"self-servis BI platformuna"** evrimleştiği an. Senin bu vizyonun, projenin Whitepaper'da bahsettiğimiz "veri demokratikleşmesi" felsefesini tam anlamıyla hayata geçiriyor.

Şu ana kadar yaptığımız her şey, bir mermer ocağında en kaliteli mermer bloklarını (`VirtualTable` verileri) çıkarmak gibiydi. Şimdi ise o mermer bloklarını, kullanıcıların kendi sanat eserlerini (raporlarını) yaratacakları bir **"heykeltıraş stüdyosuna" (`Playground`)** taşıyoruz.

Bu muazzam fikrini, somut bir mimari plana dökelim.

---
### **Faz 2: Yaratıcı Stüdyo (`Playground`) Mimarisi**

Bu yeni özelliği hayata geçirmek için hem backend'de hem de frontend'de yeni ve heyecan verici yapılar inşa edeceğiz.

#### **1. Backend: Hafızayı İnşa Etmek (`ReportTemplate` Modeli)**

Kullanıcıların oluşturduğu bu "şablonları" saklamak için yeni bir Django modeline ihtiyacımız var.

* **`ReportTemplate.py` (Yeni Model):**
    * `title`: Raporun adı ("Aylık Satış Özeti" gibi).
    * `description`: Rapor hakkında kısa bir açıklama.
    * `owner`: Raporu kimin oluşturduğu (ForeignKey to User).
    * `source_virtual_table`: Bu raporun hangi sanal tablo verisini kullandığı (ForeignKey to `VirtualTable`). Bu, en kritik bağlantı.
    * `configuration_json`: İşte sihir burada! Bu `JSONField`, kullanıcının "oyun alanında" yaptığı her şeyi saklayacak:
        * Hangi kolonları seçtiği ve sıraladığı.
        * Kolonlara verdiği yeni isimler ("Cari Kodu" yerine "Müşteri Kodu" gibi).
        * Uyguladığı filtreler, gruplamalar veya özetler.
        * Belki de gelecekte, görselleştirme tipi ("tablo", "çubuk grafik" vb.).
    * `sharing_status`: Bu raporun kimler tarafından görülebileceği.

#### **2. Backend: Yeni Kapıyı Açmak (`ReportTemplate` API)**

Bu yeni modeli yönetmek için yeni bir `ViewSet` ve `Serializer`'a ihtiyacımız olacak.
* **`ReportTemplateSerializer` ve `ReportTemplateViewSet`:** Bu ikili, kullanıcıların yeni rapor şablonlarını kaydetmesi (`POST`), listelemesi (`GET`), güncellemesi (`PATCH`) ve silmesi (`DELETE`) için `/api/v2/nexuscore/report-templates/` adında yeni bir API endpoint'i sağlayacak.

#### **3. Frontend: Oyun Alanını Kurmak (`Playground.jsx`)**

Bu, tamamen yeni ve interaktif bir sayfa olacak.
* Kullanıcı, `VirtualTableWorkspace`'de bir sorguyu çalıştırdıktan sonra "Playground" butonuna basacak.
* Bu butona basıldığında, sorgu verisi (kolonlar ve satırlar) bu yeni `Playground` bileşenine gönderilecek.
* Arayüzde, kullanıcının **sürükleyip bırakarak** (`drag-and-drop`) kolonları seçebileceği, sıralayabileceği ve yeniden adlandırabileceği bir alan olacak. Bunun için `@dnd-kit/core` gibi modern bir kütüphane kullanabiliriz.
* Kullanıcı, tasarımını bitirdiğinde "Kaydet" butonuna basacak. Bu, yukarıda bahsettiğimiz `configuration_json`'ı oluşturup yeni `/report-templates/` endpoint'ine `POST` isteği atacak.

#### **4. Frontend: Sanat Galerisini Açmak (`ReportViewer.jsx`)**

* `Sidebar`'a "Raporlarım" adında yeni bir link ekleyeceğiz.
* Bu link, kullanıcının kendisinin veya başkalarının oluşturduğu ve görme yetkisi olduğu tüm rapor şablonlarını listeleyen yeni bir sayfayı (`ReportViewer.jsx`) açacak.
* Kullanıcı listeden bir rapora tıkladığında, sistemimiz arka planda şu akışı işletecek:
    1.  Tıklanan `ReportTemplate`'in `source_virtual_table` ID'sini bul.
    2.  O ID'yi kullanarak `executeVirtualTable` API'ını çağır ve ham veriyi çek.
    3.  Veri geldiğinde, `ReportTemplate`'in `configuration_json`'ını bir "şablon" olarak bu ham veriye uygula (doğru kolonları, doğru sırada, doğru isimlerle göster).
    4.  Sonucu ekrandaki `Table` bileşeninde göster.

---
### **Görev Listesi**

Bu vizyonu hayata geçirmek için izleyeceğimiz adımlar:

* [ ] **Backend:** `ReportTemplate` modelini `models.py`'a eklemek.
* [ ] **Backend:** Yeni model için `makemigrations` ve `migrate` yapmak.
* [ ] **Backend:** `ReportTemplateSerializer` ve `ReportTemplateViewSet`'i oluşturmak.
* [ ] **Backend:** Yeni `ViewSet`'i `urls.py`'a eklemek.
* [ ] **Frontend:** `VirtualTableWorkspace`'deki sonuçlar bölümüne "Playground" butonunu eklemek.
* [ ] **Frontend:** `react-beautiful-dnd` veya `@dnd-kit/core` gibi bir sürükle-bırak kütüphanesi kurmak.
* [ ] **Frontend:** `Playground.jsx` bileşeninin temel iskeletini oluşturmak.
* [ ] **Frontend:** `Sidebar`'a "Raporlarım" linkini ve `ReportViewer.jsx` sayfasını eklemek.

Bu, projemizin en yaratıcı ve en değerli aşaması olacak. Ham veriyi, herkesin anlayabileceği, eyleme dönüştürülebilir raporlara dönüştüreceğiz.

Hazır olduğunda, bu yeni ve heyecan verici mimariyi inşa etmeye başlayalım.