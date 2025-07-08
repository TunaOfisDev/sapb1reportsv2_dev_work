# SupplierPayment API Whitepaper

## İçindekiler
1. [Giriş](#giriş)
2. [Sistem Mimarisi](#sistem-mimarisi)
3. [Veri Modelleri](#veri-modelleri)
4. [API Endpoint'leri](#api-endpointleri)
5. [Veri Akışı ve İşleme Süreci](#veri-akışı-ve-i̇şleme-süreci)
6. [Performans Optimizasyonları](#performans-optimizasyonları)
7. [Güvenlik Önlemleri](#güvenlik-önlemleri)
8. [Canlı Bildirim Sistemi](#canlı-bildirim-sistemi)
9. [Kapanış Faturası Hesaplama Algoritması](#kapanış-faturası-hesaplama-algoritması)
10. [Test ve Bakım](#test-ve-bakım)
11. [Sık Karşılaşılan Sorunlar ve Çözümleri](#sık-karşılaşılan-sorunlar-ve-çözümleri)
12. [Geliştirme Yol Haritası](#geliştirme-yol-haritası)

## Giriş

SupplierPayment API, tedarikçi ödemelerini SAP HANA veritabanından çeken, işleyen ve analiz eden kapsamlı bir REST API sistemidir. Bu API, işletmelerin tedarikçilere olan borçlarını ve alacaklarını etkin bir şekilde takip etmesini, aylık bazda finansal analizler yapmasını ve tedarikçi bakiyelerini yaşlandırarak (aging) finansal planlamaya katkıda bulunmasını sağlar.

**Amaç ve Hedefler:**
- SAP HANA veri tabanından tedarikçi ödeme verilerini güvenli ve hızlı bir şekilde çekmek
- Verileri yerel veritabanına senkronize etmek ve tutarlılığı sağlamak
- Tedarikçi bakiyelerini yaşlandırarak, hangi bakiyelerin hangi aylara ait olduğunu görselleştirmek
- İşletme yöneticilerine, finansal karar verme süreçlerinde kullanabilecekleri doğru ve güncel veriler sunmak
- Verilerin gerçek zamanlı olarak güncellenmesini ve izlenmesini mümkün kılmak

## Sistem Mimarisi

SupplierPayment API, modern ve ölçeklenebilir bir mimariye sahiptir. Sistem Django REST Framework üzerine inşa edilmiş olup, Celery ve WebSocket teknolojileri ile asenkron işlem yapabilme yeteneğine sahiptir.

### Ana Bileşenler:

1. **Django REST Framework**: API endpointlerini ve veri işleme mantığını sağlar
2. **PostgreSQL**: Yerel veri depolama için kullanılan veritabanı
3. **Celery**: Uzun süren veri çekme ve işleme görevleri için asenkron görev yöneticisi
4. **Redis**: Celery için mesaj broker'ı ve önbellek olarak kullanılır
5. **Channels**: WebSocket bağlantıları için Django entegrasyonu
6. **SAP HANA Connector**: SAP HANA veritabanına güvenli bağlantı sağlar

### Mimari Diyagram:

```
+---------------+           +-------------------+
| Client/Browser|<--------->| Django Web Server |
+---------------+           +-------------------+
                                     ^
                                     |
                +-----------+        |        +------------+
                | WebSockets|<------>|<------>| REST API   |
                +-----------+        |        +------------+
                                     |
                                     v
+------------+  +-------------+  +------------+  +------------+
| Redis      |<-| Celery      |<-| Django ORM |<-| PostgreSQL |
+------------+  +-------------+  +------------+  +------------+
                       ^
                       |
                       v
                +-------------+                 +------------+
                | HANA        |---------------->| SAP HANA DB|
                | Connector   |                 +------------+
                +-------------+
```

## Veri Modelleri

SupplierPayment API, iki ana veri modeli etrafında oluşturulmuştur: SupplierPayment ve ClosingInvoice.

### SupplierPayment Modeli

Tedarikçilere yapılan ödemeleri ve borçları temsil eder.

```python
class SupplierPayment(BaseModel):
    cari_kod = models.CharField(max_length=100, db_index=True)
    cari_ad = models.CharField(max_length=200, db_index=True)
    belge_tarih = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    belge_no = models.IntegerField(db_index=True)
    iban = models.TextField(blank=True, null=True)
    odemekosulu = models.CharField(max_length=100)
    borc = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    alacak = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    is_buffer = models.BooleanField(default=False, db_index=True)
```

Alanların açıklamaları:
- `cari_kod`: Tedarikçi kodu, SAP sistemindeki benzersiz tanımlayıcı
- `cari_ad`: Tedarikçi adı
- `belge_tarih`: İşlem tarihi (YYYY-MM-DD formatında)
- `belge_no`: Belge numarası
- `iban`: Tedarikçinin IBAN numarası
- `odemekosulu`: Ödeme koşulları
- `borc`: Borç tutarı (pozitif değer)
- `alacak`: Alacak tutarı (pozitif değer)
- `is_buffer`: Buffer kaydı olup olmadığı (geçmiş yıl verileri için true)

### ClosingInvoice Modeli

Tedarikçilerin kapanış bakiyelerini ve yaşlandırma bilgilerini temsil eder.

```python
class ClosingInvoice(BaseModel):
    cari_kod = models.CharField(max_length=100, unique=True, db_index=True)
    cari_ad = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    iban = models.TextField(blank=True, null=True)
    odemekosulu = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    monthly_balances = JSONField(null=True)
```

Alanların açıklamaları:
- `cari_kod`: Tedarikçi kodu
- `cari_ad`: Tedarikçi adı
- `iban`: Tedarikçinin IBAN numarası
- `odemekosulu`: Ödeme koşulları
- `current_balance`: Güncel toplam bakiye
- `monthly_balances`: Aylık bakiyelerin JSON formatında tutulduğu alan (yaşlandırma için)

## API Endpoint'leri

SupplierPayment API, çeşitli ihtiyaçlara cevap veren farklı endpointler sunar:

### 1. Tedarikçi Ödemeleri Yönetimi

- **GET/POST /api/v2/supplierpayment/supplier_payments/**
  - Tedarikçi ödemelerini listeler veya yeni ödeme ekler
  - Çeşitli filtreler destekler: cari_kod, is_buffer, date_from, date_to

### 2. HANA Veritabanı Senkronizasyonu

- **GET /api/v2/supplierpayment/fetch_hana_db/**
  - HANA veritabanından güncel verileri çeker ve yerel veritabanı ile senkronize eder
  - HANA'da olmayan kayıtları siler, değişen kayıtları günceller, yeni kayıtları ekler
  - İşlem sonunda kapanış faturalarını (ClosingInvoice) günceller

- **GET /api/v2/supplierpayment/fetch_hana_db_combined_service/**
  - Celery kullanarak arka planda veri senkronizasyonu başlatır
  - İşlem durumunu izlemek için task_id döndürür

- **GET /api/v2/supplierpayment/task_status/<task_id>/**
  - Celery görevinin durumunu ve ilerleme bilgisini sorgular

### 3. Kapanış Faturası Yönetimi

- **GET /api/v2/supplierpayment/local_db_closing_invoice/**
  - Tedarikçilerin kapanış faturalarını (aylık yaşlandırma bilgileri ile) getirir
  - Tüm tedarikçilerin bakiye durumunu ve aylık bakiye dağılımını gösterir

### 4. Durum Bilgisi

- **GET /api/v2/supplierpayment/last_updated_supplier_payment/**
  - Son güncelleme zamanını ve güncellenen kayıt bilgilerini döndürür
  - Sistemin güncellik durumunu kontrol etmek için kullanılır

## Veri Akışı ve İşleme Süreci

SupplierPayment API'nin çalışma mantığı ve veri akışı aşağıdaki gibidir:

### 1. HANA Veritabanı Veri Çekme

HANA veritabanından veri çekme işlemi, `fetch_hana_db_data` fonksiyonu tarafından gerçekleştirilir. Bu fonksiyon:

- JWT token ile yetkilendirme yaparak HANA DB'ye bağlanır
- Belirli bir SQL sorgusu ile tedarikçi ödeme verilerini çeker
- Verileri JSON formatında döndürür

### 2. Veri Senkronizasyonu

Çekilen veriler, yerel veritabanı ile karşılaştırılarak senkronize edilir:

- HANA DB'den gelen her kayıt için benzersiz anahtar oluşturulur (belge_no + cari_kod + belge_tarih)
- Yerel DB'deki kayıtlar da benzersiz anahtarlar ile eşleştirilir
- HANA'da olmayan kayıtlar silinir
- HANA'da olan ancak yerel DB'de olmayan kayıtlar eklenir
- Her iki veritabanında da olan kayıtlar güncellenir
- İşlem süresi ve sonuçları loglara kaydedilir

### 3. Kapanış Faturası Hesaplama

Veriler senkronize edildikten sonra, `SupplierPaymentSimulation` sınıfı tedarikçi bakiyelerini hesaplar:

- Her tedarikçi için toplam borç ve alacak hesaplanır
- Bakiyeler aylara göre dağıtılır (yaşlandırma)
- Sonuçlar ClosingInvoice modelinde güncellenir/oluşturulur

### 4. Canlı Bildirimler

İşlem sürecinde ve sonrasında, WebSocket üzerinden kullanıcılara bildirimler gönderilir:

- İşlem başlangıcı ve toplam kayıt sayısı
- İşlemin aşamaları ve ilerleme durumu
- İşlem sonucu ve özet bilgiler

## Performans Optimizasyonları

SupplierPayment API, büyük veri setleri ile verimli çalışabilmek için çeşitli optimizasyonlar içerir:

### 1. Veritabanı Optimizasyonları

- Kritik alanlarda veritabanı indeksleri (cari_kod, belge_tarih, borc, alacak)
- Karmaşık sorgular için özel indeksler (örn. GinIndex)
- Çoklu sorgular yerine toplu işlemler (bulk_create, bulk_update)

### 2. Bellek Kullanımı Optimizasyonları

- Tüm kayıtları belleğe almak yerine, sadece gerekli alanların seçilmesi (values_list)
- Büyük veri setleri için batch işleme (1000 kayıt grupları)
- Gereksiz model nesneleri oluşturmaktan kaçınma

### 3. Hız Optimizasyonları

- Asenkron işlemler için Celery kullanımı
- WebSocket ile gerçek zamanlı bildirimler
- Transaction atomikliği ile veri tutarlılığının korunması
- Bulk işlemler ile veritabanı etkileşimlerinin azaltılması

## Güvenlik Önlemleri

API, çeşitli güvenlik önlemleri ile korunmaktadır:

1. **Kimlik Doğrulama ve Yetkilendirme**
   - JWT (JSON Web Token) tabanlı kimlik doğrulama
   - İstemci isteklerinde Authorization header'ı zorunluluğu
   - Django REST Framework'ün permission_classes özelliği ile erişim kontrolü

2. **Veri Güvenliği**
   - Hassas verilerin şifrelenmesi
   - PostgreSQL'in güvenlik özellikleri ile veri koruması
   - Django ORM'nin SQL injection koruması

3. **Hata Yönetimi**
   - Detaylı hata loglaması
   - Hassas hata mesajlarının son kullanıcıya gösterilmemesi
   - Başarısız işlemlerde otomatik geri alma (transaction.atomic)

## Canlı Bildirim Sistemi

SupplierPayment API, Django Channels ve WebSockets kullanarak gerçek zamanlı bildirim sistemi içerir:

```python
class SupplierPaymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'supplierpayment_group'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
```

Bu sistem şunları sağlar:
- Veri çekme ve işleme sırasında gerçek zamanlı ilerleme bildirimleri
- Sistemin mevcut durumu hakkında güncel bilgiler
- İşlem tamamlandığında başarı/başarısızlık bildirimleri

## Kapanış Faturası Hesaplama Algoritması

Kapanış faturası hesaplama algoritması, tedarikçilerin borç ve alacak durumlarını analiz ederek, borçların hangi aylara ait olduğunu belirler. Bu algoritma, aşağıdaki adımları izler:

1. **Veri Hazırlığı**
   - Tüm tedarikçi kodları için, aylık borç ve alacak bilgileri toplanır
   - Her ay için işlemler tarih sırasına göre sıralanır

2. **Bakiye Hesaplama**
   - Tedarikçi bazında toplam borç ve alacak hesaplanır
   - Toplam borç, en eski tarihli alacaklardan başlayarak kapatılır
   - Kalan bakiye, aylara göre dağıtılır

3. **Yaşlandırma Analizi**
   - Son dört ay için ayrı ayrı bakiye hesaplanır
   - Dört aydan önceki dönem için toplam bakiye ("oncesi") hesaplanır
   - Sonuçlar, aylık bazda JSON formatında saklanır

```python
def generate_payment_list(self):
    payment_list = []
    current_date = datetime.now()
    
    # Son 4 ayı hesapla
    last_4_months = []
    temp_date = current_date
    
    for _ in range(4):
        last_4_months.append(temp_date.replace(day=1))
        if temp_date.month == 1:
            temp_date = temp_date.replace(year=temp_date.year-1, month=12, day=1)
        else:
            temp_date = temp_date.replace(month=temp_date.month-1, day=1)

    last_4_months_keys = [date.strftime("%Y-%m") for date in last_4_months]
    last_4_months_keys.reverse()

    for cari_kod, months in self.data.items():
        # Borç ve alacak hesaplamaları
        # Aylık bakiyelerin dağıtılması
        # ...

    return payment_list
```

Bu algoritma sayesinde, hangi tedarikçinin bakiyesinin hangi aylara ait olduğu belirlenebilir, böylece finansal planlamada öncelikli ödemeler için doğru kararlar alınabilir.

## Test ve Bakım

### Birim Testleri

SupplierPayment API için kapsamlı test senaryoları geliştirilmiştir:
- Model testleri
- API endpoint testleri
- Algoritma doğrulama testleri

### Bakım İşlemleri

Düzenli bakım işlemleri için yönetim komutları bulunmaktadır:

```bash
# Tüm verileri temizleme
python manage.py supp_delete_invalid_records --all

# Belirli bir cari kodun verilerini temizleme
python manage.py supp_delete_invalid_records --cari_kod=320.01.0001234

# Belirli bir tarihe ait verileri temizleme
python manage.py supp_delete_invalid_records --belge_tarih=2024-01-01

# Geçersiz kayıtları temizleme
python manage.py supp_delete_invalid_records --invalid
```

## Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. HANA DB Bağlantı Sorunları

**Sorun:** HANA veritabanına bağlanırken timeout veya yetkilendirme hataları.

**Çözüm:**
- Token'ın geçerli olduğundan emin olun
- Network bağlantısını kontrol edin
- HANA DB servisinin çalıştığını doğrulayın

### 2. Veri Tutarsızlıkları

**Sorun:** Yerel DB ve HANA DB arasında veri tutarsızlıkları.

**Çözüm:**
- Tüm verileri yeniden senkronize edin (`--all` parametresi ile)
- Kapanış faturası hesaplamalarını manuel olarak tetikleyin
- Log dosyalarını analiz edin

### 3. Performans Sorunları

**Sorun:** Büyük veri setlerinde yavaş işlem süresi.

**Çözüm:**
- Batch boyutlarını optimize edin
- Gereksiz indeksleri kaldırın
- Celery worker sayısını artırın
- PostgreSQL ayarlarını gözden geçirin

## Geliştirme Yol Haritası

SupplierPayment API için planlanan gelecek geliştirmeler:

1. **Grafik Raporlama Modülü**
   - Tedarikçi bakiyelerini görselleştiren grafikler
   - Aylık trend analizleri
   - Tedarikçi karşılaştırma raporları

2. **Tahmin Motoru**
   - Makine öğrenimi tabanlı ödeme davranışı tahminleri
   - Nakit akışı projeksiyonları
   - Ödeme önceliklendirme önerileri

3. **Mobil Uyumluluk**
   - Mobil cihazlar için optimize edilmiş API yanıtları
   - Push notification desteği
   - Offline çalışma modu

4. **Dış Sistem Entegrasyonları**
   - ERP sistemleri ile doğrudan entegrasyon
   - Banka API'leri ile bağlantı
   - Diğer finansal platformlar ile veri paylaşımı

---

**Belge Versiyonu:** 1.0  
**Son Güncelleme:** 8 Mart 2025  
**Hazırlayan:** Teknik Ekip