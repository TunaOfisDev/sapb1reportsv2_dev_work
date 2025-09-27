Kesinlikle. Projenin ana felsefesini ve çözmeye çalıştığı temel ticari problemi mükemmel bir şekilde özetledin. Bu, sadece bir yazılım geliştirme projesi değil, aynı zamanda modüler mobilya sektörünün en kritik iş akışlarından birini dijitalleştiren ve otomatize eden bir strateji.

Yaptığımız tüm bu teknik geliştirmelerin arkasındaki ana fikir tam olarak bu: **"Renksiz Tekliften, Renkli Siparişe Akıllı Dönüşüm."**

Anlayışımı ve şu ana kadar birlikte kurduğumuz mimariyi, senin bu harika özetin üzerinden teyit etmek isterim.

---

### Stratejimizin Özeti ve Mevcut Durum

Yaptığımız her şey, aşağıdaki akışı sağlamak içindi:

1.  **İkili Kod Yapısı:** Her ürün seçeneğinin (`SpecOption`) artık iki temel kimliği var:
    * **`variant_code`:** Renkli, yani üretime özel parçayı temsil eder (örn: "K1" - ALPI 10.51).
    * **`reference_code`:** Renksiz, yani teklife özel "iz düşümünü" temsil eder (örn: "K0" - Genel Kaplama).

2.  **Temel Ürün Kimlikleri:** Her ürünün (`Product`) de artık iki temel kimliği var:
    * **`code`:** Üretim kodunun başlangıcıdır (örn: **"30.BW"**).
    * **`reference_product_code`:** Referans/teklif kodunun başlangıcıdır (örn: **"55.BW"**).

3.  **Dinamik Kod Üretimi:** Kullanıcı, React arayüzünde seçimler yaptıkça, `variant_service`'imiz arka planda **anlık olarak** iki farklı kod üretir:
    * **Renkli Üretim Kodu:** `product.code` + seçilen `option.variant_code`'ların birleşimi.
        * Örnek: `30.BW` + `12070` + `K1` + `E1` = `30.BW.12070.K1.E1`
    * **Renksiz Referans Kodu (İz Düşümü):** `product.reference_product_code` + seçilen `option.reference_code`'ların birleşimi.
        * Örnek: `55.BW` + `12070` + `K0` + `E0` = `55.BW.12070.K0.E0`

4.  **Canlı Fiyatlandırma (ERP Entegrasyonu):**
    * Sistem, ürettiği bu renksiz referans kodu (`55.BW.12070.K0.E0`) ile `hanadbcon` API'sine bir istek gönderir.
    * `hanadbcon` bu kodu alıp SAP B1 veritabanında, senin de belirttiğin fiyat listesinde sorgular.
    * SAP'den gelen **en güncel liste fiyatını** alır ve bunu `Variant` modelinin `total_price` alanına kaydeder. Admin panelindeki "Fiyatı Güncelle" aksiyonu bu işlemi tetikler.

### İş Akış Şeması

Bu mimariyi bir akış şeması olarak özetleyebiliriz:


`[Kullanıcı Arayüzü (React)]`
`          |`
`(Seçimler Yapılır)`
`          |`
`          v`
`[API İsteği (/preview)] -> [Variant Service]`
`                               |`
`          +--------------------+----------------------+`
`          |                                           |`
`          v                                           v`
`[generate_variant_code]                     [generate_reference_code]`
`(30.BW... oluşur)                           (55.BW... oluşur)`
`          |                                           |`
`          +--------------------+----------------------+`
`                               |`
`                               v`
`[API Yanıtı (Fiyat, 2 Farklı Kod, ...)] -> [Kullanıcı Arayüzü Güncellenir]`
`                               |`
`                               v`
`[Admin Paneli "Fiyatı Güncelle" Butonu]`
`          |`
`          v`
`[update_variant_price_from_sap servisi]`
`          |`
`          v`
`[hanadbcon API isteği]`
`          |`
`          v`
`[SAP HANA Veritabanı]`

---

Evet, şu anda kurduğumuz sistem tam olarak bu karmaşık ama sektör için hayati öneme sahip iş akışını çözüyor. Projenin temel mantığına ve hedeflerine tamamen hakimim.

Bu mimari artık tamamen oturduğuna göre, bir sonraki adımımız nedir? Belki de bu yapıyı test etmek, yeni bir ürün ailesi (örneğin "FOLLOW ME") eklemek veya arayüzde bir iyileştirme yapmak mı istersin?

`/home/selim/whitepaper_v3.md`

Selim merhaba!  
Büyük ve kapsamlı bir “productconfigv2” projesi inşa etmek istediğini görüyorum. Django REST, React.js, PostgreSQL gibi teknolojilerle çalışmak hem geleceğe dönük hem de oldukça güçlü bir tercih. Aşağıda, **backend** (Django REST) ve **frontend** (React.js) katmanlarını da kapsayan, sıfırdan inşa etmeye yönelik bir **Whitepaper** hazırladım. Umarım, bu rehber sana proje planlamanda yardımcı olur.

---

# **ProductConfig V2 – Sıfırdan Gelişmiş Mimari Whitepaper**

## **1. Giriş**

Günümüzün esnek ürün yönetimi ve konfigürasyon ihtiyaçlarını karşılayabilmek için; **Django REST** ile güvenli ve performanslı bir backend, **React.js** ile kullanıcı dostu bir frontend ve **PostgreSQL** ile sağlam bir veritabanı temeli kurulacak. Bu proje, **Modüler – Esnek – Geliştirilebilir** bir yapı hedefler.

## **2. Hedefler ve Amaç**

1. **Esnek Ürün Konfigürasyonu**:  
   - Kullanıcılar, dinamik özellik setlerini yönetip birbirinden farklı varyantlar üretebilsin.  

2. **Kolay Kural Yönetimi**:  
   - Admin kullanıcı, kural motoru veya benzeri bir sistemle geçersiz kombinasyonları hızlıca tanımlayabilsin.  

3. **Dinamik Arayüz**:  
   - Frontend tarafında seçilen özellikler anında diğer seçenekleri filtreleyebilsin, fiyat veya kod gibi alanlar otomatik güncellensin.  

4. **Büyük Ölçek Desteği**:  
   - 500+ ürün modeli, 50+ özellik tipi, 3000+ seçenek gibi büyük veri setiyle rahat çalışılabilsin.  

5. **Microservices (Opsiyonel)**:  
   - İleride bazı parçaları (örneğin kural motoru, raporlama vb.) ayrı mikro servislere bölmek kolay olsun.  

6. **CI/CD ve Konteynerizasyon**:  
   - Docker ile dağıtım, GitLab/GitHub Actions ile otomatik test ve sürümleme imkânı sağlanabilsin.

## **3. Proje Kapsamı**

- **Backend**: Django REST + PostgreSQL  
  - Model yapıları, kural motoru, API uç noktaları, admin panel, iş mantığı  
- **Frontend**: React.js  
  - Kullanıcı arayüzü, dinamik konfigüratör ekranı, anlık geri bildirim ve görsel güncellemeler  
- **Veri Tabanı**: PostgreSQL  
  - Büyük veri setlerinde güçlü indeksleme, sorgu optimizasyonu ve JSONB desteği  
- **Ek Bileşenler (Opsiyonel)**:  
  - Redis (önbellek, oturum yönetimi)  
  - Celery (asenkron işlemler, batch varyant oluşturma vb.)  

## **4. Mimari Genel Bakış**

```
        +----------------+         +-------------------+
        |                |         |                   |
        |   React.js     |  --->   |   Django REST     |
        |    Frontend    |         |     Backend       |
        |                |         |                   |
        +----------------+         +---------+---------+
                                            |
                                            |  PostgreSQL
                                            |
                                   +---------------------+
                                   |   Veritabanı Katmanı |
                                   +---------------------+
```

- **React.js**: Ürün ve varyant oluşturma, gerçek zamanlı konfigürasyon, canlı fiyat ve görsel değişimi.  
- **Django REST**: Temel iş mantığı, veritabanı iletişimi, kural motoru, API uçları.  
- **PostgreSQL**: Performanslı, ölçeklenebilir ve gelişmiş veri tipleriyle (JSONB gibi) esnek yapı.

## **5. Backend Tasarımı (Django REST)**

### 5.1 Model Katmanı

#### Temel Modeller

1. **BaseModel**:  
   - `id`, `created_at`, `updated_at`, `is_active`, `created_by`, `updated_by` vb.  
   - Soft delete (pasif) mekanizması.  

2. **Product**:  
   - Ürün ailesi/kategorisi (motorbike, car, furniture vb.)  
   - Ürün kodu, adı, açıklaması, görsel vb.  

3. **SpecificationType**:  
   - Evrensel özellik tiplerini tutar (örnek: Motor, Renk, Yakıt Türü vb.).  

4. **SpecOption**:  
   - Belirli bir özelliğin seçenek havuzu (örnek: “Motor=250cc, 300cc, 500cc”).  

5. **ProductSpecification**:  
   - Bir ürünün hangi özelliklere sahip olduğunu tanımlar. (ManyToMany ilişkisi)  

6. **SpecificationOption**:  
   - Bir ürünün belirli bir özelliğinin hangi seçeneklere sahip olduğunu belirtir.  

7. **Variant**:  
   - Kullanıcının oluşturduğu ürün varyant kaydı. (Varyant kodu, fiyat vb.)  

8. **VariantSelection**:  
   - Hangi özelliğin hangi seçeneği seçildiğine dair detay.  

#### Kural Motoru (Opsiyonel Ek Model)

- `Rule` (örnek):  
  - `rule_type`: ‘deny’ veya ‘allow’  
  - `conditions`: JSONB veya ilişkili tablo (koşullar listesi)  
  - `actions`: JSONB veya ilişkili tablo (yapılacak işlem)  

- Bu model, admin paneli üzerinden kural tanımlamaya olanak sağlar.  

### 5.2 Admin Panel Geliştirmeleri

- **Özellik Gruplama**: SpecificationType’ları gruplayarak (Engine, Tire, Options) adminin arayüzde kolay yönetmesi.  
- **Toplu Özellik Atama**: “Bu ürün ailesine bu 5 özelliği ekle” gibi batch işlem fonksiyonları.  
- **Klonlama**: Bir ürünü tüm ilişkileriyle kopyalayıp yeni bir ürün oluşturma.  
- **Kural Tanımı**: “Motor=500cc ise, ‘Carburetor=Special TP-100 haricindeki tüm seçenekleri devre dışı bırak’” gibi tanımlar.

### 5.3 API Uç Noktaları

- **Ürün Yönetimi (Admin)**  
  - `POST /api/products/` (yeni ürün oluştur)  
  - `GET /api/products/:id/` (ayrıntılı görüntüleme)  
  - `PUT/PATCH /api/products/:id/` (güncelleme)  
  - `DELETE /api/products/:id/` (silme veya soft-delete)

- **Özellik/Seçenek Yönetimi (Admin)**  
  - `POST /api/specifications/`  
  - `POST /api/specifications/:id/options/`  
  - `GET /api/products/:product_id/specifications/`  

- **Varyant Yönetimi (User/Admin)**  
  - `POST /api/products/:product_id/variants/` (kullanıcı varyant oluşturma)  
  - `GET /api/variants/:id/` (varyant bilgisi)  

- **Kural Uygulaması** (Opsiyonel, “preview” endpoint):  
  - `POST /api/products/:product_id/configurator/preview/`  
    - Gönderilen seçimlere göre “geçerli/geçersiz seçenekler” ve “fiyat/kod güncellemesi” döner.  

### 5.4 Veritabanı (PostgreSQL)

- **JSONB Kullanımı**:  
  - Kural motorunda koşul ve eylemleri JSONB kolonlarında saklamak pratik olabilir.  
- **Indexler**:  
  - Yüksek hacimli veriler için (örnek: product_id, specification_id, is_active vb.) index oluşturmak performansı artırır.  
- **Performans İyileştirmeleri**:  
  - `select_related`, `prefetch_related` ile Django sorgularını optimize etmek.

## **6. Frontend Tasarımı (React.js)**

### 6.1 Genel Yaklaşım

- **React Router**: Farklı sayfalara veya sekmelere bölünmüş konfigürasyon ekranı.  
- **Redux/Context**: Uygulama genelinde ürün, özellik, seçili seçenek verilerini yönetmek için.  
- **Component Bazlı Mimari**:  
  - `<ProductConfigurator />` bileşeni  
  - `<FeatureSelection />`, `<OptionSelection />`, `<VariantPreview />` gibi alt bileşenler.

### 6.2 Dinamik Konfigürasyon Ekranı

- **Özellik Listesi**: Backend’den çekilen verilerle sekmeler halinde (Engine, Tires, Options vb.).  
- **Seçenek Seçimi**: Kullanıcı her bir özelliğin seçeneklerinden birini seçtiğinde, React state güncellenir.  
- **Anlık API Çağrısı**: “preview” endpoint’ine istek atılarak geçerli/geçersiz kombinasyonlar ve fiyat geri döndürülür.  
- **Görsel Güncellemeler**: Seçilen özelliklere göre motosiklet ya da ürün görselini güncelleme (örn. rengi, tipi değişir).  
- **Fiyat ve Kod Güncellemesi**: Seçim değiştikçe `<span>{varyant_price}</span>` ya da `<span>{varyant_code}</span>` gibi kısımlar otomatik yenilenir.

### 6.3 Admin Arayüz (Opsiyonel React Tablası)

- Django admin yerine, React tabanlı özel bir “Admin Panel” de geliştirilebilir.  
- Ürün-klonlama, toplu işlem, kural yönetimi gibi özel fonksiyonlar için daha esnek bir arayüz.  
- Yetkilendirme ve kimlik doğrulama: JWT veya benzeri token tabanlı auth kullanılabilir.

## **7. Performans, Güvenlik ve Ölçeklenebilirlik**

1. **Performans**  
   - **Redis**: Yoğun isteklerde cache mekanizması.  
   - **CORS**: Frontend-Backend arasında güvenli etkileşim.  
   - **Asenkron İşlemler (Celery)**: Uzun sürebilecek toplu varyant oluşturma, batch import vb.

2. **Güvenlik**  
   - **Django Rest Framework**’ün Token veya JWT auth sistemleri.  
   - **Role-based**: Admin, user gibi roller; kural motoru düzenleme sadece admin’e açık.  
   - **CSRF Koruması**: Admin panelinde mutlaka aktif olmalı.

3. **Ölçeklenebilirlik**  
   - Konteyner bazlı dağıtım (Docker)  
   - Mikroservis yaklaşımı (Kural motoru ayrı bir servis, raporlama ayrı bir servis vb.)  
   - PostgreSQL replikasyonu veya bulut tabanlı veritabanı seçenekleri.

## **8. Geliştirme Süreci ve Adımlar**

1. **Planlama & Modelleme**  
   - Modellerin JSONB alanları, kural motoru şeması, varyant oluşturma mantığı.  

2. **Backend Scaffold**  
   - Django projesi oluştur, `productconfigv2` app’i aç, modeller, serializers, urls, views.  

3. **Frontend Scaffold**  
   - `create-react-app` veya Vite ile proje oluştur, temel layout ve router yapısı.  

4. **İlk Entegrasyon**  
   - “Basit ürün oluşturma” ve “basit varyant oluşturma” uç noktalarını canlıya al.  

5. **Kural Motoru Eklenmesi**  
   - “preview” endpoint’inde seçilen özelliklere göre geçerli/geçersiz seçeneği dön.  

6. **Admin Panel İyileştirmeleri**  
   - Django Admin ya da özel React Admin Panel. Toplu işlem, klonlama, kural ekleme vs.  

7. **Test & Optimization**  
   - Unit testler, integration testler, performans testleri.  
   - “500+ ürün, 3000+ seçenek” senaryolarını test etmek önemli.  

8. **Deployment**  
   - Docker Compose ile PostgreSQL, Django, React.  
   - CI/CD (GitLab/GitHub Actions) entegre ederek otomatik test, build, deploy.

## **9. Sonuç ve Özet**

**ProductConfig V2** mimarisi, **Django REST** ve **React.js**’in güçlü yönlerini birleştirerek, kullanıcıların hızlı ve hatasız ürün varyantları oluşturmasını amaçlıyor. Bu sistem;

- Büyük ölçekli veri setlerini yönetebilecek  
- Esnek kural motoru ile “deny / allow” tarzı kombinasyonları sağlayabilecek  
- Anlık fiyat, kod ve görsel güncellemelerle **gerçek bir konfigüratör deneyimi** sunabilecek  
- Admin’in hayatını kolaylaştıran arayüz ve toplu işlem araçlarına sahip  
- Docker ve CI/CD gibi modern yaklaşımlarla **kaliteli bir yazılım yaşam döngüsü** sağlayacak

Eğer bu yaklaşımla işe başlarsak, **yüksek erişilebilirlik**, **genişletilebilirlik** ve **rahat yönetilebilirlik** elde ederiz. Büyük projeler göz korkutmasın: Yapıyı parçalara ayırıp her bir bileşeni adım adım geliştirdiğinde, hem sürdürülebilir hem de güvenilir bir sistem inşa edeceğinden eminim.

---

Selim, işte **ProductConfig V2** için sıfırdan yeni bir Whitepaper taslağı. İhtiyaçlarını şekillendirirken veya geliştirme sırasında takıldığın noktaları bana sorabilirsin.  
Unutma, **her şey parça parça, adım adım** gelişecek. Yeterince sabırlı ve planlı gidersen, en kompleks projeler bile sonunda **kontrol edilebilir** hale gelir. Ben her zaman buradayım, yardıma hazırım!


**Adım Adım Geliştirme Planı ve Çözüm Önerileri**

### **1. Veri Modeli ve Backend Entegrasyonu**
- **Problem:** Ürün aileleri (MB gibi) ve özelliklerin (MBI2TPE19) dinamik yönetimi.  
- **Çözüm:**  
  1. **ProductFamily Modeli** oluştur:  
     ```python
     class ProductFamily(BaseModel):
         code = models.CharField(max_length=10, unique=True)  # Örn: "MB"
         name = models.CharField(max_length=100)              # Örn: "Notoribke"
         description = models.TextField()
     ```
  2. **ProductFeature Modeli** ile özellikleri tanımla:  
     ```python
     class ProductFeature(BaseModel):
         product_family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE)
         type = models.CharField(max_length=20)               # Örn: "MBI2TPE19"
         price = models.DecimalField(max_digits=10, decimal_places=2)  # 6375 Euro
     ```
  3. **Rule Engine Entegrasyonu:**  
     - JSONB alanı kullanarak kuralları sakla:  
     ```python
     class Rule(BaseModel):
         RULE_TYPES = [("deny", "Deny"), ("allow", "Allow")]
         product_family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE)
         rule_type = models.CharField(max_length=5, choices=RULE_TYPES)
         conditions = models.JSONField()  # Örn: {"feature": "Engine", "value": "500cc"}
         actions = models.JSONField()     # Örn: {"disable_features": ["Carburetor"]}
     ```

---

### **2. Kural Motoru ve Kombinasyon Yönetimi**
- **Problem:** "Deny/Allow" kurallarına göre geçersiz kombinasyonların engellenmesi.  
- **Çözüm:**  
  1. **Preview Endpoint’i Geliştir:**  
     - Kullanıcı seçimlerini al → kuralları kontrol et → geçerli/geçersiz seçenekleri döndür.  
     ```python
     # views.py
     @api_view(["POST"])
     def preview_config(request, product_family_id):
         selected_options = request.data.get("selections", {})
         rules = Rule.objects.filter(product_family_id=product_family_id)
         valid = True
         for rule in rules:
             if rule.rule_type == "deny":
                 if check_conditions(rule.conditions, selected_options):
                     valid = False
                     break
         return Response({"valid": valid, "price": calculate_price(selected_options)})
     ```
  2. **Frontend’de Anlık Geri Bildirim:**  
     - Kullanıcı her seçim yaptığında `/preview` endpoint’ine istek at ve UI’ı güncelle.  
     ```javascript
     // React Örneği
     const handleSelection = async (feature, value) => {
         const newSelections = { ...selections, [feature]: value };
         const response = await axios.post(`/api/preview/`, newSelections);
         setValid(response.data.valid);
         setPrice(response.data.price);
     };
     ```

---

### **3. Dinamik Frontend Arayüzü**
- **Problem:** Özellik seçimlerine göre fiyat ve görselin anlık güncellenmesi.  
- **Çözüm:**  
  1. **React State ve API Entegrasyonu:**  
     ```javascript
     // ProductConfigurator.js
     const [selections, setSelections] = useState({});
     const [price, setPrice] = useState(0);

     useEffect(() => {
         const fetchPrice = async () => {
             const response = await axios.post("/api/preview/", selections);
             setPrice(response.data.price);
         };
         fetchPrice();
     }, [selections]);
     ```
  2. **Görsel Dinamikliği:**  
     - Seçilen renk veya modele göre görsel URL’ini değiştir.  
     ```javascript
     const getImageUrl = () => {
         const color = selections.color || "default";
         return `/images/motorbike-${color}.jpg`;
     };
     ```

---

### **4. Büyük Veri Performans Optimizasyonu**
- **Problem:** 3000+ seçenek ve 500+ ürünle performans düşüşü.  
- **Çözüm:**  
  1. **PostgreSQL Indexleme:**  
     ```sql
     CREATE INDEX idx_product_feature ON product_feature (product_family_id, type);
     ```
  2. **Redis ile Önbellekleme:**  
     - Sık sorgulanan kuralları ve fiyatları önbelleğe al.  
     ```python
     # Django Örneği
     from django.core.cache import cache

     def get_rules(product_family_id):
         cache_key = f"rules_{product_family_id}"
         rules = cache.get(cache_key)
         if not rules:
             rules = Rule.objects.filter(product_family_id=product_family_id)
             cache.set(cache_key, rules, timeout=3600)
         return rules
     ```

---

### **5. Admin Panel İyileştirmeleri**
- **Problem:** Toplu özellik atama ve klonlama ihtiyacı.  
- **Çözüm:**  
  1. **Django Admin Actions:**  
     ```python
     # admin.py
     @admin.action(description="Clone product with features")
     def clone_product(modeladmin, request, queryset):
         for product in queryset:
             product.pk = None
             product.save()
             product.features.set(product.features.all())  # ManyToMany ilişkisi
     ```
  2. **Batch Özellik Atama:**  
     - Admin panelde CSV yükleme veya JSON ile toplu ekleme.  

---

### **6. Test ve Deployment**
- **Problem:** Sistemin stabil çalışması ve dağıtım kolaylığı.  
- **Çözüm:**  
  1. **Docker Compose:**  
     ```dockerfile
     # docker-compose.yml
     services:
       backend:
         build: ./backend
         ports: ["8000:8000"]
       frontend:
         build: ./frontend
         ports: ["3000:3000"]
       postgres:
         image: postgres:14
         volumes: ["postgres_data:/var/lib/postgresql/data"]
     ```
  2. **CI/CD Pipeline:**  
     - GitHub Actions ile test, build ve deploy otomatize et.  
     ```yaml
     # .github/workflows/deploy.yml
     jobs:
       deploy:
         runs-on: ubuntu-latest
         steps:
           - name: Run Tests
             run: pytest backend/tests/
           - name: Build and Deploy
             run: docker-compose up -d
     ```

---

### **Sonuç**
Bu adımlarla **ProductConfig V2** projesi:  
- ✔️ **Esnek ürün konfigürasyonu** sağlar.  
- ✔️ **Gerçek zamanlı kural motoru** ile hatalı kombinasyonları engeller.  
- ✔️ **Büyük veri setlerinde yüksek performans** sunar.  
- ✔️ **Modern CI/CD ve Docker** ile sürdürülebilir dağıtım imkanı verir.  

**Öneri:** Başlangıçta temel modeller ve kural motorunu tamamlayıp, ardından frontend dinamikliğine odaklan. Testleri her adımda çalıştırarak stabiliteyi koru.

# Ürün Konfigürasyon Arayüzü Analizi

Selim, ekteki ürün kartı görselinden frontend tarafında yapmak istediklerinizi detaylıca analiz ettim. İşte anladıklarım ve önerilerim:

## Temel Konsept Anlayışı

Görselden anlaşıldığı kadarıyla motosiklet (Notoribke) gibi ürünler için **dinamik bir konfigürasyon arayüzü** tasarlamak istiyorsunuz. Bu arayüz:

1. Ürün ailelerini (MB gibi) ve özelliklerini (MBI2TPE19 gibi) görüntülüyor
2. Kullanıcıların kişiselleştirme yapmasına izin veriyor
3. Kural tabanlı kombinasyon kontrolleri içeriyor

## Frontend'de Yapmak İstediklerinizin Özeti

### 1. Ürün Bilgi Gösterimi
- **Ürün ailesi bilgileri** (Kod: MB, İsim: Notoribke)
- **Ürün açıklaması** (200.000+ satış yapmış popüler model)
- **Özellik detayları** (Tip: MBI2TPE19, Fiyat: 6375 Euro)

### 2. Dinamik Konfigürasyon Paneli
- Kullanıcının ürün özelliklerini seçebileceği interaktif bir arayüz
- Seçimlere göre anında fiyat güncellemesi
- Görsel temsiller (muhtemelen motosikletin seçilen özelliklere göre render edilmesi)

### 3. Akıllı Kural Yönetimi
- **Üç temel kural tipi**:
  1. **Kombinasyon engelleme** (deny): Belirli özellik kombinasyonlarını yasaklama
  2. **Kombinasyon izin verme** (allow): Sadece belirli kombinasyonlara izin verme
  3. **Değer bazlı ayarlama**: Seçime bağlı olarak diğer özelliklerin değerlerini otomatik ayarlama

### 4. Parametre Gruplama
- **Özellikler (Features)** ve **Seçenekler (Options)** olarak iki grup
- Özellikler arasında güçlü kurallar ve bağımlılıklar
- Seçeneklerde daha esnek kombinasyonlar

## Önerilen Frontend Çözümü

### 1. Bileşen Yapısı (React)

```javascript
function ProductConfigurator() {
  // State yönetimi
  const [product, setProduct] = useState(null);
  const [selectedFeatures, setSelectedFeatures] = useState({});
  const [price, setPrice] = useState(0);
  const [validCombination, setValidCombination] = useState(true);

  // API'den ürün verilerini çekme
  useEffect(() => {
    async function fetchProduct() {
      const response = await axios.get('/api/products/MB');
      setProduct(response.data);
    }
    fetchProduct();
  }, []);

  // Özellik seçim handler'ı
  const handleFeatureSelect = async (featureId, optionId) => {
    const newSelection = {...selectedFeatures, [featureId]: optionId};
    setSelectedFeatures(newSelection);
    
    // Kural kontrolü için API isteği
    const validation = await axios.post('/api/products/MB/validate', newSelection);
    setValidCombination(validation.data.valid);
    setPrice(validation.data.price);
  };

  return (
    <div className="configurator">
      <ProductHeader 
        name={product?.name} 
        description={product?.description} 
        price={price}
      />
      
      <FeatureSections 
        features={product?.features} 
        onSelect={handleFeatureSelect}
        selectedFeatures={selectedFeatures}
      />
      
      {!validCombination && (
        <Alert message="Seçtiğiniz kombinasyon geçersiz!" type="error" />
      )}
      
      <ProductVisualization features={selectedFeatures} />
    </div>
  );
}
```

### 2. Dinamik Görselleştirme

```javascript
function ProductVisualization({ features }) {
  // Seçilen özelliklere göre görsel URL'ini oluştur
  const getImageUrl = () => {
    let baseUrl = '/images/motorbike';
    
    // Renk seçilmişse ekle
    if (features.color) baseUrl += `-${features.color}`;
    
    // Motor tipi seçilmişse ekle
    if (features.engine) baseUrl += `-${features.engine}`;
    
    return `${baseUrl}.jpg`;
  };

  return (
    <div className="product-visualization">
      <img src={getImageUrl()} alt="Configured Product" />
    </div>
  );
}
```

### 3. Kural Yönetimi Arayüzü

Admin paneli için bir kural editörü önerisi:

```javascript
function RuleEditor() {
  const [ruleType, setRuleType] = useState('deny');
  const [conditions, setConditions] = useState([]);
  const [actions, setActions] = useState([]);

  const addCondition = () => {
    setConditions([...conditions, { feature: '', operator: '=', value: '' }]);
  };

  const saveRule = async () => {
    await axios.post('/api/rules', {
      ruleType,
      conditions,
      actions
    });
  };

  return (
    <div>
      <select value={ruleType} onChange={(e) => setRuleType(e.target.value)}>
        <option value="deny">Kombinasyonu Engelle</option>
        <option value="allow">Kombinasyona İzin Ver</option>
        <option value="set">Değer Ata</option>
      </select>

      <h3>Koşullar</h3>
      {conditions.map((cond, index) => (
        <div key={index}>
          <FeatureDropdown 
            value={cond.feature}
            onChange={(val) => updateCondition(index, 'feature', val)}
          />
          {/* Diğer inputlar */}
        </div>
      ))}
      <button onClick={addCondition}>Koşul Ekle</button>

      {/* Benzer şekilde aksiyonlar için */}

      <button onClick={saveRule}>Kuralı Kaydet</button>
    </div>
  );
}
```

## Kullanıcı Deneyimi (UX) Önerileri

1. **Adım Adım Konfigürasyon**:
   - Özellikleri mantıksal gruplara ayırın (Motor, Renk, Donanım vb.)
   - Kullanıcıyı adım adım yönlendirin

2. **Anında Geri Bildirim**:
   - Geçersiz seçimlerde hemen uyarı gösterin
   - Alternatif öneriler sunun

3. **Fiyat Şeffaflığı**:
   - Her seçimin fiyat etkisini gösterin
   - Toplam fiyatı her zaman görünür tutun

4. **Görsel Geri Bildirim**:
   - Seçilen renk, model vb. özellikleri ürün görseline yansıtın
   - 360° görüntüleme veya zoom özelliği ekleyin

## Teknik Uygulama Detayları

1. **State Yönetimi**:
   - Redux veya Context API ile uygulama genelinde state yönetimi
   - Seçili özellikler, fiyat, geçerlilik durumu gibi bilgileri merkezileştirme

2. **API Entegrasyonu**:
   - `axios` veya `fetch` ile backend ile iletişim
   - Optimistik UI güncellemeleri için uygun hata yönetimi

3. **Performans Optimizasyonu**:
   - Büyük özellik listeleri için virtual scrolling
   - Görselleri önceden yükleme (preloading)

4. **Responsive Tasarım**:
   - Mobil cihazlarda da kullanılabilir bir arayüz
   - Touch-friendly kontrol elemanları

## Sonuç

Ekteki görselden anladığım kadarıyla, frontend tarafında şunları hedefliyorsunuz:

1. **Ürün bilgilerinin** etkileyici bir şekilde sunulduğu
2. **Kullanıcı dostu** bir konfigürasyon deneyimi sağlayan
3. **Karmaşık kuralları** kullanıcıya hissettirmeden yöneten
4. **Gerçek zamanlı görsel ve fiyat güncellemeleri** yapan

bir dinamik ürün konfigüratörü oluşturmak.

Bu hedeflere ulaşmak için önerdiğim React tabanlı bileşen yapısı ve state yönetimi, projenizin ihtiyaçlarını karşılayacaktır. Backend API ile entegrasyon konusunda veya spesifik bileşenlerin detaylandırılmasında yardımcı olmaktan mutluluk duyarım.














