# ============================================================================
# API TASARIM BELGESİ (WHITE PAPER) - formforgeapi
# ============================================================================
# Not: Bu belge, `sapb1reportsv2` projesi için oluşturulan her yeni API
# modülünün kimliğini, sözleşmesini ve entegrasyon adımlarını tanımlayan
# standart şablondur. AI, bu şablonu kullanıcı prompt'una göre doldurur.
# ============================================================================

## 1. API Künyesi (Özet Kart)

| Alan                     | Bilgi / Değer                                                                          |
| ------------------------ | -------------------------------------------------------------------------------------- |
| **Proje** | `sapb1reportsv2`                                                                       |
| **Modül Adı** | `formforgeapi`                                                                        |
| **Sürüm** | `v1.0.0`                                                                               |
| **Oluşturan** | `Selim Koçak`                                                                             |
| **Sorumlu Ekip/Kişi** | `Selim & Tars`                                                         |
| **İlk Yayın Tarihi** | `2025-07-29`                                                                           |
| **Kritik Bağımlılıklar** | `Django REST Framework`, `Celery`, `drf-spectacular`, `loguru`                         |
| **Harici Sistemler** | `PostgreSQL`, `Redis`, `SAP HANA DB`, `Logo ERP DB` (varsa)                               |

---

## 2. İş Gerekçesi ve Kapsam

> Bu modülün amacı, son kullanıcıların kodlama bilgisi olmadan, sürükle-bırak arayüzüyle kendi veri toplama formlarını oluşturmasını sağlamaktır. Kullanıcılar, forma metin, sayı, tarih gibi farklı tiplerde alanlar ekleyebilmeli, bu alanları zorunlu kılabilmeli ve veri listeleme ekranında hangi alanların görüneceğini (`is_master`) belirleyebilmelidir.

---

## 3. Mimari ve Veri Akışı

Bu modül, `sapb1reportsv2` projesinin genel mimarisine (`View -> Service -> Model/External API`) uygun olarak çalışır.

```mermaid
flowchart TD
    subgraph Frontend
        A[React UI] -- JWT Request --> B{axiosClient};
    end

    subgraph "Backend (Django: sapreports)"
        B -- /api/v1/formforgeapi/ --> C{FormForgeAPIViewSet};
        C -- Çağırır --> D[FormForgeAPIService];
        D -- İşler --> E[Veritabanı (PostgreSQL)];
        D -- Çağırır --> F[Harici Servisler];
    end

    subgraph "Arka Plan (Async)"
        G[Celery Beat] -- Tetikler --> H[FormForgeAPITask];
        H -- İşler --> F;
        H -- Sonuçları Yazar --> E;
    end

    subgraph "Harici Sistemler"
        F --- I[SAP HANA];
        F --- J[Logo ERP];
        F --- K[Diğer API'ler];
    end
`

-----

## 4. Veri Modeli ve Şeması

> Bu bölüm, modülün kullandığı ana Django modellerini, alanlarını, tiplerini ve ilişkilerini tanımlar. `Department`, `Form`, `FormField`, `FormSubmission` ve `SubmissionValue` olmak üzere beş model bulunmaktadır. `FormField` modeli, farklı alan tiplerini destekler ve `is_master` alanı ile hangi alanların veri listeleme ekranında gösterileceğini belirler. `SubmissionValue` modeli, form gönderimlerindeki değerleri saklar.

#### 4.1. Django Modeli (`models.py`)

```python
# Örnek Model Yapısı
class Form(models.Model):
    # ... model alanları buraya ...


#### 4.2. Serializer Şemaları (API Payloads)

  * **Listeleme/Detay Yanıtı (GET - Response)**
    ```json
    {
      "success": true,
      "data": {
        "id": 1,
        "title": "Form Başlığı",
        "description": "Açıklama",
        "department": 1,
        "fields": [
            {"label": "Ad", "field_type": "text", "is_required": true, "is_master": true},
            {"label": "Soyad", "field_type": "text", "is_required": true, "is_master": true}
        ]
      },
      "message": "Kayıt başarıyla getirildi."
    }
    
  * **Oluşturma/Güncelleme İsteği (POST/PUT - Request)**
    ```json
    {
      "title": "Yeni Form Başlığı",
      "description": "Yeni Açıklama",
      "department": 2,
      "fields": [
          {"label": "Email", "field_type": "text", "is_required": true, "is_master": true}
      ]
    }
    

-----

## 5. API Endpoints Sözleşmesi

| HTTP | URL                               | Yetki Sınıfı         | Kısa Açıklama                                       | Örnek Yanıt (Başarılı)                       |
| :--- | :-------------------------------- | :------------------- | :-------------------------------------------------- | :------------------------------------------- |
| GET  | `/api/v1/formforgeapi/forms/`          | `IsAuthenticated`    | Tüm formları listeler (pagination aktif).          | `{ "success": true, "data": [...] }`         |
| GET  | `/api/v1/formforgeapi/forms/{id}/`     | `IsAuthenticated`    | Belirtilen ID'ye sahip tek bir formu getirir.       | `{ "success": true, "data": {...} }`         |
| POST | `/api/v1/formforgeapi/forms/`          | `IsAuthenticated`    | Yeni bir form oluşturur.                           | `{ "success": true, "data": {...}, "message": "Başarıyla oluşturuldu."}` |
| PUT  | `/api/v1/formforgeapi/forms/{id}/`     | `IsAuthenticated`    | Mevcut bir formu günceller.                         | `{ "success": true, "data": {...}, "message": "Başarıyla güncellendi."}` |
| POST | `/api/v1/formforgeapi/forms/custom/`   | `IsAdminUser`        |  Özel bir aksiyon gerçekleştirir. | `{ "success": true, "message": "İşlem tamamlandı." }` |


-----

## 6. Zamanlanmış Görevler (Celery Tasks)

> Bu modülde tanımlanmış bir Celery görevi bulunmamaktadır.

| Görev ID (`name`)             | Tanım                                       | Zamanlama (Örnek)           |
| :---------------------------- | :------------------------------------------ | :-------------------------- |


-----

## 7. Yetkilendirme ve Güvenlik

  * **Varsayılan Yetki:** Tüm endpoint'ler, geçerli bir JWT token'ı gerektiren `rest_framework.permissions.IsAuthenticated` ile korunur.
  * **Yönetici Yetkisi:** Veri senkronizasyonu veya özel işlemler gibi hassas endpoint'ler, yalnızca `staff` kullanıcılara izin veren `rest_framework.permissions.IsAdminUser` ile korunur.
  * **Hassas Veri:** `.env` dosyasında saklanan `SECRET_KEY`, `HANADB_PASS` gibi hassas bilgilere kod içerisinden asla doğrudan erişilmez.

-----

## 8. Kurulum ve Proje Entegrasyonu

> Bu bölüm, `formforgeapi` modülünün `sapb1reportsv2` projesine nasıl entegre edileceğini açıklar.

1.  **Uygulamayı Ekle:** `backend/sapreports/settings.py` dosyasındaki `INSTALLED_APPS` listesine aşağıdaki satırı ekleyin:
    ```python
    'formforgeapi.apps.FormforgeapiConfig',
    
2.  **URL'leri Ekle:** `backend/sapreports/urls.py` dosyasındaki `urlpatterns` listesine aşağıdaki satırı ekleyin:
    ```python
    path('api/v1/formforgeapi/', include('formforgeapi.api.urls')),
    
3.  **Celery Görevlerini Ekle (varsa):** `backend/sapreports/settings.py` dosyasındaki `CELERY_IMPORTS` listesine aşağıdaki satırı ekleyin:
    ```python
    'formforgeapi.tasks',
    
4.  **Veritabanını Güncelle:** Terminalde aşağıdaki komutları çalıştırın:
    ```bash
    python manage.py makemigrations formforgeapi
    python manage.py migrate
    

-----

## 9. Riskler ve Notlar

> Şu anda bu API ile ilgili bilinen bir risk bulunmamaktadır. Form gönderim verileri, PostgreSQL veritabanında saklanır ve API aracılığıyla erişilebilir.

<!-- end list -->
