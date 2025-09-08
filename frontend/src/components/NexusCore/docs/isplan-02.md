Selim, bu, projemizin "Yaratılış Günü". Motoru (backend) inşa ettik; şimdi sıra pilotun oturacağı kokpiti (frontend) tasarlamada.

Qlik Sense hedefimiz için bu, her şeyin birleştiği an. Backend'de yaptığımız stratejik devrimin (yani "aptal" endpoint'ten "dahi" ve agrege eden bir motora geçişin) frontend'deki yansımasını planlayacağız.

En temel değişim şu, Selim: **Frontend artık bir veri *işlemcisi* (processor) değil, bir veri *görüntüleyicisi* (renderer) olacak.** Tüm ağır yük (JOIN'ler, GROUP BY'lar, agregasyonlar) artık bizim güçlü backend'imizde. Bu, React kodumuzu kitlesel olarak basitleştirir, ancak motoru kontrol etmek için yeni arayüzler inşa etmemizi gerektirir.

İşte bu vizyonu hayata geçirecek frontend yol haritamız:

---

### Nexus Core Frontend Yol Haritası (v2.0 - "DataApp Devrimi")

#### Faz 1: "Veri Modeli Editörü" (Yeni Konteyner) Oluşturulması

Bu, Qlik'teki "App" mantığının tam karşılığıdır. Kullanıcıların `VirtualTable` bloklarını birleştirip aralarındaki ilişkileri (JOIN'leri) tanımlayacağı yerdir. Bu, sıfırdan inşa edilecek yepyeni bir arayüzdür.

* **Ana Görevler:**
    1.  **Yeni Sayfa (Container):** `VirtualTableWorkspace` gibi, `frontend/src/components/NexusCore/containers/DataAppWorkspace/` adında yeni bir ana konteyner bileşeni oluştur.
    2.  **Sidebar Güncellemesi:** Bu yeni sayfaya bir link ekle (Örn: "Veri Modelleri").
    3.  **Liste Görünümü:** Bu sayfa, `useDataApps` hook'umuzu kullanarak mevcut tüm Veri Uygulamalarını (`DataApp`) listelemeli. (Liste, başlık, bağlantı adı, sahip ve Eylem butonları [Düzenle/Sil/Yeni Oluştur] içermeli).
    4.  **Yeni/Düzenle Formu (Modal):** Bu, mimarinin kalbidir.
        * **Adım 1 (Genel):** Kullanıcıdan `title`, `description` ve en önemlisi, bu veri modelinin "yaşayacağı" ana **veri bağlantısını** (`DynamicDBConnection`) seçmesi için bir `<Select>` kutusu iste.
        * **Adım 2 (Tablo Seçimi):** Kullanıcı bir bağlantı seçtiği anda, sadece *o bağlantıya ait* olan `VirtualTable` listesini (API'dan filtreleyerek veya `virtualTablesApi.getVirtualTables()` ile çekip filtreleyerek) ona sun. Bir çift-liste (shuttle) veya çoklu seçim kutusu ile bu modele dahil edeceği tabloları seçmesini sağla. (Bu, `DataApp.virtual_tables` M2M alanını doldurur).
        * **Adım 3 (İlişki Editörü):** Bu, Faz 1'in en karmaşık UI parçasıdır.
            * Sayfa, `useAppRelationships` hook'unu kullanarak mevcut ilişkileri listelemeli.
            * "Yeni İlişki Ekle" formu sağlamalıyız:
                * `Sol Tablo`: (Adım 2'de seçilen tablolarla dolu bir `<Select>`)
                * `Sol Kolon`: (Manuel metin girişi - Phase 2'de bunu metadata'dan otomatik tamamlayabiliriz)
                * `Sağ Tablo`: (Yine Adım 2'deki tablolar)
                * `Sağ Kolon`: (Manuel metin girişi)
                * `Join Tipi`: (LEFT JOIN, INNER JOIN seçimi)
            * Bu form, `createRelationship` fonksiyonunu (hook'umuzdan gelen) çağırır. Mevcut ilişkiler listesi de `deleteRelationship` için bir "Sil" butonu barındırmalıdır.

#### Faz 2: "Report Playground" (Rapor Oluşturma) Arayüzünün Yeniden Kablolanması

Mevcut rapor oluşturma sihirbazımız (`ReportPlayground`) artık tek bir `VirtualTable`'a değil, bir `DataApp`'e dayanmak zorunda.

* **Ana Görevler:**
    1.  **Akış Değişikliği:** Rapor oluşturma akışı artık "Hangi Sanal Tablo?" diye değil, "**Hangi Veri Modelini (DataApp) kullanmak istiyorsun?**" diye sormalı.
    2.  **Mevcut Kolonların Yüklenmesi (`AvailableColumns.jsx`):**
        * Playground yüklendiğinde, seçilen `DataApp` ID'si ile `dataAppsApi.getDataAppById(appId)` çağrısı yapmalı.
        * Gelen `DataApp` nesnesi, içinde ilişkili tüm `VirtualTable` listesini (ve onların `column_metadata`'larını) barındırmalı. (Eğer Serializer'ımız bunu yapmıyorsa, `DataAppSerializer`'ı `VirtualTableSerializer`'ı nested (iç içe) kullanacak şekilde güncellemeliyiz ki metadata'yı alabilelim).
        * Playground UI'ı, bu *tüm* tablolardaki *tüm* kolonları **tek bir düz listede** birleştirerek "Kullanılabilir Kolonlar" panelini doldurmalıdır.
    3.  **Kaydetme İşlemi:** Kullanıcı sürükle-bırak işlemini bitirip "Kaydet" dediğinde, artık `useReportTemplatesApi.createTemplate` fonksiyonunu şu payload (veri yükü) ile çağıracak: `{ title: '...', configuration_json: {pivot_config: ...}, source_data_app_id: currentAppId }`. (Bu, zaten güncellediğimiz API ve hook'larla tam uyumludur).

#### Faz 3: "Report Viewer" (Rapor Görüntüleyici) Arayüzünün Basitleştirilmesi

Bu, stratejik devrimimizin en güzel meyvesidir. Raporu görüntüleyen bileşenin işi artık %90 daha kolay.

* **Ana Görevler:**
    1.  **Mevcut Akış:** `ReportList.jsx` bir raporu listeler. Kullanıcı "Görüntüle" butonuna tıklar.
    2.  **Yeni Veri Çekme Mantığı (`ReportViewer/index.jsx` veya `ReportCanvas.jsx`):**
        * Bu bileşen yüklendiğinde, artık `useEffect` içinde **sadece bir** API çağrısı yapacak: `reportTemplatesApi.executeReportTemplate(reportId)`.
        * Bunun için `const { data, loading, error, request: executeReport } = useApi(reportTemplatesApi.executeReportTemplate);` hook'unu kullanacak.
    3.  **Yeni Veri (Payload):** Dönen `data` nesnesi artık `{ configuration: ..., data: {raw_data} }` DEĞİLDİR. Dönen veri doğrudan şudur: `{ success: true, columns: ["Bayi", "Ürün Grubu", "Adet_SUM"], rows: [["Bayi A", "Grup 1", 150], ["Bayi B", "Grup 2", 200]] }`.
    4.  **Render (Görüntüleme):** Frontend'deki pivot veya tablo bileşeninin artık hesaplama, gruplama veya agregasyon yapmasına **gerek yok**. Tek görevi, `data.columns`'u alıp `<th>` (başlık) olarak, `data.rows`'u alıp `<tr><td>` (satır) olarak basmaktır. İşlem yükü sıfıra indi.

#### Faz 4: Yönetim ve İyileştirmeler (Governance)

* `VirtualTableWorkspace` arayüzüne (liste) bir "Kullanıldığı Veri Modelleri" sütunu ekle (bu, `VirtualTable.data_apps` ters ilişkisinden gelir).
* Tüm veri yükleme (`load...`) fonksiyonlarını `useEffect(..., [])` içine alarak bileşenler yüklendiğinde otomatik çalışmalarını sağla.
* Tüm CRUD işlemlerinden sonra gelen bildirimler için (`useNotifications`) `addNotification`'ı agresifçe kullan.