
# backend/sapbot_api/utils/security.py
"""
SAPBot API Security Utilities

Bu modül güvenlik ile ilgili fonksiyonları içerir:
- Input sanitization
- Rate limiting
- Token validation
- Permission checking
- Audit logging
"""

import re
import hashlib
import hmac
import secrets
import ipaddress
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from functools import wraps
import logging

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone
from rest_framework.request import Request
import jwt

from .exceptions import (
    AuthenticationException,
    AuthorizationException,
    RateLimitError,
    ValidationException,
    SecurityException
)
from .helpers import get_client_ip, get_user_agent, generate_hash

User = get_user_model()
logger = logging.getLogger(__name__)


class SecurityException(Exception):
    """Güvenlik hatası"""
    pass


class InputSanitizer:
    """Kullanıcı girişi temizleme ve doğrulama"""
    
    # Zararlı pattern'lar
    MALICIOUS_PATTERNS = [
        # XSS patterns
        r'<script[^>]*>.*?</script>',
        r'javascript\s*:',
        r'vbscript\s*:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        
        # SQL injection patterns
        r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)',
        r'(\bOR\b.*=.*|\bAND\b.*=.*)',
        r'(--|/\*|\*/|;)',
        r'(\bEXEC\b|\bEXECUTE\b|\bSP_\w+)',
        
        # Command injection patterns
        r'(\||&&|;|\$\(|\`)',
        r'(bash|sh|cmd|powershell|nc|netcat)',
        r'(wget|curl|ping|nslookup)',
        
        # Path traversal
        r'(\.\./|\.\.\\)',
        r'(/etc/passwd|/etc/shadow)',
        r'(\\windows\\system32)',
        
        # PHP patterns
        r'(<\?php|\?>)',
        r'(eval\s*\(|exec\s*\(|system\s*\()',
        r'(include\s*\(|require\s*\()',
    ]
    
    @classmethod
    def sanitize_string(cls, input_str: str, max_length: int = 2000, allow_html: bool = False) -> str:
        """String'i temizle"""
        if not isinstance(input_str, str):
            return ""
        
        # Uzunluk kontrolü
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        # HTML'e izin verilmiyorsa temizle
        if not allow_html:
            input_str = re.sub(r'<[^>]+>', '', input_str)
        
        # Zararlı pattern kontrolü
        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                logger.warning(f"Zararlı pattern tespit edildi: {pattern}")
                raise ValidationException(
                    message="Güvenlik kontrolünden geçemeyen içerik tespit edildi",
                    field="input_validation"
                )
        
        # Özel karakterleri escape et
        input_str = input_str.replace('<', '&lt;').replace('>', '&gt;')
        input_str = input_str.replace('"', '&quot;').replace("'", '&#x27;')
        
        # Gereksiz boşlukları temizle
        input_str = ' '.join(input_str.split())
        
        return input_str.strip()
    
    @classmethod
    def sanitize_chat_message(cls, message: str) -> str:
        """Chat mesajını temizle"""
        return cls.sanitize_string(
            message, 
            max_length=2000, 
            allow_html=False
        )
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Dosya adını temizle"""
        if not filename:
            return "untitled"
        
        # Zararlı karakterleri kaldır
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # Windows'ta yasaklı isimler
        forbidden_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
            'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = filename.rsplit('.', 1)[0].upper()
        if name_without_ext in forbidden_names:
            filename = f"file_{filename}"
        
        # Uzunluk sınırı
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + (f".{ext}" if ext else "")
        
        return filename
    
    @classmethod
    def validate_sql_input(cls, query: str) -> bool:
        """SQL injection kontrolü"""
        dangerous_patterns = [
            r'\bUNION\b.*\bSELECT\b',
            r'\bINSERT\b.*\bINTO\b',
            r'\bUPDATE\b.*\bSET\b',
            r'\bDELETE\b.*\bFROM\b',
            r'\bDROP\b.*\bTABLE\b',
            r'\bALTER\b.*\bTABLE\b',
            r'\bCREATE\b.*\bTABLE\b',
            r';\s*--',
            r'/\*.*\*/',
            r'\bxp_\w+',
            r'\bsp_\w+'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False
        
        return True


class RateLimiter:
    """Rate limiting sistemi"""
    
    @staticmethod
    def get_cache_key(identifier: str, action: str) -> str:
        """Cache anahtarı oluştur"""
        return f"rate_limit:{action}:{identifier}"
    
    @staticmethod
    def is_rate_limited(
        identifier: str, 
        action: str, 
        limit: int, 
        window: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Rate limit kontrolü"""
        cache_key = RateLimiter.get_cache_key(identifier, action)
        
        # Mevcut sayıyı al
        current_count = cache.get(cache_key, 0)
        
        # Limit aşıldı mı?
        if current_count >= limit:
            # Reset zamanını hesapla
            ttl = cache.ttl(cache_key) if hasattr(cache, 'ttl') else window
            reset_time = timezone.now() + timedelta(seconds=ttl)
            
            return True, {
                'limit': limit,
                'current': current_count,
                'window': window,
                'reset_time': reset_time.isoformat(),
                'retry_after': ttl
            }
        
        # Sayıyı artır
        try:
            cache.set(cache_key, current_count + 1, window)
        except Exception as e:
            logger.error(f"Rate limit cache hatası: {e}")
        
        return False, {
            'limit': limit,
            'current': current_count + 1,
            'window': window,
            'remaining': limit - current_count - 1
        }
    
    @staticmethod
    def rate_limit(limit: int = 60, window: int = 3600, key_func=None):
        """Rate limit decorator"""
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                # Identifier belirle
                if key_func:
                    identifier = key_func(request)
                else:
                    identifier = get_client_ip(request)
                
                action = f"{func.__module__}.{func.__name__}"
                
                # Rate limit kontrolü
                is_limited, info = RateLimiter.is_rate_limited(
                    identifier, action, limit, window
                )
                
                if is_limited:
                    raise RateLimitError(
                        limit=info['limit'],
                        window=info['window'],
                        reset_time=info['reset_time']
                    )
                
                # Response'a header'ları ekle
                response = func(request, *args, **kwargs)
                
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
                    response.headers['X-RateLimit-Window'] = str(info['window'])
                
                return response
            return wrapper
        return decorator


class TokenValidator:
    """JWT token doğrulama"""
    
    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        """JWT token'ı doğrula"""
        try:
            # Token'ı decode et
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Expiration kontrolü
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if datetime.utcnow().timestamp() > exp_timestamp:
                    raise AuthenticationException("Token süresi dolmuş")
            
            # User ID kontrolü
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationException("Geçersiz token yapısı")
            
            # Kullanıcı var mı?
            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    raise AuthenticationException("Kullanıcı aktif değil")
            except User.DoesNotExist:
                raise AuthenticationException("Kullanıcı bulunamadı")
            
            return {
                'valid': True,
                'user_id': user_id,
                'user': user,
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Token süresi dolmuş")
        except jwt.InvalidTokenError:
            raise AuthenticationException("Geçersiz token")
        except Exception as e:
            logger.error(f"Token doğrulama hatası: {e}")
            raise AuthenticationException("Token doğrulama başarısız")
    
    @staticmethod
    def extract_token_from_request(request: Request) -> Optional[str]:
        """Request'ten token çıkar"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Query parameter'dan da kontrol et
        return request.GET.get('token') or request.POST.get('token')


class PermissionChecker:
    """İzin kontrolü"""
    
    # SAP modül izinleri
    SAP_MODULE_PERMISSIONS = {
        'FI': ['view_financial', 'edit_financial'],
        'MM': ['view_material', 'edit_material'],
        'SD': ['view_sales', 'edit_sales'],
        'CRM': ['view_crm', 'edit_crm'],
        'HR': ['view_hr', 'edit_hr'],
        'ADMIN': ['system_admin']
    }
    
    @staticmethod
    def has_sap_module_access(user: User, sap_module: str) -> bool: # type: ignore
        """SAP modül erişimi kontrolü"""
        if not user or not user.is_active:
            return False
        
        # Süper kullanıcılar her şeye erişebilir
        if user.is_superuser:
            return True
        
        # User profile'dan SAP modüllerini kontrol et
        try:
            user_profile = user.sapbot_profile
            allowed_modules = user_profile.sap_modules or []
            return sap_module in allowed_modules
        except AttributeError:
            return False
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool: # type: ignore
        """Genel izin kontrolü"""
        if not user or not user.is_active:
            return False
        
        if user.is_superuser:
            return True
        
        return user.has_perm(permission)
    
    @staticmethod
    def check_user_type_permission(user: User, required_type: str) -> bool: # type: ignore
        """Kullanıcı tipi izni kontrolü"""
        if not user or not user.is_active:
            return False
        
        try:
            user_profile = user.sapbot_profile
            user_type = user_profile.user_type
            
            # Hiyerarşi: super_admin > admin > technical > user
            type_hierarchy = {
                'super_admin': 4,
                'admin': 3,
                'technical': 2,
                'user': 1
            }
            
            user_level = type_hierarchy.get(user_type, 0)
            required_level = type_hierarchy.get(required_type, 0)
            
            return user_level >= required_level
            
        except AttributeError:
            return False


class SecurityAuditor:
    """Güvenlik audit log'ları"""
    
    @staticmethod
    def log_security_event(
        event_type: str,
        user: Optional[User] = None, # type: ignore
        request: Optional[Request] = None,
        details: Optional[Dict] = None,
        severity: str = "INFO"
    ):
        """Güvenlik olayını logla"""
        log_data = {
            'event_type': event_type,
            'timestamp': timezone.now().isoformat(),
            'severity': severity,
            'details': details or {}
        }
        
        if user:
            log_data['user_id'] = str(user.id)
            log_data['user_email'] = user.email
        
        if request:
            log_data['ip_address'] = get_client_ip(request)
            log_data['user_agent'] = get_user_agent(request)
            log_data['path'] = request.path
            log_data['method'] = request.method
        
        # Log level'ını belirle
        log_level = {
            'DEBUG': logger.debug,
            'INFO': logger.info,
            'WARNING': logger.warning,
            'ERROR': logger.error,
            'CRITICAL': logger.critical
        }.get(severity, logger.info)
        
        log_level(f"Security Event: {event_type}", extra=log_data)
        
        # Kritik olayları ayrıca kaydet
        if severity in ['ERROR', 'CRITICAL']:
            cache.set(
                f"security_alert:{timezone.now().timestamp()}",
                log_data,
                86400  # 24 saat
            )
    
    @staticmethod
    def log_failed_login(email: str, ip_address: str, reason: str):
        """Başarısız giriş denemesini logla"""
        SecurityAuditor.log_security_event(
            event_type="FAILED_LOGIN",
            details={
                'email': email,
                'ip_address': ip_address,
                'reason': reason
            },
            severity="WARNING"
        )
    
    @staticmethod
    def log_suspicious_activity(
        user: User, # type: ignore
        request: Request,
        activity: str,
        details: Dict
    ):
        """Şüpheli aktiviteyi logla"""
        SecurityAuditor.log_security_event(
            event_type="SUSPICIOUS_ACTIVITY",
            user=user,
            request=request,
            details={
                'activity': activity,
                **details
            },
            severity="ERROR"
        )


class IPWhitelist:
    """IP whitelist kontrolü"""
    
    @staticmethod
    def is_ip_allowed(ip_address: str, whitelist: List[str] = None) -> bool:
        """IP adresinin izin listesinde olup olmadığını kontrol et"""
        if not whitelist:
            whitelist = getattr(settings, 'ALLOWED_IPS', [])
        
        if not whitelist:
            return True  # Whitelist yoksa herkese izin ver
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for allowed in whitelist:
                if '/' in allowed:
                    # CIDR notation
                    if ip in ipaddress.ip_network(allowed, strict=False):
                        return True
                else:
                    # Tek IP
                    if ip == ipaddress.ip_address(allowed):
                        return True
            
            return False
            
        except ValueError:
            logger.error(f"Geçersiz IP adresi: {ip_address}")
            return False


class PasswordValidator:
    """Şifre güvenlik kontrolü"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Şifre güçlülüğünü kontrol et"""
        result = {
            'valid': True,
            'score': 0,
            'feedback': [],
            'requirements': {
                'min_length': False,
                'has_uppercase': False,
                'has_lowercase': False,
                'has_digit': False,
                'has_special': False,
                'no_common': False
            }
        }
        
        # Uzunluk kontrolü
        if len(password) >= 8:
            result['requirements']['min_length'] = True
            result['score'] += 1
        else:
            result['feedback'].append("En az 8 karakter olmalı")
        
        # Büyük harf kontrolü
        if re.search(r'[A-Z]', password):
            result['requirements']['has_uppercase'] = True
            result['score'] += 1
        else:
            result['feedback'].append("En az bir büyük harf içermeli")
        
        # Küçük harf kontrolü
        if re.search(r'[a-z]', password):
            result['requirements']['has_lowercase'] = True
            result['score'] += 1
        else:
            result['feedback'].append("En az bir küçük harf içermeli")
        
        # Rakam kontrolü
        if re.search(r'[0-9]', password):
            result['requirements']['has_digit'] = True
            result['score'] += 1
        else:
            result['feedback'].append("En az bir rakam içermeli")
        
        # Özel karakter kontrolü
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>?]', password):
            result['requirements']['has_special'] = True
            result['score'] += 1
        else:
            result['feedback'].append("En az bir özel karakter içermeli")
        
        # Yaygın şifre kontrolü
        common_passwords = [
            '123456', 'password', '123456789', '12345678',
            'qwerty', '123123', '1234567', 'password1',
            '12345', '1234567890', '123abc', 'password123'
        ]
        
        if password.lower() not in [p.lower() for p in common_passwords]:
            result['requirements']['no_common'] = True
            result['score'] += 1
        else:
            result['feedback'].append("Yaygın kullanılan şifrelerden kaçının")
        
        # Genel değerlendirme
        if result['score'] < 4:
            result['valid'] = False
        
        return result


class CSRFProtection:
    """CSRF koruması"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """CSRF token oluştur"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(request: Request, token: str) -> bool:
        """CSRF token'ını doğrula"""
        session_token = request.session.get('csrf_token')
        return session_token and hmac.compare_digest(session_token, token)


# Security middleware functions
def require_permission(permission: str):
    """İzin gerektiren decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                raise AuthenticationException("Kimlik doğrulama gerekli")
            
            if not PermissionChecker.has_permission(request.user, permission):
                raise AuthorizationException(
                    f"Bu işlem için '{permission}' iznine ihtiyacınız var",
                    required_permission=permission
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_sap_module_access(sap_module: str):
    """SAP modül erişimi gerektiren decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                raise AuthenticationException("Kimlik doğrulama gerekli")
            
            if not PermissionChecker.has_sap_module_access(request.user, sap_module):
                raise AuthorizationException(
                    f"SAP {sap_module} modülüne erişim yetkiniz yok",
                    required_permission=f"sap_module_{sap_module}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_user_type(user_type: str):
    """Kullanıcı tipi gerektiren decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                raise AuthenticationException("Kimlik doğrulama gerekli")
            
            if not PermissionChecker.check_user_type_permission(request.user, user_type):
                raise AuthorizationException(
                    f"Bu işlem için '{user_type}' seviyesinde yetki gerekli",
                    required_permission=f"user_type_{user_type}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


# Utility functions
def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """Şifreyi hash'le"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Şifreyi doğrula"""
    test_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(hashed, test_hash)


def generate_secure_filename(original_filename: str) -> str:
    """Güvenli dosya adı oluştur"""
    # Güvenli karakterleri al
    safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '', original_filename)
    
    # Uzunluk sınırı
    if len(safe_chars) > 100:
        name, ext = safe_chars.rsplit('.', 1) if '.' in safe_chars else (safe_chars, '')
        safe_chars = name[:95] + (f".{ext}" if ext else "")
    
    # Boşsa varsayılan ad ver
    if not safe_chars:
        safe_chars = f"file_{secrets.token_hex(8)}"
    
    return safe_chars