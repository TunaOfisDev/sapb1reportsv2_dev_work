Harika Selim, işte sana sade ama fonksiyonel bir teknik whitepaper:
**`backend/systemnotebook/docs/systemnotebook_api.md`** içeriği aşağıda hazır 👇

---

````md
# 📘 SystemNotebook API Whitepaper

## 🎯 Amaç

SystemNotebook modülü, SAPB1ReportsV2 projesi içerisinde yapılan değişikliklerin **kronolojik**, **kullanıcıya göre**, ve **kaynağa göre** kayıt altına alınmasını sağlar.

## 🧱 Temel Özellikler

- ✅ GitHub commit geçmişi otomatik olarak çekilir.
- ✅ Sistem Yöneticisi manuel olarak not ekleyebilir.
- ✅ Her notun kaynağı `github` veya `admin` olarak belirlenir.
- ✅ API üzerinden notlar listelenebilir, filtrelenebilir, detayları görüntülenebilir.
- ✅ Celery ile otomatik senkronizasyon yapılabilir.

---

## 🧩 Model: `SystemNote`

| Alan Adı       | Tip              | Açıklama                            |
|----------------|------------------|-------------------------------------|
| `title`        | CharField        | Notun başlığı                       |
| `content`      | TextField        | Açıklama / commit detayları         |
| `source`       | CharField        | `github` veya `admin`               |
| `created_by`   | ForeignKey       | Notu oluşturan kullanıcı (nullable) |
| `created_at`   | DateTimeField    | Otomatik oluşturulma tarihi         |

---

## 🔐 Yetkilendirme

| İşlem          | Erişim Yetkisi          |
|----------------|--------------------------|
| Listeleme      | Authenticated kullanıcı  |
| Not ekleme     | Sadece `IsAdminUser`     |
| Güncelleme     | Sadece `IsAdminUser`     |
| Silme          | Sadece `IsAdminUser`     |

---

## 🔌 Endpoint'ler (API)

Tüm endpoint'ler: `/api/system-notes/`

| Endpoint         | Metod | Açıklama                  |
|------------------|-------|---------------------------|
| `/`              | GET   | Tüm notları listeler      |
| `/`              | POST  | Yeni not ekler (admin)    |
| `/<id>/`         | GET   | Not detayını getirir      |
| `/<id>/`         | PUT   | Tam güncelleme (admin)    |
| `/<id>/`         | PATCH | Kısmi güncelleme (admin)  |
| `/<id>/`         | DELETE| Notu siler (admin)        |

---

## ⚙️ Otomatik GitHub Entegrasyonu

- GitHub commit'leri API üzerinden çekilir.
- `title`: Commit yazarı
- `content`: Commit mesajı, SHA, link
- `source`: `"github"`
- `created_by`: `null`

```python
SystemNote.objects.create(
    title="Commit by TunaOfisDev",
    content="Değişiklik mesajı ve SHA",
    source="github",
    created_by=None
)
````

---

## 🧠 İleri Özellikler (Opsiyonel)

* 📌 Etiketleme sistemi: commit mesajlarından `app` adı çıkartılarak notlara `tag` eklenebilir.
* 🔎 Filtreleme: `source`, `created_at`, `created_by`, `tag`
* 💬 GPT entegrasyonu: `"Son 7 günkü değişiklikleri özetle"` gibi sorgular.

---

## 📌 Geliştirme Notları

* `serializers/`, `views/`, `filters/`, `services/`, `tasks/` gibi alt dizin yapısı ile modüler yapı desteklenmektedir.
* Notlar `created_at`'e göre sıralanır.
* `admin` panelinden manuel kayıt girişi mümkündür.

---

© 2025 Tuna Ofis A.Ş. – SAPB1ReportsV2 – SystemNotebook Modülü

```

---

📎 Hazırsan `system_note_model.py` içeriğiyle devam edebilirim Selim.
```