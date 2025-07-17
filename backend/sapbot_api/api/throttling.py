# backend/sapbot_api/throttling.py
"""
SAPBot API Rate Limiting

Mevcut DRF throttling yapısı ile uyumlu custom throttle sınıfları.
Circular import'u önlemek için base throttle sınıfları kullanılıyor.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ChatRateThrottle(UserRateThrottle):
    """
    SAPBot Chat endpoint için özelleştirilmiş rate limiting
    Scope: 'chat' - 60/hour
    """
    scope = 'chat'
    
    def get_cache_key(self, request, view):
        """Chat özel cache key oluştur"""
        if request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            ident = f"anon_{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """
        Chat özel allow logic
        - Süper kullanıcılar için rate limit yok
        - Technical user'lar için artırılmış limit
        """
        # Süper kullanıcılar için rate limit yok
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        
        # Technical user'lar için artırılmış limit
        if request.user.is_authenticated:
            try:
                profile = request.user.sapbot_profile
                if profile.user_type in ['technical', 'admin']:
                    # Technical user'lar için 2x limit
                    self.rate = '120/hour'
            except AttributeError:
                pass
        
        return super().allow_request(request, view)
    
    def get_rate_description(self):
        """Rate açıklaması"""
        return "Chat mesajları için saatlik limit"


class UploadRateThrottle(UserRateThrottle):
    """
    SAPBot Upload endpoint için rate limiting
    Scope: 'upload' - 10/hour
    """
    scope = 'upload'
    
    def get_cache_key(self, request, view):
        """Upload özel cache key"""
        if request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            ident = f"anon_{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """Upload özel logic"""
        # Admin kullanıcılar için artırılmış limit
        if request.user.is_authenticated:
            try:
                profile = request.user.sapbot_profile
                if profile.user_type == 'admin':
                    self.rate = '50/hour'  # Admin'ler için 5x limit
                elif profile.user_type == 'technical':
                    self.rate = '25/hour'  # Technical için 2.5x limit
            except AttributeError:
                pass
        
        return super().allow_request(request, view)
    
    def get_rate_description(self):
        """Rate açıklaması"""
        return "Dosya yükleme için saatlik limit"


class SearchRateThrottle(UserRateThrottle):
    """
    SAPBot Search endpoint için rate limiting
    Scope: 'search' - 120/hour
    """
    scope = 'search'
    
    def get_cache_key(self, request, view):
        """Search özel cache key"""
        if request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            ident = f"anon_{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """Search özel logic"""
        # Yoğun arama yapan kullanıcılar için artırılmış limit
        if request.user.is_authenticated:
            try:
                profile = request.user.sapbot_profile
                if profile.user_type in ['technical', 'admin']:
                    self.rate = '300/hour'  # Technical/Admin için artırılmış limit
            except AttributeError:
                pass
        
        return super().allow_request(request, view)
    
    def get_rate_description(self):
        """Rate açıklaması"""
        return "Arama sorguları için saatlik limit"


class BurstProtectionThrottle(UserRateThrottle):
    """
    Burst attack protection için çok kısa süreli sıkı limit
    DDoS benzeri saldırıları önlemek için
    """
    scope = 'burst'
    rate = '30/min'  # Dakika başına 30 request
    
    def get_cache_key(self, request, view):
        """Burst protection için IP bazlı key"""
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """Burst protection logic"""
        # Güvenilir IP'ler için burst protection yok
        trusted_ips = getattr(settings, 'TRUSTED_IPS', [])
        client_ip = self.get_ident(request)
        
        if client_ip in trusted_ips:
            return True
        
        return super().allow_request(request, view)


class APIKeyThrottle(UserRateThrottle):
    """
    API Key bazlı throttling
    3rd party integrations için
    """
    scope = 'api_key'
    rate = '1000/hour'  # API key'ler için yüksek limit
    
    def get_cache_key(self, request, view):
        """API Key bazlı cache key"""
        # API key'i header'dan al
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            ident = f"apikey_{api_key[:8]}"  # Security için sadece ilk 8 karakter
        else:
            ident = f"nokey_{self.get_ident(request)}"
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """API Key validation ile birlikte throttling"""
        # API key yoksa sıkı limit uygula
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            self.rate = '20/hour'  # API key yoksa çok sıkı limit
        
        return super().allow_request(request, view)


class ThrottleStatusHelper:
    """
    Throttle durumu ve bilgileri için helper sınıfı
    """
    
    @staticmethod
    def get_throttle_info(request, throttle_class) -> Dict[str, Any]:
        """Throttle bilgilerini al"""
        try:
            throttle = throttle_class()
            allowed = throttle.allow_request(request, None)
            
            # Rate bilgilerini parse et
            rate_info = throttle.parse_rate(throttle.get_rate())
            if rate_info:
                num_requests, duration = rate_info
                
                # Cache'den history al
                cache_key = throttle.get_cache_key(request, None)
                history = cache.get(cache_key, [])
                
                # Remaining hesapla
                remaining = max(0, num_requests - len(history))
                
                # Reset time hesapla
                reset_time = None
                if history:
                    import time
                    reset_time = int(time.time() + duration)
                
                return {
                    'allowed': allowed,
                    'limit': num_requests,
                    'remaining': remaining,
                    'reset_time': reset_time,
                    'duration': duration,
                    'scope': throttle.scope,
                    'rate': throttle.get_rate()
                }
            else:
                return {
                    'allowed': allowed,
                    'error': 'Invalid rate configuration'
                }
                
        except Exception as e:
            logger.error(f"Throttle info error: {e}")
            return {
                'allowed': True,
                'error': str(e)
            }
    
    @staticmethod
    def get_all_throttle_info(request) -> Dict[str, Any]:
        """Tüm throttle bilgilerini al"""
        throttle_classes = {
            'chat': ChatRateThrottle,
            'upload': UploadRateThrottle,
            'search': SearchRateThrottle,
            'burst': BurstProtectionThrottle,
            'api_key': APIKeyThrottle
        }
        
        info = {}
        for name, throttle_class in throttle_classes.items():
            info[name] = ThrottleStatusHelper.get_throttle_info(request, throttle_class)
        
        return info
    
    @staticmethod
    def clear_user_throttle(user_id: int, scope: str = None):
        """Kullanıcının throttle cache'ini temizle"""
        try:
            scopes = [scope] if scope else ['chat', 'upload', 'search', 'burst']
            
            for s in scopes:
                cache_key = f"throttle_{s}_user_{user_id}"
                cache.delete(cache_key)
            
            logger.info(f"Throttle cache cleared for user {user_id}, scopes: {scopes}")
            return True
        except Exception as e:
            logger.error(f"Clear throttle cache error: {e}")
            return False


# Decorator'lar
def require_throttle_scope(scope: str):
    """View'lar için throttle scope gerektiren decorator"""
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            throttle_class = {
                'chat': ChatRateThrottle,
                'upload': UploadRateThrottle,
                'search': SearchRateThrottle,
                'burst': BurstProtectionThrottle
            }.get(scope)
            
            if throttle_class:
                throttle = throttle_class()
                if not throttle.allow_request(request, self):
                    from rest_framework.exceptions import Throttled
                    wait_time = throttle.wait()
                    raise Throttled(
                        detail=f"{scope} rate limit exceeded",
                        wait=wait_time
                    )
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# Utility fonksiyonlar
def get_client_identifier(request) -> str:
    """Client identifier al (User ID, API Key veya IP)"""
    # API Key varsa öncelik ver
    api_key = request.META.get('HTTP_X_API_KEY')
    if api_key:
        return f"apikey_{api_key[:8]}"
    
    # Authenticated user
    if request.user.is_authenticated:
        return f"user_{request.user.pk}"
    
    # IP bazlı
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    return f"ip_{ip}"


def is_rate_limited(request, scope: str) -> bool:
    """Hızlı rate limit kontrolü"""
    throttle_classes = {
        'chat': ChatRateThrottle,
        'upload': UploadRateThrottle,
        'search': SearchRateThrottle,
        'burst': BurstProtectionThrottle
    }
    
    throttle_class = throttle_classes.get(scope)
    if not throttle_class:
        return False
    
    try:
        throttle = throttle_class()
        return not throttle.allow_request(request, None)
    except Exception as e:
        logger.error(f"Rate limit check error for {scope}: {e}")
        return False


def get_rate_limit_headers(request) -> Dict[str, str]:
    """Response headers için rate limit bilgileri"""
    headers = {}
    
    try:
        # Chat throttle bilgisi
        chat_info = ThrottleStatusHelper.get_throttle_info(request, ChatRateThrottle)
        if 'limit' in chat_info:
            headers['X-RateLimit-Limit-Chat'] = str(chat_info['limit'])
            headers['X-RateLimit-Remaining-Chat'] = str(chat_info['remaining'])
            if chat_info.get('reset_time'):
                headers['X-RateLimit-Reset-Chat'] = str(chat_info['reset_time'])
        
        # Upload throttle bilgisi
        upload_info = ThrottleStatusHelper.get_throttle_info(request, UploadRateThrottle)
        if 'limit' in upload_info:
            headers['X-RateLimit-Limit-Upload'] = str(upload_info['limit'])
            headers['X-RateLimit-Remaining-Upload'] = str(upload_info['remaining'])
            if upload_info.get('reset_time'):
                headers['X-RateLimit-Reset-Upload'] = str(upload_info['reset_time'])
    
    except Exception as e:
        logger.error(f"Rate limit headers error: {e}")
    
    return headers


def log_throttle_event(request, throttle_class, action: str = 'hit'):
    """Throttle olaylarını logla"""
    try:
        identifier = get_client_identifier(request)
        scope = getattr(throttle_class, 'scope', 'unknown')
        
        logger.info(f"Throttle {action}: {scope} - {identifier}", extra={
            'throttle_scope': scope,
            'client_identifier': identifier,
            'user_id': request.user.pk if request.user.is_authenticated else None,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'action': action
        })
    except Exception as e:
        logger.error(f"Throttle logging error: {e}")