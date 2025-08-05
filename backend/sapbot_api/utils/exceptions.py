# backend/sapbot_api/utils/exceptions.py
"""
SAPBot API Custom Exceptions

Bu modül SAPBot API için özel exception sınıflarını içerir.
Tüm exception'lar Türkçe hata mesajları ile birlikte gelir.
"""

from typing import Dict, Any, Optional
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class SAPBotException(Exception):
    """SAPBot API temel exception sınıfı"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SAPBOT_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Exception'ı dictionary'e çevir"""
        return {
            'error': {
                'code': self.error_code,
                'message': self.message,
                'details': self.details,
                'status_code': self.status_code
            }
        }


class ValidationException(SAPBotException):
    """Veri doğrulama hatası"""
    
    def __init__(
        self,
        message: str = "Geçersiz veri gönderildi",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class AuthenticationException(SAPBotException):
    """Kimlik doğrulama hatası"""
    
    def __init__(
        self,
        message: str = "Kimlik doğrulama başarısız",
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )


class AuthorizationException(SAPBotException):
    """Yetkilendirme hatası"""
    
    def __init__(
        self,
        message: str = "Bu işlem için yetkiniz bulunmuyor",
        required_permission: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ResourceNotFoundException(SAPBotException):
    """Kaynak bulunamadı hatası"""
    
    def __init__(
        self,
        message: str = "Kaynak bulunamadı",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class DocumentProcessingError(SAPBotException):
    """Döküman işleme hatası"""
    
    def __init__(
        self,
        message: str = "Döküman işleme sırasında hata oluştu",
        document_id: Optional[str] = None,
        processing_stage: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if document_id:
            details['document_id'] = document_id
        if processing_stage:
            details['processing_stage'] = processing_stage
        
        super().__init__(
            message=message,
            error_code="DOCUMENT_PROCESSING_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class EmbeddingError(SAPBotException):
    """Embedding oluşturma hatası"""
    
    def __init__(
        self,
        message: str = "Embedding oluşturma sırasında hata oluştu",
        content_hash: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if content_hash:
            details['content_hash'] = content_hash
        if model_name:
            details['model_name'] = model_name
        
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class SearchError(SAPBotException):
    """Arama hatası"""
    
    def __init__(
        self,
        message: str = "Arama sırasında hata oluştu",
        query: Optional[str] = None,
        search_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if query:
            details['query'] = query[:100]  # Sadece ilk 100 karakter
        if search_type:
            details['search_type'] = search_type
        
        super().__init__(
            message=message,
            error_code="SEARCH_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ChatError(SAPBotException):
    """Chat hatası"""
    
    def __init__(
        self,
        message: str = "Chat işlemi sırasında hata oluştu",
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if session_id:
            details['session_id'] = session_id
        if message_id:
            details['message_id'] = message_id
        
        super().__init__(
            message=message,
            error_code="CHAT_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceError(SAPBotException):
    """Harici servis hatası"""
    
    def __init__(
        self,
        message: str = "Harici servis hatası",
        service_name: Optional[str] = None,
        service_response: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if service_name:
            details['service_name'] = service_name
        if service_response:
            details['service_response'] = service_response[:200]  # İlk 200 karakter
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class OpenAIError(ExternalServiceError):
    """OpenAI API hatası"""
    
    def __init__(
        self,
        message: str = "OpenAI API hatası",
        model: Optional[str] = None,
        error_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if model:
            details['model'] = model
        if error_type:
            details['error_type'] = error_type
        
        super().__init__(
            message=message,
            service_name="OpenAI",
            **kwargs
        )


class RateLimitError(SAPBotException):
    """Rate limit hatası"""
    
    def __init__(
        self,
        message: str = "Çok fazla istek. Lütfen bekleyiniz.",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        reset_time: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if limit:
            details['limit'] = limit
        if window:
            details['window'] = window
        if reset_time:
            details['reset_time'] = reset_time
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class QuotaExceededError(SAPBotException):
    """Kota aşım hatası"""
    
    def __init__(
        self,
        message: str = "Kullanım kotanız aşıldı",
        quota_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if quota_type:
            details['quota_type'] = quota_type
        if current_usage is not None:
            details['current_usage'] = current_usage
        if limit is not None:
            details['limit'] = limit
        
        super().__init__(
            message=message,
            error_code="QUOTA_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class MaintenanceError(SAPBotException):
    """Bakım modu hatası"""
    
    def __init__(
        self,
        message: str = "Sistem bakım modunda. Lütfen daha sonra tekrar deneyiniz.",
        maintenance_end: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if maintenance_end:
            details['maintenance_end'] = maintenance_end
        
        super().__init__(
            message=message,
            error_code="MAINTENANCE_MODE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class ConfigurationError(SAPBotException):
    """Konfigürasyon hatası"""
    
    def __init__(
        self,
        message: str = "Sistem konfigürasyon hatası",
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class DatabaseError(SAPBotException):
    """Veritabanı hatası"""
    
    def __init__(
        self,
        message: str = "Veritabanı hatası",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class CacheError(SAPBotException):
    """Cache hatası"""
    
    def __init__(
        self,
        message: str = "Cache sistemi hatası",
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if cache_key:
            details['cache_key'] = cache_key
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class FileUploadError(SAPBotException):
    """Dosya yükleme hatası"""
    
    def __init__(
        self,
        message: str = "Dosya yükleme hatası",
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        max_size: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if file_name:
            details['file_name'] = file_name
        if file_size is not None:
            details['file_size'] = file_size
        if max_size is not None:
            details['max_size'] = max_size
        
        super().__init__(
            message=message,
            error_code="FILE_UPLOAD_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


# SAP B1 Özelinde Exception'lar
class SAPModuleError(SAPBotException):
    """SAP modül hatası"""
    
    def __init__(
        self,
        message: str = "SAP modül hatası",
        sap_module: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if sap_module:
            details['sap_module'] = sap_module
        
        super().__init__(
            message=message,
            error_code="SAP_MODULE_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class IntentDetectionError(SAPBotException):
    """Niyet tespit hatası"""
    
    def __init__(
        self,
        message: str = "Kullanıcı niyeti tespit edilemedi",
        query: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if query:
            details['query'] = query[:100]
        
        super().__init__(
            message=message,
            error_code="INTENT_DETECTION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


# Exception Handler
def custom_exception_handler(exc, context):
    """SAPBot özel exception handler"""
    
    # Önce DRF'nin standart handler'ını çağır
    response = exception_handler(exc, context)
    
    # SAPBot exception'ları için özel işleme
    if isinstance(exc, SAPBotException):
        # Log exception
        logger.error(f"SAPBot Exception: {exc.error_code} - {exc.message}", extra={
            'exception_type': type(exc).__name__,
            'error_code': exc.error_code,
            'details': exc.details,
            'context': context
        })
        
        # Custom response
        custom_response_data = {
            'error': {
                'code': exc.error_code,
                'message': exc.message,
                'details': exc.details,
                'timestamp': logger.formatTime(logger.makeLogRecord({}))
            }
        }
        
        return Response(
            custom_response_data,
            status=exc.status_code
        )
    
    # Django ValidationError'ları için
    elif isinstance(exc, ValidationError):
        logger.warning(f"Validation Error: {exc}")
        
        custom_response_data = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Veri doğrulama hatası',
                'details': {'validation_errors': exc.messages},
                'timestamp': logger.formatTime(logger.makeLogRecord({}))
            }
        }
        
        return Response(
            custom_response_data,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Diğer exception'lar için standart response'u döndür
    if response is not None:
        # Standart DRF response'unu SAPBot formatına çevir
        custom_response_data = {
            'error': {
                'code': 'API_ERROR',
                'message': 'API hatası',
                'details': response.data,
                'timestamp': logger.formatTime(logger.makeLogRecord({}))
            }
        }
        
        response.data = custom_response_data
    
    return response


# Utility functions
def raise_validation_error(message: str, field: str = None, value: Any = None):
    """Validation error fırlat"""
    raise ValidationException(message=message, field=field, value=value)


def raise_not_found_error(message: str, resource_type: str = None, resource_id: str = None):
    """Not found error fırlat"""
    raise ResourceNotFoundException(
        message=message,
        resource_type=resource_type,
        resource_id=resource_id
    )


def raise_auth_error(message: str = "Kimlik doğrulama başarısız"):
    """Authentication error fırlat"""
    raise AuthenticationException(message=message)


def raise_permission_error(message: str = "Bu işlem için yetkiniz bulunmuyor", required_permission: str = None):
    """Permission error fırlat"""
    raise AuthorizationException(message=message, required_permission=required_permission)


def raise_rate_limit_error(limit: int, window: int, reset_time: str = None):
    """Rate limit error fırlat"""
    raise RateLimitError(
        limit=limit,
        window=window,
        reset_time=reset_time
    )


def raise_external_service_error(service_name: str, error_message: str):
    """External service error fırlat"""
    raise ExternalServiceError(
        message=f"{service_name} servis hatası: {error_message}",
        service_name=service_name,
        service_response=error_message
    )


def handle_openai_error(error):
    """OpenAI hatalarını handle et"""
    if hasattr(error, 'error') and hasattr(error.error, 'type'):
        error_type = error.error.type
        
        if error_type == 'insufficient_quota':
            raise QuotaExceededError(
                message="OpenAI API kotası aşıldı",
                quota_type="openai_tokens"
            )
        elif error_type == 'rate_limit_exceeded':
            raise RateLimitError(
                message="OpenAI API rate limit aşıldı"
            )
        elif error_type == 'invalid_request_error':
            raise ValidationException(
                message="OpenAI API geçersiz istek"
            )
        else:
            raise OpenAIError(
                message=f"OpenAI API hatası: {error.error.message}",
                error_type=error_type
            )
    else:
        raise OpenAIError(
            message=f"OpenAI API hatası: {str(error)}"
        )


# Error code constants
ERROR_CODES = {
    'VALIDATION_ERROR': 'VALIDATION_ERROR',
    'AUTHENTICATION_ERROR': 'AUTHENTICATION_ERROR',
    'AUTHORIZATION_ERROR': 'AUTHORIZATION_ERROR',
    'RESOURCE_NOT_FOUND': 'RESOURCE_NOT_FOUND',
    'DOCUMENT_PROCESSING_ERROR': 'DOCUMENT_PROCESSING_ERROR',
    'EMBEDDING_ERROR': 'EMBEDDING_ERROR',
    'SEARCH_ERROR': 'SEARCH_ERROR',
    'CHAT_ERROR': 'CHAT_ERROR',
    'EXTERNAL_SERVICE_ERROR': 'EXTERNAL_SERVICE_ERROR',
    'RATE_LIMIT_EXCEEDED': 'RATE_LIMIT_EXCEEDED',
    'QUOTA_EXCEEDED': 'QUOTA_EXCEEDED',
    'MAINTENANCE_MODE': 'MAINTENANCE_MODE',
    'CONFIGURATION_ERROR': 'CONFIGURATION_ERROR',
    'DATABASE_ERROR': 'DATABASE_ERROR',
    'CACHE_ERROR': 'CACHE_ERROR',
    'FILE_UPLOAD_ERROR': 'FILE_UPLOAD_ERROR',
    'SAP_MODULE_ERROR': 'SAP_MODULE_ERROR',
    'INTENT_DETECTION_ERROR': 'INTENT_DETECTION_ERROR'
}

# ------------------------------------------------------------------------
# Güvenlik / denetim odaklı hata
# ------------------------------------------------------------------------
class SecurityException(SAPBotException):
    """Güvenlik ihlali veya denetim hatası"""

    def __init__(
        self,
        message: str = "Güvenlik ihlali tespit edildi",
        event_type: str | None = None,
        severity: str | None = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if event_type:
            details["event_type"] = event_type
        if severity:
            details["severity"] = severity

        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )
