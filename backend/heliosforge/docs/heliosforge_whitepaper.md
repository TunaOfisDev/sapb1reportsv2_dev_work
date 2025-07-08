# HeliosForge Whitepaper

**Sürüm**: 0.1  
**Tarih**: 04-07-2025  
**Yazar**: Selim + Tarz AI

---

## 🎯 Amaç

HeliosForge, SAP Business One HANA sistemleri için kurumsal destek sağlayan bir yapay zeka modelinin **eğitim verilerini hazırlamak**, **etiketlemek** ve **dışa aktarmak** amacıyla geliştirilmiş özel bir Django REST API modülüdür. Amaç, eğitim öncesi tüm veri hazırlık sürecini otomatik ve yeniden kullanılabilir hale getirmektir.

---

## 🚀 Ne İşe Yarar?

HeliosForge aşağıdaki işlemleri üstlenir:

### 1. **Veri Toplama**
- PDF, DOCX, XLSX ve VTT dosyalarını yükleme
class Document(models.Model):
    DOC_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('xlsx', 'XLSX'),
        ('vtt', 'Video Subtitle'),
        ('txt', 'Plain Text'),
    ]
- Manuel veya URL tabanlı kaynak tanımlama
- Her belgeye etiket ekleyebilme

### 2. **Veri Parçalama (Chunking)**
- Belgeleri içeriklerine göre küçük metin bloklarına ayırır
- Optimal token sınırlarına göre `chunk_size` ve `overlap` ile bölme yapılır
- Video altyazıları için dakika bazlı zamanlama desteği

### 3. **Temizleme & İşleme**
- OCR, dil denetimi, gereksiz karakter ayıklama
- Regex + NLP tabanlı içerik filtresi

### 4. **Embedding & Vektörleştirme**
- HuggingFace, BGE, OpenAI gibi modellerle metni embed eder
- Chroma, PGVector gibi vektör veri tabanına aktarım

### 5. **Export / Dışa Aktarım**
- JSONL formatında model eğitimi için temizlenmiş veri çıkarır
- Etiket, kaynak, chunk_id, embedding_id bilgilerini içerir

---

## 📦 Kullanım Senaryoları

| Senaryo | Açıklama |
|--------|----------|
| Model Eğitimi | Eğitimden önce temiz veri seti oluşturur |
| Vaka Hazırlığı | PDF, DOCX dökümanlar kolayca parçalanır ve etiketlenir |
| Video Indexleme | Videoların belirli dakikalarına karşılık gelen içerikler oluşturulur |
| RAG Sistemi | Chroma / PGVector ile hazır veri tabanı yapısı sunar |

---

## 🔧 Mimari Bileşenler

- `models/`: Belgeler, parçalar ve işler
- `tasks/`: Celery ile arka plan işleme (chunk, embed, export)
- `utils/`: Temizleme, splitter, embedder
- `api/`: REST endpoint'ler (upload, iş tetikleme, export)
- `services/`: Vektör veritabanı servisleri

---

## 🧠 HeliosForge Ne Değildir?

- Bir LLM motoru değildir  
- Model eğitimi yapmaz, sadece veri hazırlar  
- Eğitilecek modelin kalitesini artırmak için veri mühendisliği görevlerini üstlenir

---

## 🔒 Güvenlik ve Performans Notları

- Celery kuyruk izolasyonu (low-priority `heliosforge` queue)
- Upload limiti ayarlanabilir (örn. 100MB PDF)
- Etiket ve URL tabanlı sorgulama ile detaylı filtreleme yapılabilir
- `.env` üzerinden esnek yapılandırma destekler

---

## 📌 Yol Haritası (Roadmap)

- [ ] `.xlsx` içerik parser eklenecek  
- [ ] Çoklu dosya batch yükleme desteği  
- [ ] `labeling UI` ile manuel etiketleme arayüzü  
- [ ] Export edilen datasetlerin versiyonlanması  

---

HeliosForge, gelecekte GPT benzeri kurumsal destek sistemlerinin temel veri altyapısını oluşturmayı hedefler. Tüm belge, video ve vaka içerikleri tek merkezden yönetilir ve tekrar tekrar eğitilebilir veri kümesine dönüştürülür.

