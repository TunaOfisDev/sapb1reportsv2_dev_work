Harika bir geliştirme. Raporun statik bir görünümden, kullanıcı etkileşimli ve dinamik bir analiz aracına dönüşmesini sağlayacak bu isteğiniz, projenin değerini oldukça artıracaktır.

İstediğiniz dinamik filtreleme ve toplamlar mimarisini detaylandıran teknik dökümanı (`whitepaper`) aşağıda, belirttiğiniz dosya yoluna uygun olarak hazırladım.

-----

### Dosya: `backend/customersales/docs/customersales_whitepaper.md`

````markdown
# Teknik Döküman: Dinamik Filtreli Müşteri Satış Raporu (customersales_v2)

**Sürüm:** 1.0
**Tarih:** 02.09.2025
**Yazar:** TARS (sapb1reportsv2 Proje Asistanı)

---

## 1. Amaç ve Kapsam

Bu döküman, "Müşteri Bazlı Satış Özeti Aylık" raporunun (`customersales_v2`) teknik mimarisini ve geliştirme yol haritasını açıklamaktadır. Raporun temel amacı, SAP B1 veritabanından alınan satış verilerini, kullanıcı tarafından seçilebilen çoklu dinamik filtrelerle analiz etme imkanı sunmaktır.

**Ana Hedefler:**

1.  Kullanıcının **Satıcı**, **Satış Tipi** ve **Cari Grup** alanlarına göre çoklu seçim yapabilmesi.
2.  Yapılan filtrelere göre rapor tablosunun ve bu tabloya ait **dinamik alt toplamların** anlık olarak güncellenmesi.
3.  Filtrelerden etkilenmeyen, tüm veri setini temsil eden **statik genel toplamların** (Grand Totals) raporda her zaman görünür olması.

---

## 2. Teknik Mimari Genel Bakış

Bu dinamik yapıyı kurmak için hem backend hem de frontend tarafında koordineli bir mimari izlenecektir. Backend, veriyi ham ve filtrelenmiş olarak sunarken; frontend, kullanıcı etkileşimini yönetip veriyi görselleştirecektir.

**Veri Akış Şeması:**



1.  **Frontend (React):** Sayfa yüklendiğinde backend'e 3 temel istek gönderir:
    * Filtre seçeneklerini almak için (`/filters`).
    * Statik genel toplamları almak için (`/summary`).
    * Varsayılan (filtrelenmemiş) rapor verisini almak için (`/data`).
2.  **Kullanıcı Etkileşimi:** Kullanıcı, filtre bileşenlerinden (`Select`, `Checkbox` vb.) seçimler yapar.
3.  **Dinamik İstek:** Frontend, her filtre değişikliğinde seçili değerleri query parametresi olarak ekleyerek (`/data?satici=...&satisTipi=...`) backend'e yeni bir istek gönderir.
4.  **Backend (Django):** Gelen isteği analiz eder, query parametrelerine göre ana SQL sorgusuna dinamik `WHERE` koşulları ekler ve filtrelenmiş sonucu frontend'e döndürür.
5.  **Arayüz Güncellemesi:** Frontend, gelen yeni veri setiyle rapor tablosunu ve dinamik alt toplamları yeniden render eder. Statik genel toplamlar değişmez.

---

## 3. Backend Mimarisi (Django REST Framework)

Backend, veriyi üç farklı endpoint üzerinden sunarak sorumlulukları ayıracaktır. Bu, performansı artırır ve yönetimi kolaylaştırır.

### 3.1. API Endpoint'leri

`customersales/api/urls.py` dosyasında aşağıdaki gibi 3 yeni endpoint tanımlanacaktır:

| Method | Endpoint                                         | Amaç                                                                   |
| :----- | :----------------------------------------------- | :--------------------------------------------------------------------- |
| `GET`  | `/api/v1/reports/customersales_v2/filters`       | Filtre alanları için seçilebilir değerleri (Satici, SatisTipi vb.) getirir. |
| `GET`  | `/api/v1/reports/customersales_v2/summary`       | Filtrelerden etkilenmeyen statik genel aylık ve yıllık toplamları getirir. |
| `GET`  | `/api/v1/reports/customersales_v2/data`          | Raporun ana veri setini, query parametrelerine göre filtrelenmiş olarak getirir. |

### 3.2. Servis Katmanı (`services/report_service.py`)

Mevcut `get_monthly_customer_sales_data` fonksiyonu, dinamik filtrelemeyi destekleyecek şekilde güncellenecektir.

**Örnek Fonksiyon İmzası:**

```python
def get_monthly_customer_sales_data(filters: dict):
    base_query = """
        WITH ...
        ...
        SELECT ... FROM CTE_Pivot P
    """
    
    where_clauses = []
    params = {}

    if filters.get('satici'):
        where_clauses.append('"Satici" IN %(satici_list)s')
        params['satici_list'] = tuple(filters['satici'])

    if filters.get('satisTipi'):
        where_clauses.append('"SatisTipi" IN %(satisTipi_list)s')
        params['satisTipi_list'] = tuple(filters['satisTipi'])
    
    if filters.get('cariGrup'):
        where_clauses.append('"CariGrup" IN %(cariGrup_list)s')
        params['cariGrup_list'] = tuple(filters['cariGrup'])

    if where_clauses:
        # WHERE koşulunu ana sorgunun GROUP BY'dan önceki kısmına eklememiz gerekiyor.
        # Bu nedenle, sorguyu CTE_Pivot'tan sonraki ana SELECT'ten önce bölüp araya WHERE ekleyeceğiz.
        query = f"""
            WITH ...
            Lines AS (...)
            SELECT * FROM Lines
            WHERE {' AND '.join(where_clauses)}
        """
        # Daha sonra bu filtrelenmiş veri üzerinden pivot işlemi yapılacak.
        # Bu, sorgunun yeniden yapılandırılmasını gerektirir.
    else:
        query = base_query
    
    # ... HANA'ya sorguyu parametrelerle güvenli bir şekilde gönder ...
    # ...
````

**Not:** SQL Injection zafiyetlerini önlemek için `WHERE` koşulları asla string formatlama ile oluşturulmamalıdır. Sorgu parametreleri (`params`) kullanılmalıdır.

### 3.3. Önbellekleme (Caching) Stratejisi

Dinamik filtreler nedeniyle standart `@cache_page` dekoratörü yetersiz kalacaktır. Bunun yerine, gelen filtre parametrelerinden oluşan eşsiz bir `cache_key` üreten özel bir cache mekanizması uygulanacaktır.

```python
# views.py içinde örnek
from django.core.cache import cache
import json

def get(self, request, *args, **kwargs):
    filters = dict(request.query_params)
    cache_key = 'customersales_v2_data_' + json.dumps(filters, sort_keys=True)
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    report_data = get_monthly_customer_sales_data(filters)
    cache.set(cache_key, report_data, timeout=60 * 15) # 15 dakika cache
    return Response(report_data)
```

-----

## 4\. Frontend Mimarisi (React)

Frontend, kullanıcı arayüzünü yönetmek ve backend ile verimli iletişim kurmak için modern React prensiplerini kullanacaktır.

### 4.1. Durum Yönetimi (State Management)

Raporun karmaşıklığı göz önüne alındığında, **Redux Toolkit** veya **TanStack Query (React Query)** kullanılması önerilir.

  * **TanStack Query:** API durumunu (veri, yüklenme durumu, hatalar, önbellekleme) yönetmek için idealdir. `/filters`, `/summary` ve `/data` istekleri için ayrı `query`'ler tanımlanır.
  * **Local State (`useState`):** Seçili olan filtrelerin anlık durumunu tutmak için yeterlidir.

### 4.2. Bileşen Yapısı (Component Structure)

Sayfa, yönetilebilir ve yeniden kullanılabilir bileşenlere ayrılacaktır.

  * `CustomerSalesV2Page.jsx` (Ana Konteyner Bileşen)
      * API isteklerini yönetir ve veriyi alt bileşenlere dağıtır.
  * `ReportFilterBar.jsx`
      * `/filters` endpoint'inden gelen veriyle `Satici`, `SatisTipi` ve `CariGrup` için çoklu seçim bileşenlerini (örn: `antd Select` veya `MUI Autocomplete`) render eder.
      * Seçim değiştiğinde ana bileşendeki state'i günceller.
  * `ReportSummary.jsx`
      * `/summary` endpoint'inden gelen statik genel toplamları gösterir.
  * `ReportDataTable.jsx`
      * `/data` endpoint'inden gelen filtrelenmiş veriyi alır.
      * Veriyi göstermek için **@tanstack/react-table** kütüphanesi kullanılacaktır.
      * Tablo içinde, gösterilen veriye göre **dinamik alt toplamları** (örneğin, "Görüntülenen X müşterinin toplam satışı") hesaplayıp gösterebilir.

### 4.3. Veri Modelleri (API Yanıtları)

**`/filters` Yanıtı:**

```json
{
  "saticilar": ["Ahmet Yılmaz", "Ayşe Kaya", "Tanımsız"],
  "satisTipleri": ["YURTİÇİ", "YURTDIŞI", "PROJE"],
  "cariGruplar": ["BAYİ", "ZİNCİR MAĞAZA", "İHRACAT"]
}
```

**`/summary` Yanıtı:**

```json
{
  "toplamNetSPB_EUR": 12540350.88,
  "aylikToplamlar": {
    "Ocak": 1200000.50,
    "Şubat": 950400.30,
    // ... diğer aylar
  }
}
```

**`/data` Yanıtı:**

```json
[
  {
    "Satici": "Ahmet Yılmaz",
    "SatisTipi": "YURTİÇİ",
    "CariGrup": "BAYİ",
    "MusteriKodu": "120.01.000123",
    "MusteriAdi": "Örnek Müşteri A.Ş.",
    "ToplamNetSPB_EUR": 150000.75,
    "Ocak": 25000.00,
    "Şubat": 15000.50,
    // ... diğer aylar
  }
]
```

-----

## 5\. Geliştirme Yol Haritası

1.  **Backend - Adım 1:** `customersales` uygulaması içinde `filters`, `summary` ve `data` için üç ayrı view ve URL'nin oluşturulması.
2.  **Backend - Adım 2:** `report_service.py` içindeki SQL sorgularının dinamik `WHERE` koşullarını güvenli bir şekilde kabul edecek şekilde yeniden düzenlenmesi.
3.  **Backend - Adım 3:** API'lerin Postman veya benzeri bir araçla test edilmesi.
4.  **Frontend - Adım 1:** `ReportFilterBar`, `ReportSummary`, `ReportDataTable` bileşenlerinin iskeletlerinin oluşturulması.
5.  **Frontend - Adım 2:** TanStack Query veya Redux ile API entegrasyonunun yapılması; sayfa yüklendiğinde üç endpoint'in de çağrılması.
6.  **Frontend - Adım 3:** Filtre seçimlerinin state'e bağlanması ve her değişiklikte `/data` endpoint'ine yeni istek atılmasının sağlanması.
7.  **Frontend - Adım 4:** `@tanstack/react-table` ile gelen verinin tabloya basılması ve tablo içi dinamik toplamların konfigüre edilmesi.
8.  **Son Adım:** Genel entegrasyon testi ve performans optimizasyonu.

<!-- end list -->

```
```