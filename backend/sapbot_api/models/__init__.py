# backend/sapbot_api/models/__init__.py
"""
SAPBot API Models

Bu modül SAP Business One HANA ERP AI Support System için
tüm model sınıflarını organize eder.
"""

# Base models
from .base import (
    BaseModel,
    TimestampedModel,
    SoftDeleteModel,
    SoftDeleteManager,
    CacheableModel,
    AuditModel
)

# Document models
from .document import (
    DocumentSource,
    KnowledgeChunk,
    DocumentTag,
    DocumentChunkRelation
)

# Chat models
from .chat import (
    ChatConversation,
    ChatMessage,
    MessageFeedback,
    ConversationSummary
)

# User models
from .user import (
    UserProfile,
    UserPreferences,
    UserSession,
    UserActivity,
    UserApiKey
)

# Analytics models
from .analytics import (
    QueryAnalytics,
    UserFeedback,
    UsageStatistics,
    PerformanceMetrics,
    ErrorLog
)

# System models
from .system import (
    SystemConfiguration,
    SystemMetrics,
    SystemLog,
    SystemHealth,
    APIQuota,
    SystemNotification,
    MaintenanceWindow
)

# Tüm modelleri export et
__all__ = [
    # Base models
    'BaseModel',
    'TimestampedModel',
    'SoftDeleteModel',
    'SoftDeleteManager',
    'CacheableModel',
    'AuditModel',
    
    # Document models
    'DocumentSource',
    'KnowledgeChunk',
    'DocumentTag',
    'DocumentChunkRelation',
    
    # Chat models
    'ChatConversation',
    'ChatMessage',
    'MessageFeedback',
    'ConversationSummary',
    
    # User models
    'UserProfile',
    'UserPreferences',
    'UserSession',
    'UserActivity',
    'UserApiKey',
    
    # Analytics models
    'QueryAnalytics',
    'UserFeedback',
    'UsageStatistics',
    'PerformanceMetrics',
    'ErrorLog',
    
    # System models
    'SystemConfiguration',
    'SystemMetrics',
    'SystemLog',
    'SystemHealth',
    'APIQuota',
    'SystemNotification',
    'MaintenanceWindow',
]

# Model kategorileri
DOCUMENT_MODELS = [
    'DocumentSource',
    'KnowledgeChunk',
    'DocumentTag',
    'DocumentChunkRelation',
]

CHAT_MODELS = [
    'ChatConversation',
    'ChatMessage',
    'MessageFeedback',
    'ConversationSummary',
]

USER_MODELS = [
    'UserProfile',
    'UserPreferences',
    'UserSession',
    'UserActivity',
    'UserApiKey',
]

ANALYTICS_MODELS = [
    'QueryAnalytics',
    'UserFeedback',
    'UsageStatistics',
    'PerformanceMetrics',
    'ErrorLog',
]

SYSTEM_MODELS = [
    'SystemConfiguration',
    'SystemMetrics',
    'SystemLog',
    'SystemHealth',
    'APIQuota',
    'SystemNotification',
    'MaintenanceWindow',
]

BASE_MODELS = [
    'BaseModel',
    'TimestampedModel',
    'SoftDeleteModel',
    'SoftDeleteManager',
    'CacheableModel',
    'AuditModel',
]

# Model sayısı istatistikleri
MODEL_COUNTS = {
    'base': len(BASE_MODELS),
    'document': len(DOCUMENT_MODELS),
    'chat': len(CHAT_MODELS),
    'user': len(USER_MODELS),
    'analytics': len(ANALYTICS_MODELS),
    'system': len(SYSTEM_MODELS),
    'total': len(__all__)
}

# Versiyon bilgisi
MODELS_VERSION = '1.0.0'
MODELS_DESCRIPTION = 'SAPBot API Models - SAP Business One HANA ERP AI Support System'

def get_model_info():
    """Model bilgilerini döndür"""
    return {
        'version': MODELS_VERSION,
        'description': MODELS_DESCRIPTION,
        'counts': MODEL_COUNTS,
        'categories': {
            'base': BASE_MODELS,
            'document': DOCUMENT_MODELS,
            'chat': CHAT_MODELS,
            'user': USER_MODELS,
            'analytics': ANALYTICS_MODELS,
            'system': SYSTEM_MODELS,
        }
    }

def get_all_models():
    """Tüm modelleri döndür"""
    return __all__

def get_models_by_category(category):
    """Kategoriye göre modelleri döndür"""
    category_map = {
        'base': BASE_MODELS,
        'document': DOCUMENT_MODELS,
        'chat': CHAT_MODELS,
        'user': USER_MODELS,
        'analytics': ANALYTICS_MODELS,
        'system': SYSTEM_MODELS,
    }
    return category_map.get(category, [])

# Model import helper
def import_model(model_name):
    """Model adına göre model sınıfını döndür"""
    current_module = __import__(__name__, fromlist=[model_name])
    return getattr(current_module, model_name, None)