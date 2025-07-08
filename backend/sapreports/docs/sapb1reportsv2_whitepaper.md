🚀 **SAPB1ReportsV2** projesi, kurumsal ERP sistemleri olan **SAP Business One (HANA)** ve **Logo ERP** veritabanları ile entegre çalışan, **raporlama**, **analiz**, **görev yönetimi** ve **otomasyon** işlevlerini tek bir modern web arayüzü üzerinden sağlayan bir kurumsal uygulamadır.

---

## 🔧 **Teknik ve Mantıksal Yapı Özeti**

### 1. 🎯 **Projenin Amacı**

Kurumsal şirketlerin ihtiyaç duyduğu:

* Anlık ve dönemsel **finansal raporlar**
* **Stok**, **sipariş**, **satış** ve **maliyet analizleri**
* **Görev otomasyonu** (rapor gönderimi, veri çekme, log temizleme vs.)
* Dosya paylaşımı ve ERP'den gelen dosyaların düzenlenmesi
  için tek merkezli, güvenli ve esnek bir çözüm sunmak.

---

### 2. 🧠 **Mantıksal Katmanlar**

#### ✅ **Veri Katmanı**

* **SAP B1 HANA DB**: Canlı satış, sipariş, müşteri ve finans verileri.
* **Logo ERP DB**: Alternatif ERP sisteminden gelen ticari veriler.
* **PostgreSQL**: Tüm uygulama verileri (kullanıcılar, görev tanımları, dosya kayıtları, lokal veri kopyaları) burada tutulur.
* **Redis**: Hızlı cacheleme ve Celery kuyruk yönetimi.

---

#### ✅ **İşlem Katmanı (Backend - Django REST)**

* Django REST Framework ile yazılmış çok modüllü bir backend.
* **API** servisleri ile frontend’e veri sağlar.
* **Celery** ile zamanlanmış görevler (beat), arka plan işlemleri ve mail raporları.
* **WebSocket** (Django Channels) ile anlık bildirim/geri bildirim sağlar.
* **Loglama**, **hata yönetimi** ve **JWT kimlik doğrulama** sistemleri ile kurumsal güvenlik.

---

#### ✅ **Kullanıcı Katmanı (Frontend - React)**

* **React.js** ile yazılmış, dinamik ve modüler UI.
* Rapor tabloları için **react-table**, **react-pivottable** ve **chart.js** kullanılır.
* JWT token ile giriş yapar, Redux-persist ile session yönetir.
* Kullanıcılar veri filtreler, export alır, görsel raporları anında görüntüler.

---

### 3. 🗂️ **Uygulama Modülleri (Örnekler)**

| Modül Adı             | İşlevi                                                              |
| --------------------- | ------------------------------------------------------------------- |
| `salesbudgeteur`      | Satıcı bazlı EUR cinsinden yıllık/aylık satış-hedef analiz raporu   |
| `filesharehub_v2`     | Ağ klasörlerindeki dosyaların takibi, versiyon ve paylaşım yönetimi |
| `report_orchestrator` | Celery beat ile raporları zamanlı çalıştırma ve otomatik mail atma  |
| `hanadbcon`           | SAP B1 HANA veritabanından veri çekme işlemleri                     |
| `logodbcon`           | Logo ERP veritabanı bağlantısı ve veri işlemleri                    |
| `bomcostmanager`      | Ürün ağacı (BOM) ve mamul maliyet analizleri                        |
| `taskorchestrator`    | Görev tanımları, zamanlayıcı senkronizasyon ve orkestrasyon mantığı |
| `authcentral`         | Kullanıcı yönetimi, oturum, izin ve rol sistemi                     |

---

### 4. 🔄 **Veri Akışı Örneği**

```plaintext
[ SAP HANA / Logo DB ]
        │
        ▼
[ Celery Görevi: fetch_hana_data ]
        │
        ▼
[ PostgreSQL'e veri yazılır ]
        │
        ▼
[ REST API (örn. /api/v1/salesbudget-eur) ]
        │
        ▼
[ React Tablo: SalesBudgetEURTable ]
        │
        ▼
[ Kullanıcı filtreler, tabloyu görür, Excel alır ]
```

---

### 5. 🔒 **Kurumsal Güvenlik ve Entegrasyonlar**

* CSRF, JWT, CORS ayarları ile koruma
* E-posta servisi (Yandex SMTP) üzerinden otomatik rapor gönderimi
* GitHub, YouTube API, OpenAI entegrasyonu (eğitim, dökümantasyon, AI analiz)
* Samba entegrasyonu ile ağ klasörlerine erişim (ör. `/mnt/gorseller`)

---

## ✅ Özetle:

> **sapb1reportsv2** = SAP + LOGO + PostgreSQL + React tabanlı **kurumsal raporlama ve otomasyon platformudur**.
> ERP sistemlerinden gelen verileri toplayarak, kullanıcı dostu bir web panelde analiz etmenizi, raporlamanızı ve otomatikleştirmenizi sağlar.