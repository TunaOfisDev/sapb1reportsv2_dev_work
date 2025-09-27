# backend/<module_name>/whitepaper_api.md
### ✅ **Yeni `/var/www/sapb1reportsv2/zcontext_prompt/whitepaper_api.md` içeriği:**
# ============================================================================
# API TASARIM BELGESİ (WHITE PAPER) - <module_name>
# ============================================================================
# Not: Bu belge, `sapb1reportsv2` projesi için oluşturulan her yeni API
# modülünün kimliğini, sözleşmesini ve entegrasyon adımlarını tanımlayan
# standart şablondur. AI, bu şablonu kullanıcı prompt'una göre doldurur.
# ============================================================================

## 1. API Künyesi (Özet Kart)

| Alan                     | Bilgi / Değer                                                                          |
| ------------------------ | -------------------------------------------------------------------------------------- |
| **Proje** | `sapb1reportsv2`                                                                       |
| **Modül Adı** | `<module_name>`                                                                        |
| **Sürüm** | `v1.0.0`                                                                               |
| **Oluşturan** | `<author>`                                                                             |
| **Sorumlu Ekip/Kişi** | `<team_or_person_responsible>`                                                         |
| **İlk Yayın Tarihi** | `YYYY-MM-DD`                                                                           |
| **Kritik Bağımlılıklar** | `Django REST Framework`, `Celery`, `drf-spectacular`, `loguru`                         |
| **Harici Sistemler** | `PostgreSQL`, `Redis`, `SAP HANA DB`, `Logo ERP DB` (varsa)                               |

---

## 2. İş Gerekçesi ve Kapsam

> **[AI Dolduracak]**
> *Bu bölüm, API'nin hangi iş problemini çözdüğünü, hedefini ve kapsamını 1-2 paragrafta net bir şekilde açıklar.*
> *Örnek: "stockforecast API'si, SAP HANA'dan alınan satış verilerini kullanarak geleceğe yönelik stok tahminleri üretir. Amacı, yetersiz veya fazla stok riskini azaltarak envanter yönetimini optimize etmektir..."*

---

## 3. Mimari ve Veri Akışı

Bu modül, `sapb1reportsv2` projesinin genel mimarisine (`View -> Service -> Model/External API`) uygun olarak çalışır.

```mermaid
flowchart TD
    subgraph Frontend
        A[React UI] -- JWT Request --> B{axiosClient};
    end

    subgraph "Backend (Django: sapreports)"
        B -- /api/v1/<module_name>/ --> C{<ModuleName>ViewSet};
        C -- Çağırır --> D[<ModuleName>Service];
        D -- İşler --> E[Veritabanı (PostgreSQL)];
        D -- Çağırır --> F[Harici Servisler];
    end

    subgraph "Arka Plan (Async)"
        G[Celery Beat] -- Tetikler --> H[<ModuleName>Task];
        H -- İşler --> F;
        H -- Sonuçları Yazar --> E;
    end

    subgraph "Harici Sistemler"
        F --- I[SAP HANA];
        F --- J[Logo ERP];
        F --- K[Diğer API'ler];
    end
````

-----

## 4\. Veri Modeli ve Şeması

> **[AI Dolduracak]**
> *Bu bölüm, modülün kullandığı ana Django modellerini, alanlarını, tiplerini ve ilişkilerini tanımlar.*

#### 4.1. Django Modeli (`models.py`)

```python
# Örnek Model Yapısı
class <ModuleName>(models.Model):
    # ... model alanları buraya ...
```

#### 4.2. Serializer Şemaları (API Payloads)

  * **Listeleme/Detay Yanıtı (GET - Response)**
    ```json
    {
      "success": true,
      "data": {
        "id": 1,
        "alan_1": "değer",
        "alan_2": 123.45
      },
      "message": "Kayıt başarıyla getirildi."
    }
    ```
  * **Oluşturma/Güncelleme İsteği (POST/PUT - Request)**
    ```json
    {
      "alan_1": "yeni değer",
      "alan_2": 543.21
    }
    ```

-----

## 5\. API Endpoints Sözleşmesi

| HTTP | URL                               | Yetki Sınıfı         | Kısa Açıklama                                       | Örnek Yanıt (Başarılı)                       |
| :--- | :-------------------------------- | :------------------- | :-------------------------------------------------- | :------------------------------------------- |
| GET  | `/api/v1/<module_name>/`          | `IsAuthenticated`    | Tüm kayıtları listeler (pagination aktif).          | `{ "success": true, "data": [...] }`         |
| GET  | `/api/v1/<module_name>/{id}/`     | `IsAuthenticated`    | Belirtilen ID'ye sahip tek bir kaydı getirir.       | `{ "success": true, "data": {...} }`         |
| POST | `/api/v1/<module_name>/`          | `IsAuthenticated`    | Yeni bir kayıt oluşturur.                           | `{ "success": true, "data": {...}, "message": "Başarıyla oluşturuldu."}` |
| PUT  | `/api/v1/<module_name>/{id}/`     | `IsAuthenticated`    | Mevcut bir kaydı günceller.                         | `{ "success": true, "data": {...}, "message": "Başarıyla güncellendi."}` |
| POST | `/api/v1/<module_name>/custom/`   | `IsAdminUser`        | **[AI Dolduracak]** Özel bir aksiyon gerçekleştirir. | `{ "success": true, "message": "İşlem tamamlandı." }` |

-----

## 6\. Zamanlanmış Görevler (Celery Tasks)

> **[AI Dolduracak]**
> *Bu bölüm, modülün içerdiği Celery görevlerini, ne işe yaradıklarını ve zamanlamalarını listeler.*

| Görev ID (`name`)             | Tanım                                       | Zamanlama (Örnek)           |
| :---------------------------- | :------------------------------------------ | :-------------------------- |
| `<module_name>.run_sync_task` | Harici sistemden veri çeker ve DB'yi günceller. | Her gece 03:00 (`0 3 * * *`) |

-----

## 7\. Yetkilendirme ve Güvenlik

  * **Varsayılan Yetki:** Tüm endpoint'ler, geçerli bir JWT token'ı gerektiren `rest_framework.permissions.IsAuthenticated` ile korunur.
  * **Yönetici Yetkisi:** Veri senkronizasyonu veya özel işlemler gibi hassas endpoint'ler, yalnızca `staff` kullanıcılara izin veren `rest_framework.permissions.IsAdminUser` ile korunur.
  * **Hassas Veri:** `.env` dosyasında saklanan `SECRET_KEY`, `HANADB_PASS` gibi hassas bilgilere kod içerisinden asla doğrudan erişilmez.

-----

## 8\. Kurulum ve Proje Entegrasyonu

> **[AI Dolduracak]**
> *Bu bölüm, yeni modülün `sapb1reportsv2` projesine nasıl entegre edileceğine dair adımları içerir.*

1.  **Uygulamayı Ekle:** `backend/sapreports/settings.py` dosyasındaki `INSTALLED_APPS` listesine aşağıdaki satırı ekleyin:
    ```python
    '<module_name>.apps.<ModuleName>Config',
    ```
2.  **URL'leri Ekle:** `backend/sapreports/urls.py` dosyasındaki `urlpatterns` listesine aşağıdaki satırı ekleyin:
    ```python
    path('api/v1/<module_name>/', include('<module_name>.api.urls')),
    ```
3.  **Celery Görevlerini Ekle (varsa):** `backend/sapreports/settings.py` dosyasındaki `CELERY_IMPORTS` listesine aşağıdaki satırı ekleyin:
    ```python
    '<module_name>.tasks',
    ```
4.  **Veritabanını Güncelle:** Terminalde aşağıdaki komutları çalıştırın:
    ```bash
    python manage.py makemigrations <module_name>
    python manage.py migrate
    ```

-----

## 9\. Riskler ve Notlar

> **[AI Dolduracak]**
> *Bu bölüm, API'nin çalışmasıyla ilgili potansiyel riskleri ve önemli notları listeler.*

  * **Risk:** Harici SAP HANA veritabanı bağlantısının kopması.
      * **Önlem:** Celery görevlerinde `autoretry_for` mekanizması ile bağlantı hatalarında görev otomatik olarak yeniden denenir.
  * **Not:** Bu API tarafından oluşturulan veriler, periyodik olarak çalışan Celery görevleri ile güncellenir. Verinin anlık değil, son senkronizasyon zamanındaki durumu yansıttığı unutulmamalıdır.

<!-- end list -->
