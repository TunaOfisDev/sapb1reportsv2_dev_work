# BOM Cost Manager - Django REST API Whitepaper

Bu doküman, **BOM Cost Manager** adlı Django tabanlı bir **Restful API** projesinin mimarisini, klasör yapısını ve temel iş akışını açıklamaktadır. Proje, SAP Business One HANA veritabanından **ürün ağacı (BOM)** verilerini çekip bu verileri bir **PostgreSQL** veya Django DB’ye kaydederek, kullanıcıya **“mamul maliyet analizi”** ve **“yeniden değerleme (override) imkanı”** sunar. Ayrıca, mamul ve bileşen seviyesinde farklı çarpanlar (işçilik, genel üretim gideri, lisans, komisyon vb.) uygulayarak **nihai maliyet** hesaplamalarını destekler.

---

## 1. Arkaplan ve Amaç

- **SAP Business One** içinde patlatılmış ürün ağacı (BOM) maliyetini detaylı biçimde analiz etmek zordur. SAP, yarımamuller için resmi iş emirleri açılmadan **geleceğe yönelik** bir proje maliyeti hesaplamasını standart olarak sunmamaktadır.
- **BOM Cost Manager** bu ihtiyacı karşılamak için, SAP HANA’daki tabloları (ITT1, OITT, OITM vs.) karmaşık **SQL sorguları** ile patlatır ve her bir kalemin (ham madde, yarımamul, ana mamul) en güncel son satın alma fiyatını, override fiyatlarını ve ek maliyet çarpanlarını dikkate alarak **yeni bir maliyet öngörüsü** oluşturur.
- Böylece **yüksek enflasyon** ortamında, kullanıcı planlama veya maliyet departmanının **“ne olurdu?”** senaryolarını çalıştırmasına, malzeme ve yarımamullerin fiyatını öngörülen zam yüzdeleriyle veya doğrudan yeni rakamlarla güncellemesine imkan tanır.
- Django Rest API yapısıyla, **React** veya **başka bir front-end** üzerinden entegre çalışması kolaydır. Hem **BOM** hem de **Product** listesini getiren endpoint’ler, override işlemine ve kayıt (versiyon) oluşturmaya izin veren servisler içerir.

---

## 2. Proje Klasör Yapısı

Aşağıda `backend/bomcostmanager` altında yer alan dosya/folder yapısı özetlenmiştir:

```
backend/
└── bomcostmanager/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── permissions.py
    ├── tests.py
    ├── api/
    │   ├── __init__.py
    │   ├── bomcomponent_views.py
    │   ├── bomproduct_views.py
    │   ├── serializers.py
    │   └── urls.py
    ├── connect/
    │   ├── __init__.py
    │   ├── bomcomponent_data_fetcher.py
    │   └── bomproduct_data_fetcher.py
    ├── docs/
    │   ├── bomcostmanager.md
    │   ├── frontend.md
    │   └── sql.md
    ├── helpers/
    │   ├── __init__.py
    │   ├── bomcomponent_helper.py
    │   └── bomproduct_helper.py
    ├── migrations/
    ├── models/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── bomcomponent_models.py
    │   └── bomproduct_models.py
    ├── services/
    │   ├── __init__.py
    │   ├── bomcomponent_service.py
    │   └── bomproduct_service.py
    └── __pycache__/
```

### Ana Klasörlerin Görevleri

- **api/**:  
  - Django REST framework `ViewSet` veya `APIView` implementasyonlarını içerir. (bomcomponent_views, bomproduct_views)  
  - `serializers.py` model verisini JSON formatına dönüştüren serializer’ları barındırır.  
  - `urls.py` bu app’e özgü URL’leri tanımlar.  

- **connect/**:  
  - SAP HANA veya diğer kaynaklardan veri **çekme** (fetch) işlevleri. `bomcomponent_data_fetcher.py` ve `bomproduct_data_fetcher.py` dosyalarında, `requests` veya HANA client kütüphanesiyle “SAP HANA DB sorgu API”sine istek atılır.  

- **docs/**:  
  - `bomcostmanager.md`, `frontend.md`, `sql.md` gibi dokümantasyon dosyalarını barındırır.  
  - `sql.md` tipik olarak karmaşık SQL sorgularını veya sorgu açıklamalarını tutar.  

- **helpers/**:  
  - Belirli alanlarda (örneğin parse logic, update logic) tekrar eden mantıkları ufak helper fonksiyonlar şeklinde barındırır.  
  - `bomcomponent_helper.py`, `bomproduct_helper.py` SAP’den çekilen raw JSON datayı parse eder veya güncellemelerde ek validasyon mantığı içerir.  

- **models/**:  
  - Django modelleri ve veritabanı tablolarının tanımları.  
  - `base.py`: Ortak alanlar (created_at, updated_at, vs.)  
  - `bomcomponent_models.py`: BOM bileşenlerinin modeli (`BOMComponent`, `BOMRecord`)  
  - `bomproduct_models.py`: Ürün (BOMProduct) modeli  

- **services/**:  
  - “İş mantığı”nı içeren katman. `bomcomponent_service.py` gibi dosyalar, connect + helper + model arası akışı organize eder.  
  - Örneğin `update_products_from_hana(token)` fonksiyonu, `bomproduct_data_fetcher` yardımıyla HANA verilerini çekip, `bomproduct_helper` ile parse edip, veritabanındaki `BOMProduct` kayıtlarını günceller.  

- **permissions.py**:  
  - “HasBOMProductAccess” gibi özel permission sınıflarını barındırıp, departman bazlı CRUD yetkisi gibi kontrolleri yapabilir.  

- **admin.py**:  
  - Django Admin panelinde BOM modellerini göstermek üzere `admin.site.register()` tanımlamaları yapılabilir.  

- **tests.py**:  
  - Pytest veya Django test framework’ünde birim/integration testleri burada konumlandırılabilir.

---

## 3. Ana Kavramlar

1. **BOMProduct**:  
   - SAP’de “ItmsGrpCod=105” (örnek: mamul grubu) olarak tanımlanmış ürün.  
   - BOM (ürün ağacı) var (OITT tablosuna kaydı var).  
   - Modelde “item_code”, “item_name”, “bom_create_date”, “sales_price” gibi alanlar yer alır.  

2. **BOMComponent**:  
   - Patlatılmış ürün ağacının satır düzey verisi: “main_item”, “component_item_code”, “quantity”, “level” vb.  
   - “new_last_purchase_price” gibi override alanları ve “labor_multiplier” gibi çarpan alanları barındırır.  
   - `updated_cost` alanı: `(effective_price) × labor_multiplier × overhead_multiplier` mantığıyla kaydedilir.  

3. **BOMRecord**:  
   - Kullanıcı bir “mamul maliyet senaryosu”nu, override ettiği bileşen fiyatları ve çarpanlarla birlikte “proje adı” şeklinde DB’ye kaydedebilir.  
   - Daha sonra bu kaydı geri çağırarak karşılaştırmalar yapılabilir.

4. **Services (bomcomponent_service / bomproduct_service)**:  
   - HANA’dan veri çekip parse etme (connect), veritabanına kaydetme, override güncellemelerini ve nihai cost hesaplarını organize eder.

5. **Çarpan Faktörleri**:  
   - Ek bir gereksinimle, ana mamul üstünde “işçilik faktörü”, “genel gider faktörü”, “lisans/komisyon faktörü” gibi çarpanlar eklenebilir. Bu çarpanlar, temel malzeme maliyetinin “nihai” değere ulaşmasında kullanılır.

---

## 4. Veri Akışı

1. **Ürün Listesi (BOMProduct)**  
   - `bomproduct_views.py` içinde bir `APIView` (veya ViewSet) tanımlıdır:  
     - `GET /api/v2/bomcostmanager/bomproducts/` => Yerel DB’de saklanan mamul listesi  
     - `POST /api/v2/bomcostmanager/bomproducts/fetch_from_hana/` => SAP HANA’dan canlı veri çekip `BOMProduct` tablosunu günceller.  

2. **BOM Bileşenleri (BOMComponent)**  
   - `bomcomponent_views.py`:  
     - `GET /api/v2/bomcostmanager/bomcomponents/list/` => Tüm `BOMComponent` verilerini çeker  
     - `POST /api/v2/bomcostmanager/bomcomponents/fetch_from_hana/` => HANA’dan, parametredeki `item_code` mamulün patlatılmış ürün ağacını çeker, veritabanına kaydeder.  

3. **Override ve Güncelleme**  
   - `PUT /api/v2/bomcostmanager/bomcomponents/{id}/` => Tek bir bileşene dair `new_last_purchase_price`, `labor_multiplier`, `overhead_multiplier` gibi alanları güncelleyerek “updated_cost” otomatik hesaplanır.  

4. **Versiyonlama / BOMRecord**  
   - `POST /api/v2/bomcostmanager/bomrecords/` => Seçilen bileşenlerin override değerleri + 4 çarpan (işçilik, overhead, lisans, komisyon) + “proje adı” kaydedilir.  
   - “BOMRecord” ile o anki senaryo “frozen” halde saklanmış olur.

5. **SQL Sorguları**  
   - “docs/sql.md” dosyasında karmaşık **patlatılmış ürün ağacı sorguları** (422 satırlık) detaylandırılır. `connect/bomcomponent_data_fetcher.py` bu sorguyu HANA DB’ye gönderip JSON alır.  
   - Yine BOMProduct’lar için “MamulListe_BOMCreationUpdateUsers_FormattedDate.sql” sorgusu yer alır.

---

## 5. Örnek Endpointler

### 5.1 BOMProductViewSet

- **`GET /api/v2/bomcostmanager/bomproducts/`**  
  Yerel DB’deki `BOMProduct` listesini döner (filtreleme, sayfalama opsiyonel).  

- **`POST /api/v2/bomcostmanager/bomproducts/fetch_from_hana/`**  
  Authorization header ile token alır. Sonra “bomproduct_service.update_products_from_hana(token)” çağrılır, HANA’daki mamul listesini çeker, parse edip DB’ye yazar.

### 5.2 BOMComponentViewSet

- **`GET /api/v2/bomcostmanager/bomcomponents/list/`**  
  Tüm `BOMComponent` kayıtlarını veya bir ürünün bileşenlerini döner (parametre ile `item_code` vs.).  

- **`POST /api/v2/bomcostmanager/bomcomponents/fetch_from_hana/?item_code=XYZ`**  
  HANA’dan “XYZ” mamulün patlatılmış BOM’unu çekip `BOMComponent` tablosunda günceller.

- **`PUT /api/v2/bomcostmanager/bomcomponents/{id}/`**  
  Tek bir bileşeni güncelle. JSON body’de `new_last_purchase_price`, `labor_multiplier`, vb. gelebilir. Save() esnasında `updated_cost` otomatik hesaplanır.

### 5.3 BOMRecord

- **`POST /api/v2/bomcostmanager/bomrecords/`**  
  Yeni bir senaryo/versiyon kaydı oluşturur. “project_name”, “description” ve bileşenlerin override verileri ya da 4 çarpan parametresi body’de gelir.  
- (Opsiyonel) `GET /api/v2/bomcostmanager/bomrecords/` => Tüm kaydedilmiş senaryolar.  

---

## 6. Modellerin Detayları

1. **`BOMComponent`** (bkz. `bomcomponent_models.py`)  
   - `main_item`, `sub_item`, `component_item_code`, `quantity`, `level` …  
   - `new_last_purchase_price`, `labor_multiplier`, `overhead_multiplier`, …  
   - `updated_cost` => override price * labor * overhead  
   - `save()` metodunda otomatik hesaplama mantığı.  

2. **`BOMRecord`**  
   - “project_name” + “description” => senaryo ismi, isteğe bağlı açıklama  
   - Farklı tablo ile “bileşenler/override” ilişkisi istenirse ek bir ManyToMany tablosu (tasarım opsiyonel).  

3. **`BOMProduct`**  
   - `item_code`, `item_name`, `sales_price`, `bom_create_date`, vs.  
   - “Yarımamulse?” (grup kodu vs.)  
   - `last_fetched_at` => HANA’dan son veri çekme zamanı  

---

## 7. Services Katmanı

- **`bomproduct_service.py`**:  
  - `update_products_from_hana(token)`: `connect/bomproduct_data_fetcher.fetch_hana_db_data(token)` fonksiyonuyla HANA endpoint’inden JSON alır, `helpers/bomproduct_helper.parse_hana_product_data()` ile parse eder, `BOMProduct` tablosunu create/update yapar.  

- **`bomcomponent_service.py`**:  
  - `update_components_from_hana(token)`: HANA’daki patlatılmış ürün ağacı sorgusunu çeker (`bomcomponent_data_fetcher`).  
  - `parse_hana_component_data()` yardımıyla veriyi `BOMComponent` formuna dönüştürür. DB’de update/create yapar.  
  - `update_bom_component_cost(component)` => override’lı maliyeti hesaplar.  

Bu katman, **veri çekme** (connect) + **parse** (helpers) + **model** (save) akışını üstlenir.

---

## 8. Helpers Katmanı

- **`bomproduct_helper.py`**  
  - `parse_hana_product_data(raw_data)`: HANA’dan dönen “ItemCode, ItemName…” dictionary’yi Django model alanlarına map eder.  
  - `update_bom_product_record(product, new_data)`: mevcut kaydı güncellerken ek validasyon veya default atama yapar.  

- **`bomcomponent_helper.py`**  
  - `parse_hana_component_data(raw_data)`: BOM bileşen satırını parse, level, quantity, vs.  
  - `update_bom_component_cost(bom_component)`: Tekil bileşende `new_last_purchase_price` > 0 ise kullanılacak, yoksa `last_purchase_price_upb` kullanılacak. (BOMComponent `save()` mantığını da destekler.)

---

## 9. API Katmanı

### serializers.py
- **`BOMProductSerializer`**, **`BOMComponentSerializer`**, **`BOMRecordSerializer`** vs.
- Django model örneklerini JSON formatına dönüştürür ve tam tersi.

### bomproduct_views.py
- `BOMProductViewSet` (veya `APIView`) => CRUD + `refresh_from_hana()`  
- Tüm `BOMProduct` kayıtlarına GET, ID bazında GET/PUT/DELETE vb.

### bomcomponent_views.py
- `BOMComponentViewSet` => `/list/`, `/fetch_from_hana/` vb. action’larla BOM bileşen işlemleri.  
- “override update” => `PUT /{id}/`

### urls.py
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .bomcomponent_views import BOMComponentViewSet
from .bomproduct_views import BOMProductViewSet

router = DefaultRouter()
router.register(r'bomcomponents', BOMComponentViewSet, basename='bomcomponent')
router.register(r'bomproducts', BOMProductViewSet, basename='bomproduct')

urlpatterns = [
    path('', include(router.urls)),
]
```
- Bu şekilde `/api/v2/bomcostmanager/bomcomponents/`, `/api/v2/bomcostmanager/bomproducts/` vb. endpoint’ler otomatik yaratılır.

---

## 10. Permissions

- **permissions.py** içerik:
  - Örnek: `HasBOMProductAccess` => belirli user’ın departman bazlı API yetkisi (create/read/update/delete) var mı kontrol eder.
  - “APIAccessPermission” tablosu gibi bir yapı üzerinden “can_create, can_read, can_update, can_delete” flag’leri.

Uygulamada isterseniz `IsAuthenticated` + `HasBOMProductAccess` gibi permission’lar eklenir.

---

## 11. Sonuç ve Öneriler

- **BOM Cost Manager** projesi, SAP Business One HANA veritabanından, karmaşık **SQL** sorgular ile **ürün ağacı** + **bileşen** detaylarını çekerek bunları Django DB’de saklar.  
- Kullanıcıya, **ham madde düzeyinde** override fiyatlar ve ek çarpanlar (işçilik, overhead, lisans, komisyon vs.) ile **nihai maliyet** senaryoları oluşturma imkanı verir.  
- Django Rest API mimarisi, **React** veya benzeri front-end uygulamalarıyla **rahat entegrasyon** sağlar.  
- `services/`, `connect/`, `helpers/` katmanları projenin **temiz** ve **esnek** olmasını garanti eder.  
- “Versiyon / Proje kaydı” (`BOMRecord`) yardımıyla gelecek dönemde, farklı senaryolar (farklı zam oranları, çarpanlar) için **karşılaştırma** yapmak mümkündür.

Bu şekilde, **SAP**’nin standart yapısından bağımsız, **yüksek enflasyon** ortamına özel **dinamik maliyet** senaryoları oluşturmak, planlama ve maliyet departmanlarının **“ne olurdu?”** sorularına hızlı cevap vermek hedeflenmektedir.

> **Not**: İlerleyen aşamalarda, “Reactable” vb. front-end tablolar ile satır bazında override girme, toplu zam yüzdesi, vs. gelişmiş UI çözümleri de entegre edilerek kullanıcı deneyimi güçlendirilebilir.

--- 

**Bu whitepaper**’da, projenin **Django REST** katmanına dair mimari yaklaşım, klasör yapısı, veri akışı ve temel bileşenler açıklanmıştır. Detaylar için `docs/` klasöründeki ek dokümanlara ve ilgili **model/service** dosyalarına başvurabilirsiniz.