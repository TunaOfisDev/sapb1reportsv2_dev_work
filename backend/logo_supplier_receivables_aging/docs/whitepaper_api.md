İşte `backend/logo_supplier_receivables_aging/docs/whitepaper_api.md` dosyası için teknik bir whitepaper taslağı:

---

# Logo Tiger3 Supplier Receivables Aging API Whitepaper

## 1. GİRİŞ

Bu doküman, **Logo Tiger3 ERP** sistemine entegre çalışan **Tedarikçi Alacak Yaşlandırma API'si**nin teknik mimarisini, kullanım senaryolarını ve veri işleyişini açıklamaktadır. API, tedarikçi bazlı borç-alacak dengelerini aylar özelinde analiz ederek muhasebe ve finans ekiplerine operasyonel karar desteği sağlamayı hedefler.

## 2. AMAÇ

* Tedarikçi cari hesaplarının aylık bazda kalan alacaklarını göstermek
* “Öncesi” ve “Son 4 ay” için negatif kalanları analiz etmek
* RESTful servisler ile entegrasyonu kolay, JSON formatında veri sunmak

## 3. VERİ KAYNAĞI

Veri, doğrudan Logo Tiger3 ERP'nin HANA veritabanı üzerinden alınmaktadır. HANA verisi aşağıdaki iki temel kalemi içerir:

* **Borç:** Tedarikçiye yapılan ödemeler
* **Alacak:** Tedarikçiden alınan faturalandırılmış hizmetler

Veri SQL sorguları ile `MM-yyyy` formatında gruplanır ve `alacak - borç` farkı üzerinden kalan alacaklar hesaplanır.

## 4. VERİ MODELİ

JSON örnek veri yapısı:

```json
{
  "Cari Kod": "320.40.0000045",
  "Cari Ad": "ARGETEK TEKNİK DANIŞMANLIK",
  "Güncel Bakiye": -8383842.00,
  "Öncesi": 0.0,
  "Şub25": 0.0,
  "Mar25": -8383842.00,
  "Nis25": 0.0,
  "May25": 0.0
}
```

### Açıklamalar:

* **Güncel Bakiye:** Cari hesabın toplam alacak durumu
* **Öncesi:** 2025 öncesi dönemlere ait kalan tutar
* **Son 4 Ay:** Seçilen 4 ay boyunca oluşan kalan alacak değerleri

## 5. API ENDPOINTLERİ

### 5.1. `/api/v2/supplier-aging/summary/`

* **Yöntem:** `GET`
* **Açıklama:** Tüm cari hesapların yaşlandırılmış alacak verilerini JSON formatında döner.
* **Parametre:** Yok

### 5.2. `/api/v2/supplier-aging/fetch-hana-data/`

* **Yöntem:** `GET`
* **Açıklama:** HANA veritabanından canlı veri çeker, veritabanını günceller.

### 5.3. `/api/v2/supplier-aging/export-xlsx/`

* **Yöntem:** `GET`
* **Açıklama:** Güncel veriyi Excel formatında dışa aktarır.

### 5.4. `/api/v2/supplier-aging/last-updated/`

* **Yöntem:** `GET`
* **Açıklama:** Verinin en son ne zaman güncellendiğini döner.

## 6. OTENTİKASYON

Tüm endpoint’ler **JWT Authentication** ile korunmaktadır. Her istek için `Authorization: Bearer <token>` başlığı zorunludur.

## 7. VERİ HESAPLAMA KURALLARI

* Her ay için `(Toplam Alacak - Toplam Borç)` işlemi uygulanır.
* Negatif kalan değerler, tedarikçiden tahsil edilmesi gereken tutarı gösterir.
* Decimal hesaplama zorunludur; `float` tipi kullanılmaz.

## 8. ENTEGRASYON

API, React tabanlı bir frontend ile entegredir. Frontend tarafında:

* `react-table` ile filtreleme, sıralama ve sayfalama yapılır.
* Excel dışa aktarımı mevcuttur.
* “Anlık Veri Çek” butonu ile güncel veri HANA’dan çağrılır.

## 9. SÜRÜM VE BAKIM

* **API Versiyonu:** v2
* **Teknik Destek:** Backend geliştirme ekibi
* **Depo:** `backend/logo_supplier_receivables_aging/`

---

İstersen bu dokümana görsel diyagram veya tablo ekleyebilirim. Onaylarsan Markdown dosyası olarak çıktı da verebilirim.
