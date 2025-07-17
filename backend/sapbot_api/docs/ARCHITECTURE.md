# SAPBot API - Sistem Mimarisi

## 📋 İçindekiler

1. [Mimari Genel Bakış](#mimari-genel-bakış)
2. [Sistem Bileşenleri](#sistem-bileşenleri)
3. [Veri Akışı](#veri-akışı)
4. [AI/ML Mimarisi](#aiml-mimarisi)
5. [Güvenlik Mimarisi](#güvenlik-mimarisi)
6. [Performans Mimarisi](#performans-mimarisi)
7. [Deployment Mimarisi](#deployment-mimarisi)
8. [Monitoring ve Logging](#monitoring-ve-logging)
9. [Scalability](#scalability)
10. [Disaster Recovery](#disaster-recovery)

---

## 🏗️ Mimari Genel Bakış

### Sistem Tipi: Microservices + Layered Architecture

SAPBot API, modern enterprise standartlarına uygun olarak tasarlanmış hybrid bir mimari kullanır:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  Web App (React)  │  Mobile App  │  Desktop App  │  API    │
│  ┌─────────────┐   │  ┌─────────┐  │  ┌─────────┐  │ Clients │
│  │ Chat UI     │   │  │ Native  │  │  │ Electron│  │ ┌─────┐ │
│  │ Dashboard   │   │  │ Mobile  │  │  │ Desktop │  │ │ 3rd │ │
│  │ Admin Panel │   │  │ App     │  │  │ App     │  │ │Party│ │
│  └─────────────┘   │  └─────────┘  │  └─────────┘  │ └─────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Rate Limiting │  │  Authentication │  │   Request   │  │
│  │   Load Balancer │  │   Authorization │  │   Routing   │  │
│  │   SSL/TLS       │  │   JWT Tokens    │  │   Logging   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Chat Service  │  │ Document Service│  │Search Service│  │
│  │   ┌───────────┐ │  │   ┌───────────┐ │  │ ┌─────────┐ │  │
│  │   │RAG Engine │ │  │   │Processor  │ │  │ │Semantic │ │  │
│  │   │LLM Client │ │  │   │PDF Parser │ │  │ │Vector   │ │  │
│  │   │Context    │ │  │   │Embeddings │ │  │ │Search   │ │  │
│  │   └───────────┘ │  │   └───────────┘ │  │ └─────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   User Manager  │  │Analytics Engine │  │Config Mgr   │  │
│  │   Auth Service  │  │   Metrics       │  │System Health│  │
│  │   Session Mgr   │  │   Reports       │  │Notifications│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   PostgreSQL    │  │   Redis Cache   │  │ File Storage│  │
│  │   ┌───────────┐ │  │   ┌───────────┐ │  │ ┌─────────┐ │  │
│  │   │Vector DB  │ │  │   │Sessions   │ │  │ │Documents│ │  │
│  │   │Relations  │ │  │   │Embeddings │ │  │ │Media    │ │  │
│  │   │Analytics  │ │  │   │Queue      │ │  │ │Exports  │ │  │
│  │   └───────────┘ │  │   └───────────┘ │  │ └─────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   OpenAI API    │  │   SAP B1 HANA   │  │   Email     │  │
│  │   GPT-4 Model   │  │   Live Data     │  │   SMS       │  │
│  │   Embeddings    │  │   Integration   │  │   Webhook   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Mimari Prensipleri

1. **Separation of Concerns**: Her katman kendi sorumluluğuna odaklanır
2. **Loose Coupling**: Bileşenler arası bağımlılık minimum
3. **High Cohesion**: İlgili fonksiyonlar bir arada
4. **Scalability**: Horizontal ve vertical scaling desteği
5. **Fault Tolerance**: Hata durumlarında sistem ayakta kalır
6. **Security by Design**: Güvenlik her katmanda entegre

---

## 🔧 Sistem Bileşenleri

### 1. Web Application Layer (Frontend)

```typescript
// React.js Frontend Architecture
src/
├── components/
│   ├── Chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── TypingIndicator.tsx
│   │   └── SourcesList.tsx
│   ├── Dashboard/
│   │   ├── Analytics.tsx
│   │   ├── UserManagement.tsx
│   │   └── SystemHealth.tsx
│   └── Common/
│       ├── Layout.tsx
│       ├── Navigation.tsx
│       └── ErrorBoundary.tsx
├── services/
│   ├── api.ts          // API client
│   ├── websocket.ts    // Real-time communication
│   └── auth.ts         // Authentication
├── stores/
│   ├── chatStore.ts    // Chat state management
│   ├── userStore.ts    // User state
│   └── appStore.ts     // Global state
└── utils/
    ├── helpers.ts
    ├── constants.ts
    └── types.ts
```

**Key Features:**
- **Real-time Messaging**: WebSocket bağlantısı
- **Progressive Web App**: Offline support
- **Responsive Design**: Mobile-first approach
- **State Management**: Redux/Zustand
- **Error Handling**: Comprehensive error boundaries

### 2. API Gateway Layer

```python
# Django REST Framework ile API Gateway
# backend/sapbot_api/gateway/
middleware/
├── authentication.py   # JWT token validation
├── rate_limiting.py    # Request throttling
├── logging.py         # Request/response logging
├── cors.py            # Cross-origin handling
└── security.py        # Security headers

routing/
├── v1_urls.py         # API v1 routes
├── v2_urls.py         # API v2 routes (future)
└── internal_urls.py   # Internal API routes
```

**Responsibilities:**
- Request routing ve load balancing
- Authentication ve authorization
- Rate limiting ve throttling
- Request/response logging
- SSL/TLS termination
- API versioning

### 3. Application Services Layer

#### 3.1 Chat Service

```python
# backend/sapbot_api/services/chat_service.py
class RAGChatbotService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.search_service = SearchService()
        self.llm_client = OpenAIClient()
        self.context_manager = ContextManager()
    
    def process_message(self, query: str, session_id: str) -> ChatResponse:
        # 1. Intent detection
        intent = self.detect_intent(query)
        
        # 2. Context retrieval
        context = self.retrieve_context(query, session_id)
        
        # 3. Response generation
        response = self.generate_response(query, context, intent)
        
        # 4. Save to database
        self.save_conversation(query, response, session_id)
        
        return response
```

#### 3.2 Document Processing Service

```python
# backend/sapbot_api/services/document_processor.py
class DocumentProcessor:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.video_processor = VideoProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.chunk_splitter = ChunkSplitter()
    
    def process_document(self, document: DocumentSource) -> ProcessingResult:
        # 1. Extract text/content
        content = self.extract_content(document)
        
        # 2. Split into chunks
        chunks = self.chunk_splitter.split(content)
        
        # 3. Generate embeddings
        for chunk in chunks:
            embedding = self.embedding_generator.generate(chunk.content)
            chunk.embedding = embedding
        
        # 4. Save to database
        self.save_chunks(chunks)
        
        return ProcessingResult(success=True, chunks_created=len(chunks))
```

#### 3.3 Search Service

```python
# backend/sapbot_api/services/search_service.py
class SearchService:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.relevance_ranker = RelevanceRanker()
        self.result_formatter = ResultFormatter()
    
    def semantic_search(self, query: str, filters: dict) -> SearchResults:
        # 1. Query embedding
        query_embedding = self.generate_embedding(query)
        
        # 2. Vector similarity search
        similar_chunks = self.vector_db.similarity_search(
            query_embedding, 
            filters=filters,
            limit=10
        )
        
        # 3. Relevance ranking
        ranked_results = self.relevance_ranker.rank(similar_chunks, query)
        
        # 4. Format results
        return self.result_formatter.format(ranked_results)
```

### 4. Data Layer Architecture

#### 4.1 PostgreSQL Database Schema

```sql
-- Vector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Primary tables
CREATE TABLE sapbot_document_sources (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(20) NOT NULL,
    file_path TEXT,
    processing_status VARCHAR(20) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sapbot_knowledge_chunks (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES sapbot_document_sources(id),
    content TEXT NOT NULL,
    content_hash VARCHAR(64) UNIQUE,
    embedding VECTOR(384), -- Embedding dimension
    sap_module VARCHAR(10),
    technical_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_knowledge_chunks_embedding ON sapbot_knowledge_chunks 
USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_knowledge_chunks_sap_module ON sapbot_knowledge_chunks (sap_module);
CREATE INDEX idx_knowledge_chunks_content_hash ON sapbot_knowledge_chunks (content_hash);
```

#### 4.2 Redis Cache Architecture

```python
# backend/sapbot_api/utils/cache_utils.py
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB_SAPBOT
        )
    
    CACHE_KEYS = {
        'user_session': 'session:{session_id}',
        'chat_history': 'chat_history:{session_id}',
        'embeddings': 'embeddings:{content_hash}',
        'search_results': 'search:{query_hash}',
        'system_config': 'config:{key}',
        'user_preferences': 'user_prefs:{user_id}'
    }
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        key = self.CACHE_KEYS['chat_history'].format(session_id=session_id)
        return self.redis_client.lrange(key, 0, -1)
    
    def cache_embedding(self, content_hash: str, embedding: List[float]):
        key = self.CACHE_KEYS['embeddings'].format(content_hash=content_hash)
        self.redis_client.setex(key, 86400, json.dumps(embedding))  # 24 hours
```

---

## 🔄 Veri Akışı

### Chat Message Flow

```
User Input → Frontend → API Gateway → Chat Service → Context Retrieval
    ↓
Search Service → Vector DB → Relevance Ranking → LLM Client → Response Generation
    ↓
Database Save → Cache Update → Frontend Update → User Display
```

### Document Processing Flow

```
File Upload → Validation → Storage → Queue → Celery Worker
    ↓
Content Extraction → Text Processing → Chunk Creation → Embedding Generation
    ↓
Database Save → Vector Index → Search Index → Notification → User Update
```

### Real-time Data Flow

```python
# WebSocket connection for real-time updates
# backend/sapbot_api/consumers.py
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Process message asynchronously
        response = await self.process_chat_message(message)
        
        # Send response back to user
        await self.send(text_data=json.dumps({
            'type': 'chat_response',
            'message': response
        }))
```

---

## 🧠 AI/ML Mimarisi

### 1. RAG (Retrieval-Augmented Generation) Pipeline

```python
# backend/sapbot_api/ai/rag_pipeline.py
class RAGPipeline:
    def __init__(self):
        self.retriever = DocumentRetriever()
        self.generator = ResponseGenerator()
        self.context_manager = ContextManager()
    
    def process_query(self, query: str, session_id: str) -> RAGResponse:
        # Stage 1: Query Analysis
        query_analysis = self.analyze_query(query)
        
        # Stage 2: Document Retrieval
        relevant_docs = self.retriever.retrieve(
            query=query,
            filters={
                'sap_module': query_analysis.sap_module,
                'technical_level': query_analysis.technical_level
            },
            limit=5
        )
        
        # Stage 3: Context Preparation
        context = self.context_manager.prepare_context(
            query=query,
            documents=relevant_docs,
            session_history=self.get_session_history(session_id)
        )
        
        # Stage 4: Response Generation
        response = self.generator.generate(
            query=query,
            context=context,
            parameters={
                'temperature': 0.3,
                'max_tokens': 1500,
                'language': 'tr'
            }
        )
        
        return RAGResponse(
            response=response,
            sources=relevant_docs,
            confidence=query_analysis.confidence
        )
```

### 2. Embedding Architecture

```python
# backend/sapbot_api/ai/embedding_service.py
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        self.cache = EmbeddingCache()
        self.batch_size = 32
    
    def generate_embedding(self, text: str) -> List[float]:
        # Check cache first
        text_hash = self.generate_hash(text)
        cached_embedding = self.cache.get(text_hash)
        
        if cached_embedding:
            return cached_embedding
        
        # Generate new embedding
        embedding = self.model.encode(text)
        
        # Cache the result
        self.cache.set(text_hash, embedding.tolist())
        
        return embedding.tolist()
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Batch processing for better performance"""
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(batch)
            embeddings.extend(batch_embeddings.tolist())
        return embeddings
```

### 3. Intent Classification

```python
# backend/sapbot_api/ai/intent_classifier.py
class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'error_solving': [
                'hata', 'error', 'sorun', 'problem', 'çalışmıyor',
                'düzgün', 'bozuk', 'eksik', 'yanlış'
            ],
            'how_to': [
                'nasıl', 'how', 'ne şekilde', 'hangi adımlar',
                'yapılır', 'oluşturulur', 'kaydedilir'
            ],
            'configuration': [
                'ayar', 'setting', 'konfigürasyon', 'yapılandırma',
                'parametre', 'değer', 'seçenek'
            ],
            'explanation': [
                'nedir', 'what is', 'açıkla', 'explain',
                'anlat', 'tanım', 'kavram'
            ]
        }
    
    def classify_intent(self, query: str) -> IntentResult:
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(query_lower.count(pattern) for pattern in patterns)
            if score > 0:
                intent_scores[intent] = score / len(query.split())
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            return IntentResult(
                intent=best_intent,
                confidence=confidence,
                all_scores=intent_scores
            )
        
        return IntentResult(intent='general', confidence=0.0)
```

### 4. SAP Module Detection

```python
# backend/sapbot_api/ai/sap_module_detector.py
class SAPModuleDetector:
    def __init__(self):
        self.module_keywords = {
            'FI': [
                'mali', 'muhasebe', 'genel muhasebe', 'financial',
                'accounting', 'hesap', 'borç', 'alacak', 'fatura'
            ],
            'MM': [
                'malzeme', 'satın alma', 'stok', 'material',
                'purchasing', 'tedarik', 'sipariş', 'depo'
            ],
            'SD': [
                'satış', 'dağıtım', 'sales', 'distribution',
                'müşteri', 'teklif', 'sevkiyat', 'fiyat'
            ],
            # ... diğer modüller
        }
    
    def detect_module(self, text: str) -> ModuleResult:
        text_lower = text.lower()
        module_scores = {}
        
        for module, keywords in self.module_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                module_scores[module] = score
        
        if module_scores:
            detected_module = max(module_scores, key=module_scores.get)
            confidence = module_scores[detected_module] / len(text.split())
            
            return ModuleResult(
                module=detected_module,
                confidence=confidence,
                all_scores=module_scores
            )
        
        return ModuleResult(module=None, confidence=0.0)
```

---

## 🔒 Güvenlik Mimarisi

### 1. Authentication & Authorization

```python
# backend/sapbot_api/security/auth.py
class SAPBotAuthentication:
    def __init__(self):
        self.jwt_handler = JWTHandler()
        self.user_manager = UserManager()
        self.session_manager = SessionManager()
    
    def authenticate_user(self, email: str, password: str) -> AuthResult:
        # 1. User validation
        user = self.user_manager.get_user_by_email(email)
        if not user or not user.check_password(password):
            return AuthResult(success=False, error="Invalid credentials")
        
        # 2. Generate JWT tokens
        access_token = self.jwt_handler.create_access_token(user)
        refresh_token = self.jwt_handler.create_refresh_token(user)
        
        # 3. Create session
        session = self.session_manager.create_session(user, request_info)
        
        return AuthResult(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session.id
        )
    
    def authorize_request(self, request: Request) -> bool:
        # 1. Extract token
        token = self.extract_token(request)
        
        # 2. Validate token
        if not self.jwt_handler.validate_token(token):
            return False
        
        # 3. Check permissions
        user = self.get_user_from_token(token)
        required_permission = self.get_required_permission(request)
        
        return self.user_manager.has_permission(user, required_permission)
```

### 2. Data Protection

```python
# backend/sapbot_api/security/data_protection.py
class DataProtection:
    def __init__(self):
        self.encryption_key = settings.DATA_ENCRYPTION_KEY
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storing"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieving"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def anonymize_user_data(self, user_data: dict) -> dict:
        """Anonymize user data for analytics"""
        return {
            'user_id': hashlib.sha256(user_data['email'].encode()).hexdigest()[:8],
            'department': user_data.get('department', 'unknown'),
            'user_type': user_data.get('user_type', 'user'),
            'session_count': user_data.get('session_count', 0)
        }
```

### 3. Input Validation & Sanitization

```python
# backend/sapbot_api/security/validators.py
class InputValidator:
    def __init__(self):
        self.sql_injection_patterns = [
            r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)",
            r"(\bUNION\b|\bDROP\b|\bCREATE\b|\bALTER\b)",
            r"(--|/\*|\*/|;)",
            r"(\bOR\b.*=.*|\bAND\b.*=.*)"
        ]
        
        self.xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe.*?>.*?</iframe>"
        ]
    
    def validate_chat_message(self, message: str) -> ValidationResult:
        # 1. Length validation
        if len(message) > 2000:
            return ValidationResult(valid=False, error="Message too long")
        
        # 2. SQL injection check
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return ValidationResult(valid=False, error="Invalid characters")
        
        # 3. XSS check
        for pattern in self.xss_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return ValidationResult(valid=False, error="Invalid content")
        
        # 4. Content sanitization
        sanitized_message = self.sanitize_content(message)
        
        return ValidationResult(
            valid=True,
            sanitized_input=sanitized_message
        )
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize user input"""
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove potentially dangerous characters
        content = re.sub(r'[<>"\']', '', content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
```

---

## 📊 Performans Mimarisi

### 1. Caching Strategy

```python
# backend/sapbot_api/performance/cache_strategy.py
class CacheStrategy:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.cache_levels = {
            'L1': 'memory',    # In-memory cache
            'L2': 'redis',     # Redis cache
            'L3': 'database'   # Database cache
        }
    
    def get_cached_response(self, query_hash: str) -> Optional[Dict]:
        # L1: Memory cache
        if hasattr(self, '_memory_cache'):
            cached = self._memory_cache.get(query_hash)
            if cached:
                return cached
        
        # L2: Redis cache
        cached = self.redis_client.get(f"response:{query_hash}")
        if cached:
            return json.loads(cached)
        
        return None
    
    def cache_response(self, query_hash: str, response: Dict, ttl: int = 3600):
        # L1: Memory cache
        if not hasattr(self, '_memory_cache'):
            self._memory_cache = {}
        self._memory_cache[query_hash] = response
        
        # L2: Redis cache
        self.redis_client.setex(
            f"response:{query_hash}",
            ttl,
            json.dumps(response)
        )
```

### 2. Database Optimization

```python
# backend/sapbot_api/performance/db_optimization.py
class DatabaseOptimizer:
    def __init__(self):
        self.connection_pool = self.create_connection_pool()
    
    def create_connection_pool(self):
        return psycopg2.pool.ThreadedConnectionPool(
            minconn=5,
            maxconn=20,
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
    
    def optimize_vector_search(self, query_embedding: List[float]) -> List[Dict]:
        """Optimized vector similarity search"""
        sql = """
        SELECT id, content, sap_module, technical_level,
               embedding <-> %s as distance
        FROM sapbot_knowledge_chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <-> %s
        LIMIT 10
        """
        
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, (query_embedding, query_embedding))
                results = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'content': row[1],
                        'sap_module': row[2],

Mükemmel Selim! Bu SAP Business One 10.0 HANA ekran görüntüsü sayesinde sistemi daha iyi anlayabiliyorum. Görünen özelliklere göre SAPBot API'nin odaklanması gereken ana alanları belirliyorum:

## 🎯 SAP B1 Sisteminiz İçin SAPBot API Analizi

### 📊 Gözlemlenen Modüller ve Özellikler

**Aktif Modüller:**
- ✅ **Finansallar** (Mali Yönetim)
- ✅ **CRM** (Müşteri İlişkileri)
- ✅ **Fırsatlar** (Satış Fırsatları)
- ✅ **Satış - müşteri** (Satış Yönetimi)
- ✅ **Satınalma - satıcı** (Satın Alma)
- ✅ **Muhataplar** (İş Ortakları)
- ✅ **Bankacılık işlemleri**
- ✅ **Stok** (Envanter Yönetimi)
- ✅ **Kaynaklar** (Kaynak Yönetimi)
- ✅ **Üretim** (Üretim Planlama)
- ✅ **MIP** (Malzeme İhtiyaç Planlaması)
- ✅ **Hizmet** (Servis Yönetimi)
- ✅ **İnsan kaynakları** (HR)

**Dashboard Metrikleri:**
- Toplam satış tutarı: 44.65M TRY
- Toplam alacak tutarı: 49.26M TRY
- Sales Process workflow görünümü
- Teslim edilmeyen satış siparişleri takibi

### 🔧 SAPBot API İçin Özelleştirilmiş Konfigürasyon

Bu bilgilere dayanarak `backend/sapbot_api/config/constants.py` dosyasını firmaya özel oluşturalım:

```python
# backend/sapbot_api/config/constants.py
# SAP Business One 10.0 HANA - Tuna Çelik ERP Özelleştirmeleri

# SAP B1 Versiyon Bilgileri
SAP_B1_VERSION = "10.0"
SAP_B1_PLATFORM = "HANA"
SAP_B1_BUILD = "10.00.240 SP 2402"
SAP_B1_ARCHITECTURE = "64-bit"

# Firmaya Özel SAP Modülleri
COMPANY_SAP_MODULES = {
    'FI': {
        'name': 'Finansallar',
        'description': 'Mali yönetim ve muhasebe işlemleri',
        'keywords': ['finansal', 'mali', 'muhasebe', 'genel muhasebe', 'bütçe'],
        'active': True,
        'priority': 1
    },
    'CRM': {
        'name': 'CRM',
        'description': 'Müşteri ilişkileri yönetimi',
        'keywords': ['crm', 'müşteri', 'ilişki', 'customer', 'relationship'],
        'active': True,
        'priority': 2
    },
    'SD': {
        'name': 'Satış - Müşteri',
        'description': 'Satış yönetimi ve müşteri işlemleri',
        'keywords': ['satış', 'müşteri', 'sales', 'teklif', 'sipariş', 'fatura'],
        'active': True,
        'priority': 1
    },
    'MM': {
        'name': 'Satınalma - Satıcı',
        'description': 'Satın alma ve tedarikçi yönetimi',
        'keywords': ['satın alma', 'satıcı', 'tedarikçi', 'purchasing', 'vendor'],
        'active': True,
        'priority': 2
    },
    'BP': {
        'name': 'Muhataplar',
        'description': 'İş ortağı yönetimi',
        'keywords': ['muhatap', 'iş ortağı', 'business partner', 'bp'],
        'active': True,
        'priority': 2
    },
    'BANK': {
        'name': 'Bankacılık İşlemleri',
        'description': 'Banka işlemleri ve finansal yönetim',
        'keywords': ['banka', 'bankacılık', 'ödeme', 'transfer', 'banking'],
        'active': True,
        'priority': 2
    },
    'INV': {
        'name': 'Stok',
        'description': 'Envanter ve stok yönetimi',
        'keywords': ['stok', 'envanter', 'inventory', 'malzeme', 'depo'],
        'active': True,
        'priority': 1
    },
    'RES': {
        'name': 'Kaynaklar',
        'description': 'Kaynak yönetimi ve planlama',
        'keywords': ['kaynak', 'resource', 'planlama', 'planning'],
        'active': True,
        'priority': 3
    },
    'PROD': {
        'name': 'Üretim',
        'description': 'Üretim planlama ve yönetimi',
        'keywords': ['üretim', 'production', 'manufacturing', 'imalat'],
        'active': True,
        'priority': 2
    },
    'MRP': {
        'name': 'MIP',
        'description': 'Malzeme İhtiyaç Planlaması',
        'keywords': ['mip', 'mrp', 'malzeme ihtiyaç', 'planlama'],
        'active': True,
        'priority': 3
    },
    'SVC': {
        'name': 'Hizmet',
        'description': 'Servis ve hizmet yönetimi',
        'keywords': ['hizmet', 'service', 'servis', 'destek'],
        'active': True,
        'priority': 2
    },
    'HR': {
        'name': 'İnsan Kaynakları',
        'description': 'İnsan kaynakları yönetimi',
        'keywords': ['insan kaynakları', 'hr', 'human resources', 'personel'],
        'active': True,
        'priority': 3
    }
}

# Dashboard Metrikleri
DASHBOARD_METRICS = {
    'sales_total': {
        'name': 'Toplam Satış Tutarı',
        'description': 'Toplam satış tutarı (TRY)',
        'format': 'currency',
        'currency': 'TRY'
    },
    'receivables_total': {
        'name': 'Toplam Alacak Tutarı',
        'description': 'Toplam alacak tutarı (TRY)',
        'format': 'currency',
        'currency': 'TRY'
    },
    'pending_orders': {
        'name': 'Teslim Edilmeyen Siparişler',
        'description': 'Teslim edilmeyen satış siparişleri',
        'format': 'number'
    }
}

# Sales Process Workflow
SALES_PROCESS_STEPS = [
    'sales_quotation',    # Sales Quotation
    'sales_order',        # Sales Order
    'delivery',           # Delivery
    'ar_invoice',         # A/R Invoice
    'incoming_payments',  # Incoming Payments
    'ar_dp_invoice',     # A/R DP Invoice
    'dunning_wizard',    # Dunning Wizard
    'customer'           # Customer
]

# Kullanıcı Tipleri - Firmaya Özel
USER_TYPES = {
    'end_user': {
        'name': 'Son Kullanıcı',
        'description': 'Günlük SAP B1 kullanıcısı',
        'modules': ['FI', 'SD', 'MM', 'INV', 'CRM'],
        'technical_level': 'basic'
    },
    'power_user': {
        'name': 'İleri Kullanıcı',
        'description': 'Deneyimli SAP B1 kullanıcısı',
        'modules': ['FI', 'SD', 'MM', 'INV', 'CRM', 'PROD', 'MRP'],
        'technical_level': 'intermediate'
    },
    'admin': {
        'name': 'Sistem Yöneticisi',
        'description': 'SAP B1 sistem yöneticisi',
        'modules': list(COMPANY_SAP_MODULES.keys()),
        'technical_level': 'advanced'
    },
    'developer': {
        'name': 'Geliştirici',
        'description': 'SAP B1 geliştirici/entegratör',
        'modules': list(COMPANY_SAP_MODULES.keys()),
        'technical_level': 'expert'
    }
}

# Türkçe Intent Patterns - SAP B1 Özelleştirmeli
TURKISH_INTENT_PATTERNS = {
    'sales_inquiry': [
        'satış faturası', 'satış teklifi', 'satış siparişi', 'müşteri siparişi',
        'sales quotation', 'sales order', 'ar invoice', 'satış süreci'
    ],
    'inventory_inquiry': [
        'stok durumu', 'stok raporu', 'envanter', 'malzeme', 'depo',
        'inventory', 'stock', 'item master', 'warehouse'
    ],
    'financial_inquiry': [
        'mali rapor', 'muhasebe kaydı', 'genel muhasebe', 'finansal',
        'chart of accounts', 'journal entry', 'financial report'
    ],
    'purchase_inquiry': [
        'satın alma', 'tedarikçi', 'satıcı', 'purchase order',
        'vendor', 'supplier', 'ap invoice', 'procurement'
    ],
    'process_help': [
        'nasıl yapılır', 'adım adım', 'süreç', 'işlem', 'how to',
        'process', 'workflow', 'step by step'
    ],
    'error_resolution': [
        'hata', 'problem', 'sorun', 'error', 'issue', 'bug',
        'çalışmıyor', 'not working', 'fail'
    ]
}

# Sistem Konfigürasyonu
SYSTEM_CONFIG = {
    'company_name': 'Tuna Çelik',
    'sap_version': SAP_B1_VERSION,
    'database_type': 'HANA',
    'language': 'TR',
    'currency': 'TRY',
    'timezone': 'Europe/Istanbul',
    'date_format': 'DD.MM.YYYY',
    'number_format': '###.###,##'
}
```

### 🚀 Sonraki Adımlar

1. **Model Güncellemeleri**: `KnowledgeChunk` modelinde SAP_MODULE_CHOICES'ları firmaya özel güncelleme
2. **Intent Classifier**: Türkçe SAP B1 terminolojisine özel intent detection
3. **Context Manager**: Sales Process workflow'u anlayan bağlam yönetimi
4. **Dashboard Integration**: Gerçek zamanlı SAP B1 metrikleri entegrasyonu

Bu yapıya göre devam edelim mi? Hangi bileşeni öncelikle detaylandırmak istiyorsun?