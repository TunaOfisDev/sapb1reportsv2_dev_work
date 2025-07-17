# SAPBot API Reference

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Authentication](#authentication)
3. [Chat API](#chat-api)
4. [Document API](#document-api)
5. [Search API](#search-api)
6. [User API](#user-api)
7. [Analytics API](#analytics-api)
8. [System API](#system-api)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [Webhooks](#webhooks)
12. [SDK ve Examples](#sdk-ve-examples)

---

## 🌐 Genel Bakış

### Base URL
```
Production: https://api.sapbot.tunacelik.com.tr
Development: http://localhost:8000
```

### API Versioning
```
Current Version: v1
Base Path: /api/sapbot/v1/
```

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`
- **File Upload**: `multipart/form-data`

### Common Headers
```http
Content-Type: application/json
Authorization: Bearer {access_token}
Accept: application/json
User-Agent: SAPBot-Client/1.0
```

---

## 🔐 Authentication

### JWT Token Authentication

#### Login
```http
POST /api/sapbot/v1/auth/login/
```

**Request Body:**
```json
{
  "email": "user@tunacelik.com.tr",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 28800,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@tunacelik.com.tr",
    "user_type": "user",
    "permissions": ["chat", "upload", "search"]
  }
}
```

#### Refresh Token
```http
POST /api/sapbot/v1/auth/refresh/
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Logout
```http
POST /api/sapbot/v1/auth/logout/
```

**Headers:**
```http
Authorization: Bearer {access_token}
```

---

## 💬 Chat API

### Send Message

```http
POST /api/sapbot/v1/chat/message/
```

**Request Body:**
```json
{
  "message": "SAP B1'de satış faturası nasıl kesilir?",
  "session_id": "session_12345",
  "user_type": "user",
  "context": {
    "sap_module": "SD",
    "language": "tr"
  }
}
```

**Response:**
```json
{
  "id": "msg_123456",
  "session_id": "session_12345",
  "response": "SAP Business One'da satış faturası kesmek için şu adımları izleyebilirsiniz:\n\n1. Ana menüden 'Satış - A/R' > 'Satış Faturası' seçeneğini tıklayın...",
  "sources": [
    {
      "id": "doc_789",
      "title": "SAP B1 Satış Modülü Kullanım Kılavuzu",
      "page_number": 45,
      "section": "Satış Faturası Oluşturma",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "response_time": 2.3,
    "tokens_used": 150,
    "intent_detected": "how_to",
    "confidence_score": 0.89,
    "sap_module": "SD"
  },
  "created_at": "2025-01-16T10:30:00Z"
}
```

### Get Chat History

```http
GET /api/sapbot/v1/chat/history/
```

**Query Parameters:**
- `session_id` (required): Session ID
- `limit` (optional): Number of messages (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "session_id": "session_12345",
  "total_messages": 25,
  "messages": [
    {
      "id": "msg_123456",
      "type": "user",
      "content": "SAP B1'de satış faturası nasıl kesilir?",
      "timestamp": "2025-01-16T10:30:00Z"
    },
    {
      "id": "msg_123457",
      "type": "assistant",
      "content": "SAP Business One'da satış faturası kesmek için...",
      "sources": [...],
      "timestamp": "2025-01-16T10:30:02Z"
    }
  ],
  "pagination": {
    "next": "/api/sapbot/v1/chat/history/?session_id=session_12345&offset=50",
    "previous": null,
    "count": 25
  }
}
```

### Submit Feedback

```http
POST /api/sapbot/v1/chat/feedback/
```

**Request Body:**
```json
{
  "message_id": "msg_123456",
  "rating": 5,
  "feedback_type": "rating",
  "comment": "Çok faydalı bir açıklama oldu, teşekkürler!",
  "is_helpful": true
}
```

**Response:**
```json
{
  "id": "feedback_789",
  "message_id": "msg_123456",
  "rating": 5,
  "status": "received",
  "created_at": "2025-01-16T10:35:00Z"
}
```

### Clear Conversation

```http
DELETE /api/sapbot/v1/chat/clear/
```

**Request Body:**
```json
{
  "session_id": "session_12345"
}
```

---

## 📄 Document API

### List Documents

```http
GET /api/sapbot/v1/documents/
```

**Query Parameters:**
- `type` (optional): Document type (pdf, video, manual)
- `language` (optional): Document language (tr, en, mixed)
- `status` (optional): Processing status (pending, processing, completed, failed)
- `search` (optional): Search in title and description
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Response:**
```json
{
  "count": 145,
  "next": "/api/sapbot/v1/documents/?page=2",
  "previous": null,
  "results": [
    {
      "id": "doc_123456",
      "title": "SAP B1 Kullanım Kılavuzu",
      "description": "SAP Business One temel kullanım rehberi",
      "document_type": "pdf",
      "language": "tr",
      "processing_status": "completed",
      "file_size": 15728640,
      "chunk_count": 234,
      "uploaded_by": "admin@tunacelik.com.tr",
      "created_at": "2025-01-15T14:30:00Z",
      "processed_at": "2025-01-15T14:45:00Z"
    }
  ]
}
```

### Upload Document

```http
POST /api/sapbot/v1/documents/upload/
```

**Request (multipart/form-data):**
```
file: [PDF/Video File]
title: "SAP B1 Mali Modül Kılavuzu"
description: "Mali muhasebe modülü detaylı kullanım rehberi"
language: "tr"
tags: ["FI", "muhasebe", "kılavuz"]
```

**Response:**
```json
{
  "id": "doc_789012",
  "title": "SAP B1 Mali Modül Kılavuzu",
  "document_type": "pdf",
  "processing_status": "pending",
  "file_size": 8945120,
  "message": "Dosya başarıyla yüklendi, işleme başladı",
  "estimated_processing_time": "10-15 dakika",
  "created_at": "2025-01-16T11:00:00Z"
}
```

### Get Document Status

```http
GET /api/sapbot/v1/documents/{document_id}/status/
```

**Response:**
```json
{
  "id": "doc_789012",
  "processing_status": "processing",
  "progress": 65,
  "chunks_processed": 89,
  "total_chunks_estimated": 137,
  "processing_started": "2025-01-16T11:01:00Z",
  "estimated_completion": "2025-01-16T11:12:00Z",
  "error_message": null
}
```

### Delete Document

```http
DELETE /api/sapbot/v1/documents/{document_id}/
```

**Response:**
```json
{
  "message": "Document successfully deleted",
  "deleted_chunks": 234,
  "freed_space": "15 MB"
}
```

### Reprocess Document

```http
POST /api/sapbot/v1/documents/{document_id}/reprocess/
```

**Request Body:**
```json
{
  "force": true,
  "update_embeddings": true
}
```

### Get Document Chunks

```http
GET /api/sapbot/v1/documents/{document_id}/chunks/
```

**Query Parameters:**
- `sap_module` (optional): Filter by SAP module
- `technical_level` (optional): Filter by technical level
- `page` (optional): Page number

**Response:**
```json
{
  "document_id": "doc_789012",
  "total_chunks": 234,
  "chunks": [
    {
      "id": "chunk_456789",
      "content": "Satış faturası oluşturmak için ana menüden...",
      "page_number": 45,
      "section_title": "Satış Faturası İşlemleri",
      "sap_module": "SD",
      "technical_level": "user",
      "usage_count": 12,
      "last_used": "2025-01-16T10:30:00Z"
    }
  ]
}
```

### Bulk Upload

```http
POST /api/sapbot/v1/documents/bulk-upload/
```

**Request (multipart/form-data):**
```
files: [Multiple files]
language: "tr"
auto_detect_type: true
```

---

## 🔍 Search API

### Knowledge Search

```http
POST /api/sapbot/v1/search/knowledge/
```

**Request Body:**
```json
{
  "query": "satış faturası iptal",
  "user_type": "user",
  "filters": {
    "sap_module": "SD",
    "technical_level": "user",
    "language": "tr"
  },
  "limit": 10,
  "min_relevance": 0.7
}
```

**Response:**
```json
{
  "query": "satış faturası iptal",
  "results_count": 8,
  "search_time": 0.12,
  "results": [
    {
      "id": "chunk_123456",
      "content": "Satış faturası iptal etmek için öncelikle faturanın durumunu kontrol etmeniz gerekir...",
      "source": {
        "id": "doc_789",
        "title": "SAP B1 Satış Modülü",
        "page_number": 67,
        "section": "Fatura İptal İşlemleri"
      },
      "relevance_score": 0.94,
      "sap_module": "SD",
      "technical_level": "user",
      "highlighted_text": "Satış <mark>faturası</mark> <mark>iptal</mark> etmek için..."
    }
  ],
  "suggestions": [
    "satış faturası düzeltme",
    "fatura iade işlemi",
    "satış iade faturası"
  ]
}
```

### Search Suggestions

```http
GET /api/sapbot/v1/search/suggestions/
```

**Query Parameters:**
- `query` (required): Partial search query
- `limit` (optional): Number of suggestions (default: 5)

**Response:**
```json
{
  "query": "satış fat",
  "suggestions": [
    "satış faturası",
    "satış faturası iptal",
    "satış faturası düzeltme",
    "satış faturası raporu",
    "satış faturası onay"
  ]
}
```

### Popular Searches

```http
GET /api/sapbot/v1/search/popular/
```

**Query Parameters:**
- `period` (optional): Time period (daily, weekly, monthly)
- `user_type` (optional): Filter by user type
- `limit` (optional): Number of results

**Response:**
```json
{
  "period": "weekly",
  "popular_searches": [
    {
      "query": "satış faturası",
      "search_count": 156,
      "success_rate": 0.92
    },
    {
      "query": "stok raporu",
      "search_count": 89,
      "success_rate": 0.87
    }
  ]
}
```

---

## 👤 User API

### Get User Profile

```http
GET /api/sapbot/v1/user/profile/
```

**Response:**
```json
{
  "id": "user_123456",
  "email": "user@tunacelik.com.tr",
  "display_name": "Ahmet Yılmaz",
  "user_type": "user",
  "preferred_language": "tr",
  "sap_modules": ["FI", "MM", "SD"],
  "departments": ["Muhasebe", "Satış"],
  "chat_settings": {
    "response_format": "detailed",
    "show_sources": true,
    "auto_translate": false
  },
  "email_notifications": true,
  "last_login": "2025-01-16T09:00:00Z",
  "created_at": "2024-12-01T10:00:00Z"
}
```

### Update User Profile

```http
PUT /api/sapbot/v1/user/profile/
```

**Request Body:**
```json
{
  "display_name": "Ahmet Yılmaz",
  "preferred_language": "tr",
  "chat_settings": {
    "response_format": "detailed",
    "show_sources": true,
    "context_memory": 10
  },
  "email_notifications": true
}
```

### Get User Preferences

```http
GET /api/sapbot/v1/user/preferences/
```

**Response:**
```json
{
  "theme": "light",
  "font_size": 14,
  "show_typing_indicator": true,
  "sound_enabled": true,
  "keyboard_shortcuts": true,
  "auto_save_conversations": true,
  "dashboard_widgets": [
    "recent_chats",
    "popular_topics",
    "system_status"
  ]
}
```

### Update User Preferences

```http
PATCH /api/sapbot/v1/user/preferences/
```

**Request Body:**
```json
{
  "theme": "dark",
  "font_size": 16,
  "sound_enabled": false
}
```

### Get User Activity

```http
GET /api/sapbot/v1/user/activity/
```

**Query Parameters:**
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `activity_type` (optional): Filter by activity type
- `limit` (optional): Number of results

**Response:**
```json
{
  "total_activities": 156,
  "activities": [
    {
      "id": "activity_123",
      "activity_type": "chat",
      "description": "Chat session started",
      "timestamp": "2025-01-16T10:30:00Z",
      "metadata": {
        "session_duration": 1800,
        "message_count": 12
      }
    }
  ]
}
```

### Generate API Key

```http
POST /api/sapbot/v1/user/api-keys/
```

**Request Body:**
```json
{
  "name": "Mobile App Integration",
  "permissions": ["chat", "search"],
  "rate_limit": 100,
  "expires_in_days": 90
}
```

**Response:**
```json
{
  "id": "key_123456",
  "name": "Mobile App Integration",
  "key": "sapbot_1234567890abcdef...",
  "permissions": ["chat", "search"],
  "rate_limit": 100,
  "created_at": "2025-01-16T11:00:00Z",
  "expires_at": "2025-04-16T11:00:00Z"
}
```

---

## 📊 Analytics API

### Dashboard Analytics

```http
GET /api/sapbot/v1/analytics/dashboard/
```

**Query Parameters:**
- `period` (optional): Time period (daily, weekly, monthly)
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Response:**
```json
{
  "period": "monthly",
  "summary": {
    "total_queries": 2456,
    "unique_users": 89,
    "avg_response_time": 2.3,
    "success_rate": 0.92,
    "user_satisfaction": 4.2
  },
  "trends": {
    "daily_queries": [
      {"date": "2025-01-15", "count": 89},
      {"date": "2025-01-16", "count": 156}
    ],
    "popular_modules": [
      {"module": "FI", "count": 567, "percentage": 23.1},
      {"module": "MM", "count": 445, "percentage": 18.1}
    ]
  },
  "user_metrics": {
    "new_users": 12,
    "active_users": 89,
    "returning_users": 77
  }
}
```

### Module Analytics

```http
GET /api/sapbot/v1/analytics/modules/
```

**Response:**
```json
{
  "modules": [
    {
      "module": "FI",
      "name": "Mali Muhasebe",
      "query_count": 567,
      "success_rate": 0.94,
      "avg_response_time": 2.1,
      "user_satisfaction": 4.3,
      "top_intents": [
        {"intent": "how_to", "count": 234},
        {"intent": "error_solving", "count": 189}
      ],
      "popular_topics": [
        "fatura kesme",
        "muhasebe kaydı",
        "rapor alma"
      ]
    }
  ]
}
```

### User Analytics

```http
GET /api/sapbot/v1/analytics/users/
```

**Query Parameters:**
- `user_type` (optional): Filter by user type
- `department` (optional): Filter by department
- `period` (optional): Time period

**Response:**
```json
{
  "user_statistics": {
    "total_users": 245,
    "active_users": 89,
    "by_type": {
      "user": 189,
      "technical": 45,
      "admin": 11
    },
    "by_department": {
      "Muhasebe": 67,
      "Satış": 45,
      "Satın Alma": 23
    }
  },
  "engagement_metrics": {
    "avg_session_duration": 1245,
    "avg_queries_per_user": 15.6,
    "return_rate": 0.78
  }
}
```

### Export Analytics

```http
POST /api/sapbot/v1/analytics/export/
```

**Request Body:**
```json
{
  "report_type": "user_activity",
  "format": "excel",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "filters": {
    "user_type": "user",
    "sap_module": "FI"
  }
}
```

**Response:**
```json
{
  "export_id": "export_123456",
  "status": "processing",
  "estimated_completion": "2025-01-16T11:15:00Z",
  "download_url": null
}
```

### Get Export Status

```http
GET /api/sapbot/v1/analytics/export/{export_id}/
```

**Response:**
```json
{
  "export_id": "export_123456",
  "status": "completed",
  "file_size": 2048576,
  "record_count": 1456,
  "download_url": "https://api.sapbot.tunacelik.com.tr/exports/export_123456.xlsx",
  "expires_at": "2025-01-23T11:15:00Z"
}
```

---

## 🖥️ System API

### Health Check

```http
GET /api/sapbot/v1/health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T11:00:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "openai_api": "healthy",
    "document_processor": "healthy",
    "search_engine": "healthy"
  },
  "metrics": {
    "uptime": 2592000,
    "response_time": 45,
    "active_connections": 23
  }
}
```

### System Statistics

```http
GET /api/sapbot/v1/system/stats/
```

**Response:**
```json
{
  "system_info": {
    "version": "1.0.0",
    "environment": "production",
    "uptime": 2592000,
    "last_deployment": "2025-01-10T14:30:00Z"
  },
  "database_stats": {
    "total_documents": 1456,
    "total_chunks": 234567,
    "processed_documents": 1442,
    "failed_documents": 14
  },
  "performance_metrics": {
    "avg_response_time": 2.3,
    "requests_per_minute": 45,
    "error_rate": 0.02,
    "cache_hit_rate": 0.87
  },
  "storage_usage": {
    "documents": "15.6 GB",
    "database": "2.3 GB",
    "cache": "512 MB",
    "logs": "1.2 GB"
  }
}
```

### System Configuration

```http
GET /api/sapbot/v1/system/config/
```

**Response:**
```json
{
  "configurations": [
    {
      "key": "max_upload_size_mb",
      "value": "100",
      "description": "Maksimum dosya yükleme boyutu (MB)",
      "category": "upload"
    },
    {
      "key": "chat_response_timeout",
      "value": "30",
      "description": "Chat yanıt timeout süresi (saniye)",
      "category": "chat"
    }
  ]
}
```

### Update System Configuration

```http
PUT /api/sapbot/v1/system/config/{config_key}/
```

**Request Body:**
```json
{
  "value": "150"
}
```

### System Logs

```http
GET /api/sapbot/v1/system/logs/
```

**Query Parameters:**
- `level` (optional): Log level (DEBUG, INFO, WARNING, ERROR)
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `limit` (optional): Number of logs

**Response:**
```json
{
  "logs": [
    {
      "id": "log_123456",
      "level": "INFO",
      "message": "User authentication successful",
      "timestamp": "2025-01-16T10:30:00Z",
      "module": "auth",
      "user_id": "user_789",
      "session_id": "session_456"
    }
  ]
}
```

---

## 🚨 Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Geçersiz veri gönderildi",
    "details": {
      "field": "message",
      "reason": "Bu alan gereklidir"
    },
    "timestamp": "2025-01-16T11:00:00Z",
    "request_id": "req_123456"
  }
}
```

### HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| 200  | OK | Successful request |
| 201  | Created | Resource created successfully |
| 400  | Bad Request | Invalid request data |
| 401  | Unauthorized | Authentication required |
| 403  | Forbidden | Insufficient permissions |
| 404  | Not Found | Resource not found |
| 409  | Conflict | Resource already exists |
| 422  | Unprocessable Entity | Validation failed |
| 429  | Too Many Requests | Rate limit exceeded |
| 500  | Internal Server Error | Server error |
| 503  | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `PROCESSING_ERROR` | Document processing failed |
| `EXTERNAL_SERVICE_ERROR` | External service unavailable |
| `QUOTA_EXCEEDED` | Usage quota exceeded |
| `MAINTENANCE_MODE` | System in maintenance mode |

---

## ⚡ Rate Limiting

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642329600
X-RateLimit-Window: 3600
```

### Rate Limits by Endpoint

| Endpoint | Rate Limit | Window |
|----------|------------|---------|
| `/chat/message/` | 100 requests | 1 hour |
| `/documents/upload/` | 10 requests | 1 hour |
| `/search/knowledge/` | 200 requests | 1 hour |
| `/analytics/*` | 50 requests | 1 hour |
| All other endpoints | 1000 requests | 1 hour |

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 100,
      "window": 3600,
      "reset_time": "2025-01-16T12:00:00Z"
    }
  }
}
```

---

## 📡 Webhooks

### Webhook Events

| Event | Description |
|-------|-------------|
| `document.processed` | Document processing completed |
| `document.failed` | Document processing failed |
| `user.registered` | New user registered |
| `system.maintenance` | System maintenance started |
| `analytics.report` | Analytics report generated |

### Webhook Payload Example

```json
{
  "event": "document.processed",
  "timestamp": "2025-01-16T11:00:00Z",
  "data": {
    "document_id": "doc_123456",
    "title": "SAP B1 Kullanım Kılavuzu",
    "chunks_created": 234,
    "processing_time": 892
  },
  "webhook_id": "webhook_789012"
}
```

### Webhook Configuration

```http
POST /api/sapbot/v1/webhooks/
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/sapbot",
  "events": ["document.processed", "document.failed"],
  "secret": "your_webhook_secret"
}
```

---

## 🛠️ SDK ve Examples

### JavaScript SDK

```javascript
// Installation
npm install @sapbot/api-client

// Usage
import SAPBotClient from '@sapbot/api-client';

const client = new SAPBotClient({
  baseURL: 'https://api.sapbot.tunacelik.com.tr',
  apiKey: 'your_api_key'
});

// Send chat message
const response = await client.chat.sendMessage({
  message: 'SAP B1\'de stok raporu nasıl alınır?',
  sessionId: 'session_123',
  userType: 'user'
});

console.log(response.data.response);
```

### Python SDK

```python
# Installation
pip install sapbot-api-client

# Usage
from sapbot_api import SAPBotClient

client = SAPBotClient(
    base_url='https://api.sapbot.tunacelik.com.tr',
    api_key='your_api_key'
)

# Send chat message
response = client.chat.send_message(
    message='SAP B1\'de stok raporu nasıl alınır?',
    session_id='session_123',
    user_type='user'
)

print(response.response)
```

### cURL Examples

```bash
# Send chat message
curl -X POST \
  https://api.sapbot.tunacelik.com.tr/api/sapbot/v1/chat/message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SAP B1'\''de stok raporu nasıl alınır?",
    "session_id": "session_123",
    "user_type": "user"
  }'

# Upload document
curl -X POST \
  https://api.sapbot.tunacelik.com.tr/api/sapbot/v1/documents/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \