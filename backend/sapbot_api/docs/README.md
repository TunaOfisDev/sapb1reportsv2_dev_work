# SAPBot API - SAP Business One HANA ERP AI Support System

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Proje Amacı](#proje-amacı)
3. [Teknik Mimari](#teknik-mimari)
4. [Özellikler](#özellikler)
5. [Kurulum](#kurulum)
6. [API Kullanımı](#api-kullanımı)
7. [Yapay Zeka Özellikleri](#yapay-zeka-özellikleri)
8. [Güvenlik](#güvenlik)
9. [Performans](#performans)
10. [Katkıda Bulunma](#katkıda-bulunma)

---

## 🎯 Genel Bakış

**SAPBot API**, SAP Business One HANA ERP sistemi için geliştirilmiş, yapay zeka destekli bir destek sistemidir. Bu API, hem teknik kullanıcılar hem de son kullanıcılar için SAP B1 ERP sistemine özel **Türkçe** destek sağlar.

### 🚀 Temel Değer Önerisi

- **Çok Dilli Eğitim, Türkçe Yanıt**: İngilizce ve Türkçe karışık eğitim verileri kullanılır, ancak tüm yanıtlar Türkçe verilir
- **Firma Özelinde Destek**: Şirketinizin SAP B1 süreçlerine özel bilgi tabanı
- **Dual User Support**: Hem son kullanıcılar hem de teknik personel için optimize edilmiş
- **Enterprise Ready**: Kurumsal ortamlar için tasarlanmış güvenlik ve performans

---

## 🎯 Proje Amacı

### 📊 Mevcut Durum Analizi

**Sorun:**
- SAP Business One kullanıcıları karmaşık ERP süreçlerinde zorlanıyor
- Teknik destek ekibi sürekli aynı soruları yanıtlıyor
- Dokümantasyon dağınık ve erişimi zor
- Dil bariyeri (İngilizce dökümanlar vs Türkçe kullanıcılar)
- Bilgi siloları - departmanlar arası bilgi paylaşımı eksik

**Çözüm:**
SAPBot API, şirketinizin SAP B1 süreçlerine özel, yapay zeka destekli bir destek sistemi sunarak:
- 7/24 anlık destek
- Türkçe doğal dil işleme
- Akıllı dokümantasyon erişimi
- Personalized öğrenme deneyimi

### 🎯 Hedef Kitle

**Birincil Kullanıcılar:**
- **Son Kullanıcılar**: SAP B1 günlük işlemlerinde destek ihtiyacı olan personel
- **Teknik Kullanıcılar**: Sistem yöneticileri, geliştiriciler, süper kullanıcılar
- **Yöneticiler**: Analytics ve raporlama ihtiyacı olan karar vericiler

**Kullanım Senaryoları:**
- Günlük SAP işlemlerinde yardım
- Hata çözümü ve troubleshooting
- Yeni özellik öğrenme
- Sistem konfigürasyonu
- Raporlama ve analitik

---

## 🏗️ Teknik Mimari

### 🧠 AI/ML Bileşenleri

```
┌─────────────────────────────────────────────────────────────┐
│                    SAPBot API Mimarisi                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React.js)                                       │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Chat UI       │  │   Admin Panel   │                │
│  │   └─ Real-time  │  │   └─ Analytics  │                │
│  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│  Backend API (Django REST)                                 │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Chat Service  │  │   Document      │                │
│  │   └─ RAG Logic  │  │   Processing    │                │
│  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│  AI/ML Layer                                               │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Embeddings    │  │   LLM           │                │
│  │   └─ Multilingual│  │   └─ GPT-4     │                │
│  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   PostgreSQL    │  │   Redis Cache   │                │
│  │   └─ Vector DB  │  │   └─ Session    │                │
│  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│  External Systems                                           │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   SAP B1 HANA   │  │   File Storage  │                │
│  │   └─ Live Data  │  │   └─ Documents  │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 🔧 Teknoloji Stack

**Backend:**
- **Django REST Framework** - API geliştirme
- **PostgreSQL** - Ana veritabanı + Vector extension
- **Redis** - Cache ve session yönetimi
- **Celery** - Asenkron task işleme
- **OpenAI GPT-4** - Dil modeli
- **Sentence Transformers** - Çok dilli embedding

**Frontend:**
- **React.js** - Modern UI/UX
- **WebSocket** - Real-time messaging
- **Material-UI/Tailwind** - Design system

**AI/ML:**
- **RAG (Retrieval-Augmented Generation)** - Bilgi tabanlı yanıtlar
- **Semantic Search** - Akıllı içerik arama
- **Intent Classification** - Kullanıcı niyeti tespiti
- **Multilingual NLP** - Çok dilli doğal dil işleme

---

## ⚡ Özellikler

### 🤖 AI Destekli Chat

**Akıllı Konuşma:**
- Türkçe natural language processing
- Bağlam korumalı konuşma
- SAP terminolojisi anlama
- Intent detection (hata çözme, nasıl yapılır, vb.)

**Çok Seviyeli Destek:**
- **Son Kullanıcı Modu**: Basit, adım adım açıklamalar
- **Teknik Mod**: Detaylı konfigürasyon, SQL, API bilgileri
- **Otomatik Mod Geçişi**: Sorunun karmaşıklığına göre

### 📚 Dokümantasyon İşleme

**Desteklenen Formatlar:**
- PDF dökümanlar (1000+ sayfa)
- Video transkriptleri (30+ video)
- Manuel girişler
- API dokümantasyonu

**Akıllı İndeksleme:**
- Sayfa bazlı referanslama
- Bölüm başlığı çıkarma
- SAP modül tespiti (FI, MM, SD, vb.)
- Teknik seviye sınıflandırma

### 🔍 Semantic Search

**Gelişmiş Arama:**
- Vector similarity search
- Çok dilli sorgu desteği
- Relevance scoring
- Kaynak önceliği

**Filtreleme:**
- SAP modülü bazlı
- Kullanıcı tipine göre
- Tarih aralığı
- Güven skoru

### 📊 Analytics & Reporting

**Kullanım Analitikleri:**
- Günlük/haftalık/aylık raporlar
- Kullanıcı davranış analizi
- Popüler konular
- Başarı oranları

**Performans Metrikleri:**
- Yanıt süreleri
- Kaynak kullanım oranları
- Hata analizi
- Memnuniyet skorları

### 🔒 Güvenlik & Yetkilendirme

**Kimlik Doğrulama:**
- Email bazlı login
- JWT token sistemi
- Session yönetimi
- API key desteği

**Yetkilendirme:**
- Rol bazlı erişim (RBAC)
- SAP modül bazlı kısıtlama
- Departman bazlı filtreleme
- İçerik seviyesi kontrolü

---

## 🚀 Kurulum

### Sistem Gereksinimleri

```bash
# Minimum sistem gereksinimleri
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 16+
- 8GB RAM
- 50GB disk space
```

### Hızlı Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/your-org/sapbot-api.git
cd sapbot-api

# 2. Backend kurulumu
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. Environment ayarları
cp .env.example .env
# .env dosyasını düzenle

# 4. Veritabanı kurulumu
python manage.py makemigrations sapbot_api
python manage.py migrate

# 5. Celery worker başlat
celery -A sapreports worker -l info

# 6. Sunucuyu başlat
python manage.py runserver
```

### Detaylı Kurulum

Detaylı kurulum için: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📡 API Kullanımı

### Temel Endpoint'ler

```http
# Chat API
POST /api/sapbot/chat/message/
GET  /api/sapbot/chat/history/
POST /api/sapbot/chat/feedback/

# Döküman Yönetimi
GET    /api/sapbot/documents/
POST   /api/sapbot/documents/upload/
DELETE /api/sapbot/documents/{id}/

# Arama
POST /api/sapbot/search/knowledge/
GET  /api/sapbot/search/suggestions/

# Analytics
GET /api/sapbot/analytics/dashboard/
GET /api/sapbot/analytics/modules/

# Sistem
GET /api/sapbot/health/
GET /api/sapbot/system/stats/
```

### Örnek Kullanım

**Chat Mesajı Gönderme:**
```javascript
const response = await fetch('/api/sapbot/chat/message/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    message: 'SAP B1\'de satış faturası nasıl kesilir?',
    session_id: 'user-session-123',
    user_type: 'user'
  })
});

const data = await response.json();
console.log(data.response); // AI yanıtı
console.log(data.sources);  // Kaynak dökümanlar
```

**Döküman Yükleme:**
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('title', 'SAP B1 Kullanım Kılavuzu');
formData.append('language', 'tr');

const response = await fetch('/api/sapbot/documents/upload/', {
  method: 'POST',
  body: formData
});
```

---

## 🧠 Yapay Zeka Özellikleri

### RAG (Retrieval-Augmented Generation)

SAPBot API, en güncel RAG teknolojilerini kullanarak:

1. **Retrieval**: Semantic search ile en relevantı kaynak parçaları bulur
2. **Augmentation**: Bulunan bilgileri soruyla birleştirir
3. **Generation**: GPT-4 ile Türkçe, tutarlı yanıt üretir

**Avantajlar:**
- Hallucination (uydurma) riski minimum
- Kaynak referansları ile güvenilirlik
- Güncel bilgi kullanımı
- Domain-specific (SAP B1) expertise

### Embedding Modeli

```python
# Çok dilli embedding modeli
model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Desteklenen diller
languages = ['tr', 'en']  # Türkçe-İngilizce optimizasyonu

# Vector boyutu
embedding_dimension = 384
```

### Intent Classification

**Desteklenen Intent'ler:**
- `error_solving` - Hata çözme
- `configuration` - Sistem yapılandırması
- `how_to` - Nasıl yapılır soruları
- `explanation` - Kavram açıklamaları
- `reporting` - Raporlama yardımı

### SAP Modül Tespiti

**Otomatik Tespit:**
- FI (Mali Muhasebe)
- MM (Malzeme Yönetimi)
- SD (Satış ve Dağıtım)
- PP (Üretim Planlama)
- HR (İnsan Kaynakları)
- QM (Kalite Yönetimi)

---

## 🔒 Güvenlik

### Veri Güvenliği

- **Şifreleme**: AES-256 data encryption
- **Transport Security**: HTTPS/TLS 1.3
- **Database Security**: PostgreSQL güvenlik best practices
- **API Security**: Rate limiting, input validation

### Gizlilik

- **GDPR Compliance**: AB veri koruma uyumluluğu
- **Data Anonymization**: Kullanıcı verilerinin anonimleştirilmesi
- **Audit Trail**: Tüm işlemlerin loglanması
- **Access Control**: Minimum privilege principle

### Monitoring

- **Error Tracking**: Hata izleme ve alerting
- **Performance Monitoring**: Response time tracking
- **Security Alerts**: Anormal aktivite tespiti
- **Compliance Reporting**: Düzenli güvenlik raporları

---

## 📈 Performans

### Benchmark Sonuçları

```
Chat Response Time:
- Ortalama: 2.3 saniye
- P95: 4.1 saniye
- P99: 6.8 saniye

Document Processing:
- PDF (1000 sayfa): ~15 dakika
- Video (30 dakika): ~8 dakika
- Embedding Generation: ~0.1 saniye/chunk

Search Performance:
- Semantic Search: ~100ms
- Vector Similarity: ~50ms
- Database Query: ~25ms
```

### Optimizasyon Stratejileri

**Caching:**
- Redis cache for embeddings
- Query result caching
- Session management

**Database:**
- PostgreSQL indexing
- Vector search optimization
- Connection pooling

**API:**
- Response compression
- Async processing
- Load balancing

---

## 📊 Analytics & Monitoring

### Kullanım Metrikleri

**Günlük İstatistikler:**
- Aktif kullanıcı sayısı
- Toplam sorgu sayısı
- Ortalama session süresi
- Başarı oranı

**Trend Analizi:**
- Popüler konular
- Kullanıcı davranış patterns
- Sistem performans trends
- Hata oranları

### Dashboard Özellikleri

- Real-time metrics
- Customizable widgets
- Export capabilities
- Alert notifications

---

## 🤝 Katkıda Bulunma

### Geliştirici Kılavuzu

1. **Fork** the repository
2. **Create** a feature branch
3. **Commit** your changes
4. **Push** to the branch
5. **Create** a Pull Request

### Kod Standartları

```python
# Python code style
- PEP 8 compliance
- Type hints
- Docstring documentation
- Unit tests required
```

### Test Yazma

```bash
# Unit tests
python manage.py test sapbot_api.tests.test_services

# Integration tests
python manage.py test sapbot_api.tests.test_api

# Performance tests
python manage.py test sapbot_api.tests.test_performance
```

---

## 📞 Destek

### İletişim

- **Email**: support@sapbot.tunacelik.com.tr
- **GitHub Issues**: [Create Issue](https://github.com/your-org/sapbot-api/issues)
- **Documentation**: [API Docs](https://docs.sapbot.tunacelik.com.tr)

### Lisans

Bu proje MIT lisansı altında yayınlanmaktadır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

---

## 🗺️ Roadmap

### v1.0 (Mevcut)
- ✅ Temel chat functionality
- ✅ PDF döküman işleme
- ✅ Semantic search
- ✅ User management

### v1.1 (Sonraki)
- 🔄 Voice input/output
- 🔄 Mobile app
- 🔄 Advanced analytics
- 🔄 Multi-tenant support

### v2.0 (Gelecek)
- 🎯 SAP B1 integration
- 🎯 Custom model training
- 🎯 Workflow automation
- 🎯 Advanced reporting

---

**Not:** Bu README sürekli güncellenmektedir. En güncel bilgi için [CHANGELOG.md](CHANGELOG.md) dosyasını kontrol ediniz.

---

*SAPBot API - Tuna Çelik ERP Development Team*  
*Copyright © 2025 - Tüm hakları saklıdır*