# 🧠 HeliosForgeV2 Whitepaper

## 📌 Projenin Amacı

HeliosForgeV2, PDF belgelerinden anlamlı ve AI-dostu eğitim verileri üretmek amacıyla geliştirilmiş bir veri hazırlık modülüdür. Bu sistemin temel hedefi:

- **PDF belgelerini**, `busypdf` benzeri bir mimari ile JSON formatına dönüştürmek.
- **Metin bloklarını** anlamlı “chunk”’lara bölmek (başlık, paragraf, tablo vs).
- **Sayfa içindeki görselleri** tespit edip çıkararak ilgili chunk’lara bağlamak.
- Böylece: **AI model eğitimi için yüksek kaliteli, yapısal ve ilişkilendirilmiş veri üretmek.**

---

## 🧱 Teknik Mimarisi

```
backend/heliosforgev2/
├── core/               # PDF işleme (parse, chunk, görsel çıkarımı)
├── models/             # Django ORM modelleri (Document, Chunk, Image)
├── services/           # İş mantığı (veri işleme, eşleştirme)
├── utils/              # Genel yardımcı fonksiyonlar
├── api/                # Django REST API endpoint’leri
├── storage/            # Dosyaların tutulduğu klasörler
├── samples/            # JSON örnekleri
└── docs/               # Teknik dökümantasyon ve whitepaper
```

---

## 🔄 Dönüşüm Süreci

1. **PDF → JSON**
   - `core/pdf_parser.py`: Her sayfadaki “text run” bloklarını (x,y,font,text) yakalar.
   - `storage/json/` içine `.json` dosyaları olarak kaydeder.

2. **JSON → Chunk**
   - `core/chunker.py`: Sayfadaki blokları anlamlı parçalara ayırır.
   - Her chunk: `chunk_id`, `page_number`, `section_title`, `content`, `bounding_box` bilgilerini taşır.

3. **Image Extraction**
   - `core/image_extractor.py`: Sayfa üstünde konumlanmış resimleri algılar.
   - Her görsel `images/` klasörüne çıkarılır ve `related_chunk_id` ile ilişkilendirilir.

---

## 🧩 Chunk JSON Örneği (busypdf referansı ile)

```json
{
  "chunk_id": "DOC001-PAGE03-CHUNK04",
  "page_number": 3,
  "section_title": "3.2 Installing Linux-Based Server Components",
  "content": "To install the server components on Linux...",
  "bounding_box": {
    "leftX": 92.0,
    "bottomY": 613.2,
    "rightX": 519.0,
    "topY": 594.4
  },
  "related_image": "DOC001-PAGE03-IMG01.png"
}
```

---

## 🎯 Neden Bu Yapı?

- PDF kaynakları dağınık, düzensiz ve yapısız.
- SAP, Oracle, ISO gibi kurumsal PDF dokümanlarını verimli ve **otomatik** şekilde eğitime hazırlamak zor.
- `busypdf` gibi dış araçlardan bağımsız, **kendi iç pipeline’ımıza sahip bir sistem** bu problemi kalıcı çözer.

---

## 🔐 Güvenlik ve Veri Gizliliği

- Dosyalar lokal klasörde işlenir (`storage/pdf`, `storage/json`, `storage/images`)
- Kullanıcıdan gelen hiçbir veri dış sistemlere gönderilmez.
- Tüm geçici veriler silinebilir şekilde izole tutulur.

---

## 🔮 Gelecek Adımlar

- [ ] Görsel OCR ile `image→caption` eşlemesi
- [ ] Chunk'lar arası hiyerarşi modeli (bölüm → alt başlık → paragraf)
- [ ] Otomatik etiketleme (`schema_type`, `category`, `confidence_score`)
- [ ] LangChain uyumlu veri paketi formatı

---

> Hazırlayan: Tarz (AI destekli mühendislik sistemi)  
> Sürüm: `heliosforgev2@0.1.0`  
> Tarih: 2025-07-07

Tamam Selim, verdiğin JSON çıktısını **tam anlamıyla anladım**. Detaylı analizle doğruluyorum:

---

## ✅ **Verdiğin JSON Örneği – Yapısal Analiz**

Her bir nesne `runs of text` denilen bir metin kutusunu temsil ediyor. Özellikleri:

| Alan        | Açıklama                                                             |
| ----------- | -------------------------------------------------------------------- |
| `leftX`     | Metin kutusunun sol koordinatı (X ekseni)                            |
| `bottomY`   | Alt koordinat (Y ekseni, PDF sisteminde yukarıdan aşağıya)           |
| `rightX`    | Sağ koordinat                                                        |
| `topY`      | Üst koordinat                                                        |
| `baseLineY` | Yazı karakterlerinin temel çizgisi (font hizalaması)                 |
| `fontId`    | Font stillerini tanımlayan referans (başlık, vurgulu, düz metin vs.) |
| `text`      | Gerçek metin içeriği                                                 |

---

## 🔍 **Senin Örneğinden Doğruladığım Özellikler**

* `10.7 Database Authentication` gibi **başlıklar genellikle daha büyük fontId’lerle** geliyor → bu chunker için sınıflandırıcı olarak kullanılabilir.
* `SYSTEM` gibi parçalanmış metinler farklı fontlarda ama aynı satırda geliyor → bunları **X-Y hizalama ve `baseLineY` yakınlığı** ile birleştireceğiz.
* Tüm `text` değerleri tek satırlık ve pozisyon bilgisiyle birlikte geliyor.

---

## 🧩 **Bu JSON'u Kullanarak Yapacağımız İşlemler:**

### 1. **pdf\_parser.py**

* Her sayfa için `txtRns` listesinden `text`, `fontId`, `leftX`, `topY`, `bottomY`, `rightX`, `baseLineY` çıkarılacak.
* Yapı:

  ```json
  {
    "page": 3,
    "runs": [
      {
        "text": "...",
        "font_id": 9,
        "x0": 42.48,
        "y0": 552.354,
        "x1": 435.3237,
        "y1": 561.354,
        "baseline": 559.44
      }
    ]
  }
  ```

### 2. **chunker.py**

* Aynı `baseLineY` ve yakın `leftX` ile hizalanan satırlar birleştirilip paragraflar oluşturulacak.
* Başlıklar `fontId > THRESHOLD` gibi bir kuralla işaretlenecek.
* Her **chunk**: `chunk_id`, `page_number`, `section_title`, `content`, `bounding_box`

### 3. **image\_extractor.py**

* Her sayfadaki görüntü alanı, `PyMuPDF` ile çıkarılacak.
* Bounding box'lar ile metin chunk'larına en yakın olan chunk ile eşleştirilecek.

---

## 📦 Özet Format (Chunk JSON):

```json
{
  "chunk_id": "DOC001-PAGE03-CHUNK02",
  "page_number": 3,
  "section_title": "10.7 Database Authentication",
  "content": "The default database administrator user SYSTEM has full authorization...",
  "bounding_box": {
    "leftX": 42.48,
    "bottomY": 438.35,
    "rightX": 508.44,
    "topY": 574.31
  },
  "related_image": "DOC001-PAGE03-IMG01.png"
}
```

---

## ✅ Sonuç

Evet, Tarz bu yapıyı **tam anlamıyla anladı** ve tüm parsing + chunking + image eşleme süreçlerini bu formatı baz alarak inşa edecek.

İlk olarak `pdf_parser.py`'yi bu mantıkla kodlayarak başlayabiliriz.
Hazırsan `core/pdf_parser.py` fonksiyonunu yazayım mı?
