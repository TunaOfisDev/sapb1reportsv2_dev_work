### ✅ `docs/procure_compare_api_whitepaper.md` İçeriği:

```markdown
# 📘 ProcureCompare API Whitepaper

## 🎯 Amaç

`ProcureCompare API`, SAP HANA üzerindeki satınalma siparişleri ile geçmiş tekliflerin fiyat verilerini karşılaştırır.  
Bu sayede kullanıcılar, geçmiş tekliflerle kıyas yaparak **en uygun tedarikçiyi** seçebilir, **maliyet avantajı** sağlayabilir ve **veriye dayalı kararlar** alabilir.

---

## ⚙️ Genel Yapı

- Backend: `Django + DRF`
- Frontend: `React.js`
- Veritabanı: `PostgreSQL`
- Veri Kaynağı: `SAP HANA`
- Sync: Her senkronizasyon işleminde eski veriler silinir, HANA'dan yeniden çekilir.

---

## 🧱 Mimaride Kullanılan Katmanlar

- **API:** `procure_compare/api/`
- **Models:** `procure_compare/models/`
- **Services:** `procure_compare/services/`
- **Tasks:** `procure_compare/tasks/`
- **Docs:** `procure_compare/docs/`

---

## 🔐 Güvenlik & Erişim

- Tüm API çağrıları `Bearer Token` ile güvenlik altına alınmıştır.
- Loglama işlemleri `loguru` ile yapılır.

---

## 📊 Kullanım Senaryoları

- Sipariş/teklif fiyat karşılaştırması
- En düşük teklifin seçimi
- Tedarikçi analizleri
- Maliyet avantajı belirleme

---

## 📮 Onay Süreci

- Onay yetkisi `Satin_Alma_Onay` grubuna atanmıştır.
- Bu gruptaki herhangi bir kullanıcının ilk onayı işlem için yeterlidir.
- Onay verildiğinde:
  - Onay durumu, onaylayan kişi ve tarih DB'ye yazılır.
  - `mailservice` API'si tetiklenerek onay bildirimi e-posta ile iletilir.
- Çoklu onay süreci şimdilik devre dışı bırakılmıştır (esnek yapıya sahiptir).

---

## ✉️ MailService Entegrasyonu

Bu yapı `mailservice` modülü ile entegredir:

- **Modül:** `backend_mailservice/services/send_procure_compare_approval_email.py`
- **Görevi:** Onay işlemi sonrası ilgili kişilere PDF ve HTML olarak mail gönderimi
- **Şablon:** `templates/mailservice/procure_compare_approval_email.html/pdf`

---

## 📉 Teklif Skorlama Algoritması (Aktif/Pasif)

| Kriter                    | Durum  | Açıklama |
|--------------------------|--------|----------|
| Fiyat Önceliği           | ✅ Aktif | Döviz kuru üzerinden normalize edilir |
| Vade Gün Önceliği        | ⛔ Pasif | Uzun vade > kısa vade |
| Teslim Tarihi Önceliği   | ⛔ Pasif | Belge tarihine yakın teslimat tercih edilir |
| Kalite Kontrol Skoru     | ⛔ Pasif | Kalite puanı 100 üzerinden değerlendirilir |

> Not: Şirket politikası gereği sadece fiyat karşılaştırması aktif kullanılmaktadır.

---

## 🔄 Senkronizasyon

```http
POST /api/sync/
Authorization: Bearer <TOKEN>

Response:
{
  "status": "success",
  "synced_records": 245
}
```

---

## 📈 Satın Alma Karşılaştırma API

```http
GET /api/purchase-comparisons/?date_from=2025-04-01&date_to=2025-04-20

Response:
[
  {
    "belge_no": 7454,
    "kalem": "KULP BERFİNO...",
    "net_fiyat": 60.0,
    "teklifler": {
      "AYDER": "60 TRY",
      "STARWOOD": "80 TRY"
    }
  }
]
```

---

## 🧬 Dosya Hiyerarşisi (QuantumStack Uyumlu)

```plaintext
procure_compare/
├── api/
├── models/
├── services/
├── tasks/
├── tests/
├── docs/
├── admin.py
├── apps.py
└── urls.py
```

---

## 📝 Notlar

- API modeli birebir HANA veri yapısına sadıktır.
- Modüler yapı ile geliştirilebilirlik kolaydır.
