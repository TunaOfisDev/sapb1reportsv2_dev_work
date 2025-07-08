# ProductConfigSimulator: Kapsamlı Ürün Konfigürasyon Simülatörü

## Özet

ProductConfigSimulator, karmaşık ürün konfigürasyon sistemlerini test etmek, olası tüm varyantları keşfetmek ve veri kalitesini doğrulamak için geliştirilmiş bir Django REST Framework tabanlı uygulamadır. Bu araç, özellikle modüler üretim şirketlerinin ürün varyasyonlarını kapsamlı bir şekilde analiz etmelerine, eksik verileri tespit etmelerine ve ürün konfigürasyon sistemlerini optimize etmelerine olanak tanır.

## 1. Giriş

### 1.1 Genel Bakış

Günümüzde karmaşık ürün yapılandırma sistemleri, özellikle modüler üretim yapan şirketler için kritik öneme sahiptir. Bu sistemler, müşterilerin kendi ihtiyaçlarına göre özelleştirilmiş ürünler yapılandırmasına olanak tanırken, üreticilerin de üretim süreçlerini daha etkin yönetmesini sağlar. Ancak, bu tür sistemlerin doğru ve eksiksiz çalışmasını sağlamak, binlerce olası varyant kombinasyonu nedeniyle zorlu bir görevdir.

ProductConfigSimulator, bu zorluğu ele almak için geliştirilmiş, ürün konfigürasyon sistemlerini kapsamlı bir şekilde test eden ve simüle eden bir çözümdür. Belirli kategoriler, ürün grupları veya tek bir ürün modeli için tüm olası varyantları otomatik olarak oluşturarak, eksik verileri, hatalı konfigürasyonları ve veri tutarsızlıklarını tespit eder.

### 1.2 Problem Tanımı

Karmaşık ürün konfigürasyon sistemleri genellikle şu zorlukları beraberinde getirir:

- **Yüksek Karmaşıklık**: Binlerce olası ürün varyantı ve bunların arasındaki karmaşık ilişkiler
- **Eksik Veriler**: Ürün yapılandırma akışında kritik soruların seçeneklerinin eksik olması
- **Tutarsızlıklar**: Bağımlı kurallar, koşullu seçenekler ve fiyat çarpanları arasındaki potansiyel çelişkiler
- **Test Zorluğu**: Manuel olarak tüm olası varyantları test etmenin imkansızlığı
- **Kalite Güvencesi**: Üretim öncesi veri kalitesini sağlamanın zorluğu

### 1.3 Amaç ve Hedefler

ProductConfigSimulator'ın temel amaçları şunlardır:

- Ürün konfigürasyon sistemindeki veri eksikliklerini tespit etmek
- Olası tüm varyant kombinasyonlarını simüle etmek ve kaydetmek
- Potansiyel hataları ve çelişkileri belirlemek ve raporlamak
- Veri kalitesini ve tutarlılığını artırmak
- Ürün konfigürasyon sürecini optimize etmek

## 2. Sistem Mimarisi

### 2.1 Genel Mimari

ProductConfigSimulator, Django ve Django REST Framework üzerine inşa edilmiş modüler bir yapıya sahiptir. Uygulama, ana productconfig sisteminden bağımsız ancak onunla entegre çalışacak şekilde tasarlanmıştır. Bu modüler yapı, simülasyonların ana sistemi etkilemeden çalıştırılabilmesini sağlar.

```
+-------------------------+      +----------------------------+
|                         |      |                            |
|  ProductConfig          |<---->|  ProductConfigSimulator    |
|  (Ana Sistem)           |      |  (Simülasyon Sistemi)      |
|                         |      |                            |
+-------------------------+      +----------------------------+
         ^                                   ^
         |                                   |
         v                                   v
+-------------------------+      +----------------------------+
|                         |      |                            |
|  PostgreSQL             |<---->|  Celery + Redis            |
|  (Veritabanı)           |      |  (Asenkron İşlem Yönetimi) |
|                         |      |                            |
+-------------------------+      +----------------------------+
```

### 2.2 Bileşenler

ProductConfigSimulator aşağıdaki temel bileşenlerden oluşur:

#### 2.2.1 Model Katmanı

- **SimulationJob**: Simülasyon işlerini ve durumlarını yönetir
- **SimulatedVariant**: Simülasyon sonucunda oluşturulan varyantları saklar
- **SimulationError**: Simülasyon sırasında tespit edilen hataları kaydeder

#### 2.2.2 Servis Katmanı

- **SimulatorService**: Temel simülasyon mantığını içerir
- **Çeşitli yardımcı hizmetler**: Varyant oluşturma, soru-cevap işleme, vb.

#### 2.2.3 API Katmanı

- RESTful API uç noktaları
- Serializers
- API kimlik doğrulama ve izinler

#### 2.2.4 Asenkron İş Yönetimi

- Celery görevleri
- Redis arka plan iş sırası
- İş durumu izleme

#### 2.2.5 Admin Arayüzü

- Özelleştirilmiş admin paneli
- Simülasyon yönetimi
- Hata raporları ve düzeltme araçları

### 2.3 Dosya Yapısı

ProductConfigSimulator'ın dosya yapısı, işlevselliğin modüler organizasyonunu yansıtır:

```
backend/productconfig_simulator/
├── admin/
│   ├── filters.py
│   ├── __init__.py
│   └── simulator_admin.py
├── api/
│   ├── __init__.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── management/
│   └── commands/
│       └── run_simulation.py
├── migrations/
├── models/
│   ├── __init__.py
│   └── simulator_models.py
├── services/
│   ├── __init__.py
│   └── simulator_service.py
├── templates/
│   └── admin/
│       └── productconfig_simulator/
│           └── productconfig_simulator.html
├── utils/
│   ├── __init__.py
│   ├── simulators.py
│   └── validators.py
├── __init__.py
├── apps.py
├── settings.py
├── signals.py
├── tasks.py
└── tests.py
```

## 3. Temel İşlevsellik

### 3.1 Simülasyon Seviyesi Seçimi

ProductConfigSimulator, çeşitli seviyelerde simülasyon yapabilme esnekliği sunar:

- **Marka Seviyesi**: Belirli bir markaya ait tüm ürün grupları, kategoriler ve modeller
- **Ürün Grubu Seviyesi**: Belirli bir ürün grubuna ait tüm kategoriler ve modeller
- **Kategori Seviyesi**: Belirli bir kategoriyi içeren tüm ürün modelleri
- **Ürün Modeli Seviyesi**: Tek bir ürün modeli için tüm olası varyantlar

Bu esneklik, simülasyonun kapsamını kontrol etmeye ve kaynak kullanımını optimize etmeye olanak tanır.

### 3.2 Simülasyon Algoritması

Simülasyon algoritması, aşağıdaki adımları izler:

1. **Hedef Belirleme**: Seçilen seviyeye göre simüle edilecek ürün modellerini belirleme
2. **Veri Doğrulama**: Her ürün modeli için soruları ve seçenekleri kontrol etme
3. **Varyant Oluşturma**: Rekursif olarak tüm soru-cevap kombinasyonlarını oluşturma
4. **Bağımlı Kural Değerlendirmesi**: Soruların görünürlük kurallarını uygulama
5. **Koşullu Seçenek İşleme**: Koşullu seçenekleri doğru şekilde ele alma
6. **Varyant Kod Oluşturma**: Her kombinasyon için varyant kodu ve açıklaması üretme
7. **Sonuçları Saklama**: Oluşturulan varyantları veritabanına kaydetme

### 3.3 Hata Tespiti ve Raporlama

Sistem, aşağıdaki tipte hataları tespit eder ve raporlar:

- **Seçeneği Olmayan Sorular**: Soru tanımlanmış ancak seçenek mevcut değil
- **Bağımlı Kural Hataları**: Çelişkili veya eksik bağımlı kurallar
- **Koşullu Seçenek Hataları**: Koşullu seçenek tanımlarındaki sorunlar
- **Fiyat Çarpan Hataları**: Çelişkili veya eksik fiyat çarpanları
- **İşlem Hataları**: Simülasyon sırasında oluşan diğer hatalar

Her hata tipi, düzeltici eylem için gerekli tüm bilgilerle birlikte detaylı olarak raporlanır.

### 3.4 Performans Optimizasyonu

Büyük veri setleri ile çalışırken performansı optimize etmek için uygulama:

- **Asenkron İşleme**: Uzun süren simülasyonları arka planda Celery ile yürütür
- **Veritabanı Optimizasyonu**: Toplu işlemler ve verimli sorgular kullanır
- **Bellek Yönetimi**: Büyük veri setlerini etkili şekilde işlemeyi sağlar
- **Limit Kontrolü**: Her model için maksimum varyant sayısı sınırlandırılabilir
- **Kademeli İşleme**: Sonuçlar elde edildikçe kaydedilir, tam tamamlanma beklenmez

## 4. Kullanıcı Arayüzü

### 4.1 Admin Paneli

ProductConfigSimulator, aşağıdaki özellikleri içeren kapsamlı bir admin paneli sunar:

- **Simülasyon Oluşturma**: Çeşitli seviyelerde simülasyon başlatma
- **Durum İzleme**: Devam eden simülasyonların durumunu görüntüleme
- **Sonuç Görüntüleme**: Oluşturulan varyantları filtreleme ve inceleme
- **Hata Raporları**: Tespit edilen hataları kategoriler halinde görüntüleme
- **Düzeltme Araçları**: Hatalı verileri doğrudan düzeltme bağlantıları

### 4.2 API Uç Noktaları

RESTful API, aşağıdaki temel uç noktaları sağlar:

- `/api/simulations/`: Simülasyon işlerini listeleme ve oluşturma
- `/api/simulations/<id>/`: Belirli bir simülasyonun detaylarını görüntüleme
- `/api/simulations/<id>/status/`: Simülasyon durumunu kontrol etme
- `/api/simulations/<id>/variants/`: Bir simülasyonun varyantlarını listeleme
- `/api/simulations/<id>/errors/`: Bir simülasyonun hata raporlarını görüntüleme
- `/api/export/<id>/`: Simülasyon sonuçlarını CSV veya JSON olarak dışa aktarma

## 5. Entegrasyon

### 5.1 ProductConfig Sistemi ile Entegrasyon

ProductConfigSimulator, ana ProductConfig sistemiyle aşağıdaki şekilde entegre olur:

- **Model Referansları**: Ana sistemin modellerine doğrudan referanslar
- **Servis Paylaşımı**: Gerektiğinde ana sistemin servislerini kullanma
- **Veri Bütünlüğü**: Ana sistem verilerini değiştirmeden okuma

### 5.2 Veritabanı Entegrasyonu

Simülatör, PostgreSQL veritabanını ana sistemle paylaşır, ancak kendi tablolarını kullanır:

- **productconfig_simulator_simulationjob**: Simülasyon işleri
- **productconfig_simulator_simulatedvariant**: Simüle edilmiş varyantlar
- **productconfig_simulator_simulationerror**: Simülasyon hataları

### 5.3 Asenkron İşlem Entegrasyonu

Uzun süren simülasyonlar için Celery ve Redis entegrasyonu:

- **Celery Görevleri**: Arka planda çalıştırılan simülasyon işleri
- **Redis Arka Plan İş Sırası**: İş kuyruğu yönetimi
- **Durum İzleme**: Görev durumunun gerçek zamanlı izlenmesi

## 6. Simülasyon Örnekleri

### 6.1 Kategori Seviyesinde Simülasyon

Varsayalım "Operasyonel Tekil Masalar" kategorisi için bir simülasyon başlatmak istiyoruz:

1. Admin panelinde "Yeni Simülasyon" sayfasına gidilir
2. "Kategori Bazında" seçeneği işaretlenir
3. Marka olarak "TUNA" seçilir
4. Ürün Grubu olarak "TUNA - MASA" seçilir
5. Kategori olarak "Operasyonel Tekil Masalar" seçilir
6. Varyant limiti 100 olarak ayarlanır
7. Simülasyon başlatılır

Sistem şunları yapar:
- Kategori altındaki tüm ürün modellerini belirler
- Her model için soruları ve seçenekleri kontrol eder
- Seçeneği olmayan sorular varsa raporlar
- Her ürün modeli için varyantları oluşturur
- Sonuçları ve hataları kaydeder

### 6.2 Ürün Modeli Seviyesinde Simülasyon

Tek bir ürün modeli için daha detaylı bir simülasyon:

1. Admin panelinde "Yeni Simülasyon" sayfasına gidilir
2. "Ürün Modeli Bazında" seçeneği işaretlenir
3. İlgili marka, ürün grubu ve kategori seçilir
4. Özel ürün modeli seçilir
5. Varyant limiti 1000 olarak ayarlanır (daha kapsamlı test için)
6. Simülasyon başlatılır

Sistem şunları yapar:
- Ürün modeli için tüm soruları belirler
- Seçenekleri ve bağımlı kuralları kontrol eder
- Detaylı bir şekilde tüm olası varyantları oluşturur
- Her varyant için varyant kodu, açıklaması ve fiyatını hesaplar
- Eski bileşen kodlarını üretir
- Tüm sonuçları ve potansiyel hataları kaydeder

## 7. Teknik Özellikler

### 7.1 Teknoloji Yığını

ProductConfigSimulator aşağıdaki teknolojileri kullanır:

- **Backend**: Django 3.2+, Django REST Framework 3.13+
- **Veritabanı**: PostgreSQL 13+
- **Asenkron İşlemler**: Celery 5.2+, Redis 6.2+
- **Frontend**: Django Admin Panel (Özelleştirilmiş)
- **API Formatları**: JSON, CSV
- **Test**: pytest, coverage

### 7.2 Ölçeklenebilirlik

Sistem, aşağıdaki ölçeklendirme özelliklerine sahiptir:

- **Yatay Ölçeklendirme**: Celery worker'larının sayısını artırarak işlem kapasitesini genişletme
- **Veritabanı Ölçeklendirme**: Büyük veri setleri için veritabanı optimizasyonu
- **Modüler Mimari**: Sistemin belirli bileşenlerini bağımsız olarak ölçeklendirme imkanı

### 7.3 Güvenlik

Simülatör, güvenliği sağlamak için şu önlemleri içerir:

- **Kimlik Doğrulama**: Django kimlik doğrulama sistemi
- **Yetkilendirme**: İzin tabanlı erişim kontrolü
- **API Güvenliği**: JWT tabanlı token doğrulama
- **Veri Doğrulama**: Giriş verileri için kapsamlı doğrulama

## 8. Kullanım Senaryoları

ProductConfigSimulator'ın kullanılabileceği çeşitli senaryolar:

### 8.1 Veri Kalitesi Kontrolü

- Yeni ürün modelleri eklendikten sonra veri bütünlüğünü doğrulama
- Seçeneği olmayan soruları tespit etme ve düzeltme
- Bağımlı kuralların tutarlılığını kontrol etme

### 8.2 Katalog Oluşturma

- Tüm olası ürün varyantlarını oluşturma
- Katalog için varyant kodları ve açıklamalarını otomatik üretme
- Fiyat listesi oluşturma

### 8.3 Test ve Kalite Güvencesi

- Ürün konfigürasyon sistemindeki hataları tespit etme
- Kullanıcı deneyimini etkileyebilecek sorunları önceden belirleme
- Ürünü piyasaya sürmeden önce veri tamlığını doğrulama

### 8.4 Sistem Optimizasyonu

- Sistem performansını analiz etme
- Konfigürasyon sürecini optimize etme
- Kullanıcı deneyimini geliştirme

## 9. Kullanım Kılavuzu

### 9.1 Kurulum

```bash
# Sanal ortam oluşturma
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Bağımlılıkları yükleme
pip install -r requirements.txt

# Veritabanı migrasyonlarını uygulama
python manage.py migrate

# Geliştirme sunucusunu başlatma
python manage.py runserver
```

### 9.2 Celery Worker Başlatma

```bash
# Redis'i başlatma
docker run -d -p 6379:6379 redis

# Celery worker'ı başlatma
celery -A mainapp worker -l info
```

### 9.3 Simülasyon Oluşturma

1. Django admin panelini açın: `http://localhost:8000/admin/`
2. "ProductConfigSimulator" bölümüne gidin
3. "Simülasyon İşleri" sayfasından "Simülasyon Başlat" düğmesine tıklayın
4. İstediğiniz seviyeyi ve hedefleri seçin
5. "Simülasyonu Başlat" düğmesine tıklayın
6. Simülasyon durumunu izleyin

### 9.4 Sonuçları Görüntüleme

1. Simülasyon işleri listesine gidin
2. İlgili simülasyona tıklayın
3. "Simüle Edilmiş Varyantlar" bölümünde sonuçları görüntüleyin
4. "Hata Raporları" bölümünde tespit edilen sorunları inceleyin
5. Sonuçları CSV veya JSON olarak dışa aktarmak için ilgili düğmeyi kullanın

## 10. Sonuç

ProductConfigSimulator, karmaşık ürün konfigürasyon sistemlerini test etmek, tüm olası varyantları keşfetmek ve veri kalitesini doğrulamak için güçlü bir araçtır. Modern web teknolojileri kullanılarak geliştirilen bu uygulama, özellikle modüler üretim şirketlerinin veri kalitesi sorunlarını proaktif olarak tespit etmelerine ve çözmelerine yardımcı olur.

Asenkron işleme, detaylı hata raporlama ve kapsamlı API desteği gibi özellikleriyle ProductConfigSimulator, ürün konfigürasyon süreçlerinin verimliliğini artırmaya ve kullanıcı deneyimini iyileştirmeye yönelik değerli bir çözüm sunar.

---

**Ek Bilgiler**

- Sürüm: 1.0.0
- Yazarlar: [Şirket Adı] Yazılım Geliştirme Ekibi
- Lisans: [Lisans Bilgisi]
- İletişim: [İletişim Bilgileri]