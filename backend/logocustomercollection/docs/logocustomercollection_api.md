Tedarikçi alacak yaşlandırma API'sine dayalı olarak, müşteri hesaplarının borçlarının belge tarihine göre hangi aylardan geldiğini gösteren **"logocustomercollection"** adlı bir API tasarlayalım. Bu API, Logo Tiger3 ERP sistemine entegre olacak ve müşteri borçlarını aylık bazda analiz ederek JSON formatında sunacak. Aşağıda, bu API için teknik bir whitepaper taslağı hazırladım. Taslak, önceki whitepaper formatına uygun şekilde düzenlendi ve **logocustomercollection** API'sinin gereksinimlerine göre özelleştirildi.

---

# Logo Tiger3 Customer Collection Aging API Whitepaper

## 1. GİRİŞ

Bu doküman, **Logo Tiger3 ERP** sistemine entegre çalışan **Müşteri Borç Yaşlandırma API'si ("logocustomercollection")**'nın teknik mimarisini, kullanım senaryolarını ve veri işleyişini açıklamaktadır. API, müşteri cari hesaplarının borçlarını (alacaklar) belge tarihine göre aylara göre sınıflandırarak finans ve muhasebe ekiplerine operasyonel karar desteği sağlamayı amaçlar.

## 2. AMAÇ

- Müşteri cari hesaplarının borçlarının (alacakların) aylık bazda dağılımını göstermek.
- “Öncesi” ve “Son 4 ay” için pozitif kalanları (müşteriden tahsil edilecek tutarları) analiz etmek.
- RESTful servisler aracılığıyla JSON formatında veri sunarak entegrasyonu kolaylaştırmak.

## 3. VERİ KAYNAĞI

Veri, Logo Tiger3 ERP'nin **HANA veritabanı** üzerinden çekilmektedir. Veritabanı aşağıdaki temel kalemleri içerir:

- **Borç:** Müşterinin firmaya olan borçları (faturalar, vb.).
- **Alacak:** Firmadan müşteriye yapılan ödemeler veya iadeler.
- **Belge Tarihi:** Borçların oluştuğu tarih, `MM-yyyy` formatında gruplanır.

Veriler, SQL sorguları ile belge tarihine göre aylık bazda gruplanır ve `(Borç - Alacak)` farkı üzerinden kalan borçlar hesaplanır.

## 4. VERİ MODELİ

JSON örnek veri yapısı:

```json
{
  "CariKod": "120.40.0000123",
  "CariAd": "AYTEK TEKNOLOJİ A.Ş.",
  "GunelBakiye": 1254300.50,
  "Oncesi": 200000.00,
  "Sub25": 354300.50,
  "Mar25": 400000.00,
  "Nis25": 250000.00,
  "May25": 50000.00
}
```

### Açıklamalar:

- **CariKod:** Müşterinin cari hesap kodu (ör. 120 ile başlayan hesaplar).
- **CariAd:** Müşterinin adı.
- **GunelBakiye:** Cari hesabın toplam borç durumu (pozitif değer, müşteriden tahsil edilecek tutarı gösterir).
- **Oncesi:** 2025 öncesi dönemlere ait kalan borç tutarı.
- **Son 4 Ay:** Seçilen 4 ay boyunca oluşan borç değerleri (ör. Şubat 2025, Mart 2025, Nisan 2025, Mayıs 2025).

## 5. API ENDPOINTLERİ

### 5.1. `/api/v2/logocustomercollection/summary/`

- **Yöntem:** `GET`
- **Açıklama:** Tüm müşteri cari hesaplarının borç yaşlandırma verilerini JSON formatında döner.
- **Parametreler:**
  - `cariKod` (opsiyonel): Belirli bir cari hesap için filtreleme yapar (ör. `120.40.0000123`).
  - `startDate` (opsiyonel): Analiz başlangıç tarihi (varsayılan: son 4 ay).
  - `endDate` (opsiyonel): Analiz bitiş tarihi (varsayılan: cari ay).
- **Örnek İstek:**  
  ```
  GET /api/v2/logocustomercollection/summary/?cariKod=120.40.0000123
  ```
- **Örnek Yanıt:**
  ```json
  [
    {
      "CariKod": "120.40.0000123",
      "CariAd": "AYTEK TEKNOLOJİ A.Ş.",
      "GunelBakiye": 1254300.50,
      "Oncesi": 200000.00,
      "Sub25": 354300.50,
      "Mar25": 400000.00,
      "Nis25": 250000.00,
      "May25": 50000.00
    }
  ]
  ```

### 5.2. `/api/v2/logocustomercollection/fetch-hana-data/`

- **Yöntem:** `GET`
- **Açıklama:** HANA veritabanından canlı veri çeker ve veritabanını günceller.
- **Parametreler:** Yok
- **Örnek Yanıt:**
  ```json
  {
    "status": "success",
    "message": "Veri HANA'dan başarıyla çekildi ve güncellendi.",
    "lastUpdated": "01-07-2025 13:56"
  }
  ```

### 5.3. `/api/v2/logocustomercollection/export-xlsx/`

- **Yöntem:** `GET`
- **Açıklama:** Güncel borç yaşlandırma verisini Excel formatında dışa aktarır.
- **Parametreler:**
  - `cariKod` (opsiyonel): Belirli bir cari hesap için veri dışa aktarır.
- **Yanıt:** Excel dosyası (`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`).

### 5.4. `/api/v2/logocustomercollection/last-updated/`

- **Yöntem:** `GET`
- **Açıklama:** Verinin en son ne zaman güncellendiğini döner.
- **Örnek Yanıt:**
  ```json
  {
    "lastUpdated": "01-07-2025 13:56",
    "timezone": "TRT (UTC+3)"
  }
  ```

## 6. OTENTİKASYON

Tüm endpoint’ler **JWT Authentication** ile korunmaktadır. Her istek için aşağıdaki başlık zorunludur:

```
Authorization: Bearer <token>
```

Token, Logo Tiger3 ERP sisteminin kullanıcı kimlik doğrulama servisi üzerinden alınır.

## 7. VERİ HESAPLAMA KURALLARI

- Her ay için `(Toplam Borç - Toplam Alacak)` işlemi uygulanır.
- Pozitif kalan değerler, müşteriden tahsil edilmesi gereken tutarı gösterir.
- Hesaplamalarda `decimal` veri tipi kullanılır; `float` tipi yuvarlama hatalarını önlemek için kullanılmaz.
- Belge tarihi, `MM-yyyy` formatında gruplanır.
- Cari kodlar, `120` ile başlayan müşteri hesaplarına özeldir.

## 8. ENTEGRASYON

API, React tabanlı bir frontend ile entegredir. Frontend özellikleri:

- **react-table** ile veri filtreleme, sıralama ve sayfalama.
- Excel dışa aktarım özelliği.
- “Anlık Veri Çek” butonu ile HANA’dan canlı veri çekimi.
- Grafiksel analiz için **Chart.js** entegrasyonu (aylık borç dağılımı görselleştirme).

## 9. ZAMAN DAMGASI VE YEREL SAAT YÖNETİMİ

- Tüm işlemler ve raporlamalar **Türkiye/İstanbul (UTC+3)** saat dilimine göre yapılır.
- Tarih formatı: `gg-aa-yyyy ss:dd` (ör. `01-07-2025 13:56`).
- Harici veri kaynakları UTC kullanıyorsa, otomatik olarak UTC+3’e çevrilir.

## 10. ŞÜPHE MODU

- **Tetkileyiciler:**
  - HANA veritabanından veri eksikliği.
  - Belge tarihi veya cari kod çelişkisi.
  - Aylık borç toplamlarında tutarsızlık.
- **Aksiyon:** Analiz durdurulur ve şu mesaj döner:
  ```json
  {
    "status": "error",
    "message": "Analiz durduruldu – veri uyumsuz. Lütfen güncel veri yükleyin."
  }
  ```

## 11. SÜRÜM VE BAKIM

- **API Versiyonu:** v2
- **Teknik Destek:** Backend geliştirme ekibi
- **Depo:** `backend/logo_customer_collection_aging/`
- **Güncelleme Sıklığı:** HANA veri güncellemelerine bağlı olarak günlük.

## 12. PERFORMANS GÖSTERGELERİ

- **Veri Çekme Süresi:** Ortalama 2-5 saniye (HANA bağlantı hızına bağlı).
- **Veri Hacmi:** Tek istekte maksimum 10.000 cari hesap.
- **Hata Oranı:** %0.1’den düşük (decimal hesaplama ile).

## 13. ÖRNEK KULLANIM SENARYOSU

1. Finans ekibi, `120.40.0000123` cari kodlu müşterinin borçlarını analiz etmek ister.
2. `/api/v2/logocustomercollection/summary/?cariKod=120.40.0000123` endpoint’ine GET isteği gönderilir.
3. API, müşterinin son 4 ay ve öncesi için borç dağılımını JSON formatında döndürür.
4. Ekip, veriyi Excel’e aktarmak için `/api/v2/logocustomercollection/export-xlsx/` endpoint’ini kullanır.

---

### Ek Notlar

- **Görselleştirme:** İstersen, API yanıtlarının görselleştirilmesi için bir **Chart.js** diyagramı veya **Mermaid** ile akış şeması ekleyebilirim.
- **Markdown Çıktısı:** Bu dokümanı `backend/logo_customer_collection_aging/docs/whitepaper_api.md` olarak Markdown formatında kaydedebilirim. Onaylarsan dosyayı oluştururum.
- **Test Verisi:** Örnek veri seti ile test endpoint’leri oluşturmamı istersen, lütfen belirt.

Onayını bekliyorum!