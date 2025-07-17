# backend/sapbot_api/utils/validators.py
"""
SAPBot API Validators

Bu modül veri doğrulama fonksiyonlarını içerir:
- Chat message validation
- Document upload validation
- Search query validation
- User input validation
- Business logic validation
"""
import os
import re
import uuid
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
import magic
import logging

from django.core.validators import validate_email, URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile

from .exceptions import (
    ValidationException,
    FileUploadError,
    SAPModuleError,
    IntentDetectionError
)
from .security import InputSanitizer
from .text_processing import LanguageDetector, SAPTerminologyAnalyzer

logger = logging.getLogger(__name__)


class BaseValidator:
    """Temel validator sınıfı"""
    
    def __init__(self, error_message: str = "Doğrulama hatası"):
        self.error_message = error_message
    
    def validate(self, value: Any) -> Any:
        """Doğrulama fonksiyonu - alt sınıflarda override edilecek"""
        raise NotImplementedError
    
    def raise_error(self, message: str = None, field: str = None, value: Any = None):
        """Validation error fırlat"""
        raise ValidationException(
            message=message or self.error_message,
            field=field,
            value=value
        )


class ChatMessageValidator(BaseValidator):
    """Chat mesajı doğrulama"""
    
    MIN_LENGTH = 1
    MAX_LENGTH = 2000
    
    FORBIDDEN_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript\s*:',
        r'on\w+\s*=',
        r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)',
        r'(\||&&|;|\$\(|\`)',
        r'(\.\./|\.\.\\)',
    ]
    
    def validate_message_content(self, message: str) -> str:
        """Mesaj içeriğini doğrula ve temizle"""
        if not message:
            self.raise_error("Mesaj içeriği boş olamaz", "message", message)
        
        if not isinstance(message, str):
            self.raise_error("Mesaj string tipinde olmalıdır", "message", type(message))
        
        # Uzunluk kontrolü
        if len(message) < self.MIN_LENGTH:
            self.raise_error(
                f"Mesaj en az {self.MIN_LENGTH} karakter olmalıdır",
                "message_length",
                len(message)
            )
        
        if len(message) > self.MAX_LENGTH:
            self.raise_error(
                f"Mesaj en fazla {self.MAX_LENGTH} karakter olabilir",
                "message_length",
                len(message)
            )
        
        # Güvenlik kontrolü
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                self.raise_error(
                    "Mesaj güvenlik kontrolünden geçemedi",
                    "security_check"
                )
        
        # Mesajı temizle
        try:
            cleaned_message = InputSanitizer.sanitize_chat_message(message)
            return cleaned_message
        except Exception as e:
            self.raise_error(f"Mesaj temizleme hatası: {str(e)}", "sanitization")
    
    def validate_session_id(self, session_id: str) -> str:
        """Session ID doğrula"""
        if not session_id:
            self.raise_error("Session ID gerekli", "session_id")
        
        if not isinstance(session_id, str):
            self.raise_error("Session ID string tipinde olmalıdır", "session_id")
        
        if len(session_id) < 10 or len(session_id) > 100:
            self.raise_error("Session ID uzunluğu 10-100 karakter arasında olmalıdır", "session_id")
        
        # Session ID formatı kontrolü
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            self.raise_error("Session ID geçersiz karakter içeriyor", "session_id")
        
        return session_id
    
    def validate_user_type(self, user_type: str) -> str:
        """Kullanıcı tipi doğrula"""
        valid_types = ['user', 'technical', 'admin', 'super_admin']
        
        if not user_type:
            return 'user'  # Varsayılan
        
        if user_type not in valid_types:
            self.raise_error(
                f"Geçersiz kullanıcı tipi. Geçerli değerler: {', '.join(valid_types)}",
                "user_type",
                user_type
            )
        
        return user_type
    
    def validate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Context bilgisini doğrula"""
        if context is None:
            return {}
        
        if not isinstance(context, dict):
            self.raise_error("Context dictionary tipinde olmalıdır", "context")
        
        # Allowed context keys
        allowed_keys = [
            'sap_module', 'language', 'intent', 'technical_level',
            'previous_messages', 'user_preferences'
        ]
        
        validated_context = {}
        
        for key, value in context.items():
            if key not in allowed_keys:
                logger.warning(f"Bilinmeyen context key: {key}")
                continue
            
            if key == 'sap_module':
                validated_context[key] = self.validate_sap_module(value)
            elif key == 'language':
                validated_context[key] = self.validate_language(value)
            elif key == 'technical_level':
                validated_context[key] = self.validate_technical_level(value)
            else:
                validated_context[key] = value
        
        return validated_context
    
    def validate_sap_module(self, sap_module: str) -> Optional[str]:
        """SAP modül doğrula"""
        if not sap_module:
            return None
        
        valid_modules = [
            'FI', 'MM', 'SD', 'CRM', 'PROD', 'HR', 'QM', 'PM', 
            'CO', 'WM', 'BI', 'ADMIN', 'OTHER'
        ]
        
        sap_module = sap_module.upper()
        
        if sap_module not in valid_modules:
            self.raise_error(
                f"Geçersiz SAP modülü. Geçerli değerler: {', '.join(valid_modules)}",
                "sap_module",
                sap_module
            )
        
        return sap_module
    
    def validate_language(self, language: str) -> str:
        """Dil doğrula"""
        valid_languages = ['tr', 'en', 'mixed']
        
        if not language:
            return 'tr'  # Varsayılan
        
        if language not in valid_languages:
            self.raise_error(
                f"Geçersiz dil. Geçerli değerler: {', '.join(valid_languages)}",
                "language",
                language
            )
        
        return language
    
    def validate_technical_level(self, technical_level: str) -> str:
        """Teknik seviye doğrula"""
        valid_levels = ['user', 'admin', 'developer', 'mixed']
        
        if not technical_level:
            return 'user'  # Varsayılan
        
        if technical_level not in valid_levels:
            self.raise_error(
                f"Geçersiz teknik seviye. Geçerli değerler: {', '.join(valid_levels)}",
                "technical_level",
                technical_level
            )
        
        return technical_level


class DocumentUploadValidator(BaseValidator):
    """Döküman upload doğrulama"""
    
    ALLOWED_EXTENSIONS = {
        'pdf': ['.pdf'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'document': ['.doc', '.docx', '.txt', '.rtf']
    }
    
    ALLOWED_MIMETYPES = {
        'pdf': ['application/pdf'],
        'video': [
            'video/mp4', 'video/avi', 'video/quicktime', 
            'video/x-msvideo', 'video/webm', 'video/x-matroska'
        ],
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 
            'image/bmp', 'image/tiff'
        ],
        'document': [
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/rtf'
        ]
    }
    
    MAX_FILE_SIZES = {
        'pdf': 100 * 1024 * 1024,      # 100MB
        'video': 500 * 1024 * 1024,    # 500MB
        'image': 10 * 1024 * 1024,     # 10MB
        'document': 50 * 1024 * 1024   # 50MB
    }
    
    def validate_file(self, file: UploadedFile) -> Dict[str, Any]:
        """Dosya doğrulama"""
        if not file:
            self.raise_error("Dosya gerekli", "file")
        
        # Dosya adı kontrolü
        if not file.name:
            self.raise_error("Dosya adı gerekli", "filename")
        
        filename = InputSanitizer.sanitize_filename(file.name)
        
        # Dosya boyutu kontrolü
        if file.size == 0:
            self.raise_error("Dosya boş olamaz", "file_size", 0)
        
        # Dosya uzantısı kontrolü
        file_extension = self._get_file_extension(filename)
        file_type = self._determine_file_type(file_extension)
        
        # Boyut kontrolü
        max_size = self.MAX_FILE_SIZES.get(file_type, 50 * 1024 * 1024)
        if file.size > max_size:
            raise FileUploadError(
                message=f"Dosya boyutu çok büyük. Maksimum: {max_size // (1024*1024)}MB",
                file_name=filename,
                file_size=file.size,
                max_size=max_size
            )
        
        # MIME type kontrolü
        try:
            file.seek(0)
            mime_type = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
        except Exception:
            mime_type = file.content_type
        
        allowed_mimes = self.ALLOWED_MIMETYPES.get(file_type, [])
        if mime_type not in allowed_mimes:
            self.raise_error(
                f"Desteklenmeyen dosya tipi: {mime_type}",
                "mime_type",
                mime_type
            )
        
        return {
            'filename': filename,
            'file_type': file_type,
            'file_size': file.size,
            'mime_type': mime_type,
            'extension': file_extension
        }
    
    def validate_title(self, title: str) -> str:
        """Döküman başlığı doğrula"""
        if not title:
            self.raise_error("Döküman başlığı gerekli", "title")
        
        if len(title) < 3:
            self.raise_error("Başlık en az 3 karakter olmalıdır", "title")
        
        if len(title) > 255:
            self.raise_error("Başlık en fazla 255 karakter olabilir", "title")
        
        # Başlığı temizle
        return InputSanitizer.sanitize_string(title, max_length=255)
    
    def validate_description(self, description: str) -> Optional[str]:
        """Açıklama doğrula"""
        if not description:
            return None
        
        if len(description) > 1000:
            self.raise_error("Açıklama en fazla 1000 karakter olabilir", "description")
        
        return InputSanitizer.sanitize_string(description, max_length=1000)
    
    def validate_tags(self, tags: List[str]) -> List[str]:
        """Etiketleri doğrula"""
        if not tags:
            return []
        
        if not isinstance(tags, list):
            self.raise_error("Etiketler liste formatında olmalıdır", "tags")
        
        if len(tags) > 10:
            self.raise_error("En fazla 10 etiket eklenebilir", "tags")
        
        validated_tags = []
        for tag in tags:
            if not isinstance(tag, str):
                continue
            
            tag = tag.strip()
            if len(tag) < 2:
                continue
            
            if len(tag) > 50:
                tag = tag[:50]
            
            # Etiket temizle
            clean_tag = re.sub(r'[^a-zA-ZçğıöşüÇĞIİÖŞÜ0-9_-]', '', tag)
            if clean_tag:
                validated_tags.append(clean_tag)
        
        return validated_tags[:10]  # Maksimum 10 etiket
    
    def _get_file_extension(self, filename: str) -> str:
        """Dosya uzantısını al"""
        return os.path.splitext(filename.lower())[1]
    
    def _determine_file_type(self, extension: str) -> str:
        """Dosya tipini belirle"""
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return file_type
        
        self.raise_error(
            f"Desteklenmeyen dosya uzantısı: {extension}",
            "file_extension",
            extension
        )


class SearchQueryValidator(BaseValidator):
    """Arama sorgusu doğrulama"""
    
    MIN_QUERY_LENGTH = 2
    MAX_QUERY_LENGTH = 500
    
    def validate_search_query(self, query: str) -> str:
        """Arama sorgusunu doğrula"""
        if not query:
            self.raise_error("Arama sorgusu gerekli", "query")
        
        if not isinstance(query, str):
            self.raise_error("Arama sorgusu string tipinde olmalıdır", "query")
        
        # Uzunluk kontrolü
        if len(query.strip()) < self.MIN_QUERY_LENGTH:
            self.raise_error(
                f"Arama sorgusu en az {self.MIN_QUERY_LENGTH} karakter olmalıdır",
                "query_length",
                len(query)
            )
        
        if len(query) > self.MAX_QUERY_LENGTH:
            self.raise_error(
                f"Arama sorgusu en fazla {self.MAX_QUERY_LENGTH} karakter olabilir",
                "query_length",
                len(query)
            )
        
        # Güvenlik kontrolü
        if re.search(r'[\<\>\"\'%;()&+]', query):
            self.raise_error("Arama sorgusunda geçersiz karakter", "query_security")
        
        # SQL injection kontrolü
        dangerous_patterns = [
            r'\bUNION\b', r'\bSELECT\b', r'\bINSERT\b', r'\bUPDATE\b',
            r'\bDELETE\b', r'\bDROP\b', r'--', r'/\*', r'\*/'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                self.raise_error("Arama sorgusunda güvenlik riski", "query_security")
        
        return query.strip()
    
    def validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Arama filtrelerini doğrula"""
        if not filters:
            return {}
        
        if not isinstance(filters, dict):
            self.raise_error("Filtreler dictionary tipinde olmalıdır", "filters")
        
        validated_filters = {}
        
        # SAP modül filtresi
        if 'sap_module' in filters:
            sap_module = filters['sap_module']
            if sap_module:
                chat_validator = ChatMessageValidator()
                validated_filters['sap_module'] = chat_validator.validate_sap_module(sap_module)
        
        # Teknik seviye filtresi
        if 'technical_level' in filters:
            tech_level = filters['technical_level']
            if tech_level:
                chat_validator = ChatMessageValidator()
                validated_filters['technical_level'] = chat_validator.validate_technical_level(tech_level)
        
        # Dil filtresi
        if 'language' in filters:
            language = filters['language']
            if language:
                chat_validator = ChatMessageValidator()
                validated_filters['language'] = chat_validator.validate_language(language)
        
        # Minimum relevans skoru
        if 'min_relevance' in filters:
            min_relevance = filters['min_relevance']
            if min_relevance is not None:
                try:
                    min_relevance = float(min_relevance)
                    if 0.0 <= min_relevance <= 1.0:
                        validated_filters['min_relevance'] = min_relevance
                    else:
                        self.raise_error("Minimum relevans 0.0-1.0 arasında olmalıdır", "min_relevance")
                except (ValueError, TypeError):
                    self.raise_error("Minimum relevans sayı tipinde olmalıdır", "min_relevance")
        
        # Limit
        if 'limit' in filters:
            limit = filters['limit']
            if limit is not None:
                try:
                    limit = int(limit)
                    if 1 <= limit <= 50:
                        validated_filters['limit'] = limit
                    else:
                        self.raise_error("Limit 1-50 arasında olmalıdır", "limit")
                except (ValueError, TypeError):
                    self.raise_error("Limit integer tipinde olmalıdır", "limit")
        
        return validated_filters


class UserInputValidator(BaseValidator):
    """Kullanıcı girişi doğrulama"""
    
    def validate_email(self, email: str) -> str:
        """Email doğrula"""
        if not email:
            self.raise_error("Email adresi gerekli", "email")
        
        email = email.strip().lower()
        
        try:
            validate_email(email)
        except ValidationError:
            self.raise_error("Geçersiz email formatı", "email", email)
        
        return email
    
    def validate_password(self, password: str) -> str:
        """Şifre doğrula"""
        if not password:
            self.raise_error("Şifre gerekli", "password")
        
        if len(password) < 8:
            self.raise_error("Şifre en az 8 karakter olmalıdır", "password")
        
        if len(password) > 128:
            self.raise_error("Şifre en fazla 128 karakter olabilir", "password")
        
        # Karmaşıklık kontrolü
        if not re.search(r'[A-Z]', password):
            self.raise_error("Şifre en az bir büyük harf içermelidir", "password")
        
        if not re.search(r'[a-z]', password):
            self.raise_error("Şifre en az bir küçük harf içermelidir", "password")
        
        if not re.search(r'[0-9]', password):
            self.raise_error("Şifre en az bir rakam içermelidir", "password")
        
        return password
    
    def validate_phone(self, phone: str) -> Optional[str]:
        """Telefon numarası doğrula"""
        if not phone:
            return None
        
        # Türkiye telefon formatı
        phone = re.sub(r'[^\d]', '', phone)  # Sadece rakamlar
        
        if len(phone) == 11 and phone.startswith('0'):
            phone = '90' + phone[1:]  # 0 yerine 90 ekle
        
        if len(phone) == 10:
            phone = '90' + phone  # Başına 90 ekle
        
        if not (len(phone) == 12 and phone.startswith('90')):
            self.raise_error("Geçersiz telefon numarası formatı", "phone", phone)
        
        return phone
    
    def validate_url(self, url: str) -> Optional[str]:
        """URL doğrula"""
        if not url:
            return None
        
        url = url.strip()
        
        # Protokol yoksa ekle
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            self.raise_error("Geçersiz URL formatı", "url", url)
        
        return url
    
    def validate_uuid(self, uuid_str: str) -> str:
        """UUID doğrula"""
        if not uuid_str:
            self.raise_error("UUID gerekli", "uuid")
        
        try:
            uuid.UUID(uuid_str)
        except ValueError:
            self.raise_error("Geçersiz UUID formatı", "uuid", uuid_str)
        
        return uuid_str
    
    def validate_json(self, json_str: str) -> Dict[str, Any]:
        """JSON doğrula"""
        if not json_str:
            return {}
        
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                self.raise_error("JSON dictionary formatında olmalıdır", "json")
            return data
        except json.JSONDecodeError as e:
            self.raise_error(f"Geçersiz JSON formatı: {str(e)}", "json")
    
    def validate_decimal(self, value: str, max_digits: int = 10, decimal_places: int = 2) -> Decimal:
        """Decimal doğrula"""
        if not value:
            self.raise_error("Değer gerekli", "decimal")
        
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            self.raise_error("Geçersiz sayı formatı", "decimal", value)
        
        # Toplam digit kontrolü
        sign, digits, exponent = decimal_value.as_tuple()
        if len(digits) > max_digits:
            self.raise_error(f"Sayı en fazla {max_digits} basamak olabilir", "decimal")
        
        # Ondalık basamak kontrolü
        if exponent < -decimal_places:
            self.raise_error(f"En fazla {decimal_places} ondalık basamak olabilir", "decimal")
        
        return decimal_value
    
    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[datetime, datetime]:
        """Tarih aralığı doğrula"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            self.raise_error("Geçersiz tarih formatı (ISO format bekleniyor)", "date_format")
        
        if start >= end:
            self.raise_error("Başlangıç tarihi bitiş tarihinden önce olmalıdır", "date_range")
        
        # Maksimum aralık kontrolü (1 yıl)
        if (end - start).days > 365:
            self.raise_error("Tarih aralığı en fazla 1 yıl olabilir", "date_range")
        
        return start, end


class BusinessLogicValidator(BaseValidator):
    """İş mantığı doğrulama"""
    
    def validate_sap_transaction_code(self, tcode: str) -> str:
        """SAP transaction code doğrula"""
        if not tcode:
            self.raise_error("Transaction code gerekli", "tcode")
        
        tcode = tcode.upper().strip()
        
        # SAP tcode formatı: 2-8 karakter, harfle başlamalı
        if not re.match(r'^[A-Z][A-Z0-9]{1,7}$', tcode):
            self.raise_error("Geçersiz SAP transaction code formatı", "tcode", tcode)
        
        return tcode
    
    def validate_document_number(self, doc_number: str) -> str:
        """SAP döküman numarası doğrula"""
        if not doc_number:
            self.raise_error("Döküman numarası gerekli", "document_number")
        
        doc_number = doc_number.strip()
        
        # SAP döküman numarası: 8-10 rakam
        if not re.match(r'^\d{8,10}$', doc_number):
            self.raise_error("Geçersiz döküman numarası formatı", "document_number", doc_number)
        
        return doc_number
    
    def validate_company_code(self, company_code: str) -> str:
        """Şirket kodu doğrula"""
        if not company_code:
            self.raise_error("Şirket kodu gerekli", "company_code")
        
        company_code = company_code.upper().strip()
        
        # SAP şirket kodu: 1-4 karakter
        if not re.match(r'^[A-Z0-9]{1,4}$', company_code):
            self.raise_error("Geçersiz şirket kodu formatı", "company_code", company_code)
        
        return company_code
    
    def validate_currency_code(self, currency: str) -> str:
        """Para birimi kodu doğrula"""
        if not currency:
            return 'TRY'  # Varsayılan
        
        currency = currency.upper().strip()
        
        # ISO 4217 para birimi kodları
        valid_currencies = ['TRY', 'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
        
        if currency not in valid_currencies:
            self.raise_error(
                f"Geçersiz para birimi. Geçerli değerler: {', '.join(valid_currencies)}",
                "currency",
                currency
            )
        
        return currency
    
    def validate_amount(self, amount: Union[str, int, float], currency: str = 'TRY') -> Decimal:
        """Tutar doğrula"""
        if amount is None:
            self.raise_error("Tutar gerekli", "amount")
        
        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            self.raise_error("Geçersiz tutar formatı", "amount", amount)
        
        if decimal_amount < 0:
            self.raise_error("Tutar negatif olamaz", "amount", decimal_amount)
        
        # Para birimine göre maksimum tutar kontrolü
        max_amounts = {
            'TRY': Decimal('999999999.99'),
            'USD': Decimal('99999999.99'),
            'EUR': Decimal('99999999.99')
        }
        
        max_amount = max_amounts.get(currency, Decimal('999999999.99'))
        if decimal_amount > max_amount:
            self.raise_error(f"Tutar çok büyük (max: {max_amount} {currency})", "amount")
        
        return decimal_amount.quantize(Decimal('0.01'))  # 2 ondalık basamağa yuvarla


# Utility functions
def validate_chat_message(message: str, session_id: str, user_type: str = 'user', context: Dict = None) -> Dict[str, Any]:
    """Chat mesajı doğrulama"""
    validator = ChatMessageValidator()
    
    return {
        'message': validator.validate_message_content(message),
        'session_id': validator.validate_session_id(session_id),
        'user_type': validator.validate_user_type(user_type),
        'context': validator.validate_context(context or {})
    }


def validate_document_upload(file: UploadedFile, title: str, description: str = None, tags: List[str] = None) -> Dict[str, Any]:
    """Döküman upload doğrulama"""
    validator = DocumentUploadValidator()
    
    file_info = validator.validate_file(file)
    
    return {
        'file_info': file_info,
        'title': validator.validate_title(title),
        'description': validator.validate_description(description),
        'tags': validator.validate_tags(tags or [])
    }


def validate_search_query(query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Arama sorgusu doğrulama"""
    validator = SearchQueryValidator()
    
    return {
        'query': validator.validate_search_query(query),
        'filters': validator.validate_filters(filters or {})
    }


def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Kullanıcı girişi doğrulama"""
    validator = UserInputValidator()
    validated = {}
    
    if 'email' in data:
        validated['email'] = validator.validate_email(data['email'])
    
    if 'password' in data:
        validated['password'] = validator.validate_password(data['password'])
    
    if 'phone' in data:
        validated['phone'] = validator.validate_phone(data['phone'])
    
    if 'url' in data:
        validated['url'] = validator.validate_url(data['url'])
    
    if 'uuid' in data:
        validated['uuid'] = validator.validate_uuid(data['uuid'])
    
    return validated


def validate_sap_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """SAP verileri doğrulama"""
    validator = BusinessLogicValidator()
    validated = {}
    
    if 'transaction_code' in data:
        validated['transaction_code'] = validator.validate_sap_transaction_code(data['transaction_code'])
    
    if 'document_number' in data:
        validated['document_number'] = validator.validate_document_number(data['document_number'])
    
    if 'company_code' in data:
        validated['company_code'] = validator.validate_company_code(data['company_code'])
    
    if 'currency' in data:
        validated['currency'] = validator.validate_currency_code(data['currency'])
    
    if 'amount' in data:
        currency = data.get('currency', 'TRY')
        validated['amount'] = validator.validate_amount(data['amount'], currency)
    
    return validated


class RateLimitValidator(BaseValidator):
    """Rate limit doğrulama"""
    
    def validate_rate_limit_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Rate limit konfigürasyonu doğrula"""
        if not isinstance(config, dict):
            self.raise_error("Rate limit config dictionary olmalıdır", "config")
        
        validated = {}
        
        # Limit sayısı
        if 'limit' in config:
            try:
                limit = int(config['limit'])
                if limit <= 0 or limit > 10000:
                    self.raise_error("Limit 1-10000 arasında olmalıdır", "limit")
                validated['limit'] = limit
            except (ValueError, TypeError):
                self.raise_error("Limit integer olmalıdır", "limit")
        
        # Zaman penceresi (saniye)
        if 'window' in config:
            try:
                window = int(config['window'])
                if window <= 0 or window > 86400:  # Max 1 gün
                    self.raise_error("Window 1-86400 saniye arasında olmalıdır", "window")
                validated['window'] = window
            except (ValueError, TypeError):
                self.raise_error("Window integer olmalıdır", "window")
        
        return validated


class AnalyticsValidator(BaseValidator):
    """Analytics veri doğrulama"""
    
    def validate_analytics_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Analytics sorgusu doğrula"""
        if not isinstance(query, dict):
            self.raise_error("Analytics query dictionary olmalıdır", "query")
        
        validated = {}
        
        # Zaman aralığı
        if 'start_date' in query and 'end_date' in query:
            user_validator = UserInputValidator()
            start, end = user_validator.validate_date_range(
                query['start_date'], 
                query['end_date']
            )
            validated['start_date'] = start
            validated['end_date'] = end
        
        # Metrik tipi
        if 'metric_type' in query:
            valid_metrics = [
                'queries', 'users', 'sessions', 'response_time',
                'success_rate', 'sap_modules', 'intents'
            ]
            metric_type = query['metric_type']
            if metric_type not in valid_metrics:
                self.raise_error(
                    f"Geçersiz metrik tipi. Geçerli değerler: {', '.join(valid_metrics)}",
                    "metric_type"
                )
            validated['metric_type'] = metric_type
        
        # Gruplama
        if 'group_by' in query:
            valid_groups = ['day', 'week', 'month', 'hour', 'user_type', 'sap_module']
            group_by = query['group_by']
            if group_by not in valid_groups:
                self.raise_error(
                    f"Geçersiz gruplama. Geçerli değerler: {', '.join(valid_groups)}",
                    "group_by"
                )
            validated['group_by'] = group_by
        
        # Filtreler
        if 'filters' in query:
            search_validator = SearchQueryValidator()
            validated['filters'] = search_validator.validate_filters(query['filters'])
        
        return validated


class FeedbackValidator(BaseValidator):
    """Geri bildirim doğrulama"""
    
    def validate_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Geri bildirim doğrula"""
        if not isinstance(feedback, dict):
            self.raise_error("Feedback dictionary olmalıdır", "feedback")
        
        validated = {}
        
        # Message ID
        if 'message_id' in feedback:
            user_validator = UserInputValidator()
            validated['message_id'] = user_validator.validate_uuid(feedback['message_id'])
        
        # Rating
        if 'rating' in feedback:
            try:
                rating = int(feedback['rating'])
                if rating < 1 or rating > 5:
                    self.raise_error("Rating 1-5 arasında olmalıdır", "rating")
                validated['rating'] = rating
            except (ValueError, TypeError):
                self.raise_error("Rating integer olmalıdır", "rating")
        
        # Comment
        if 'comment' in feedback:
            comment = feedback['comment']
            if comment:
                if len(comment) > 1000:
                    self.raise_error("Yorum en fazla 1000 karakter olabilir", "comment")
                validated['comment'] = InputSanitizer.sanitize_string(comment, max_length=1000)
        
        # Is helpful
        if 'is_helpful' in feedback:
            validated['is_helpful'] = bool(feedback['is_helpful'])
        
        return validated


class ConfigurationValidator(BaseValidator):
    """Sistem konfigürasyon doğrulama"""
    
    VALID_CONFIG_TYPES = ['string', 'integer', 'float', 'boolean', 'json', 'list']
    
    def validate_system_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sistem konfigürasyonu doğrula"""
        if not isinstance(config, dict):
            self.raise_error("Config dictionary olmalıdır", "config")
        
        validated = {}
        
        # Key
        if 'key' in config:
            key = config['key']
            if not re.match(r'^[a-z_][a-z0-9_]*', key):
                self.raise_error("Config key sadece küçük harf, rakam ve underscore içerebilir", "key")
            if len(key) > 100:
                self.raise_error("Config key en fazla 100 karakter olabilir", "key")
            validated['key'] = key
        
        # Value
        if 'value' in config:
            validated['value'] = str(config['value'])
        
        # Config type
        if 'config_type' in config:
            config_type = config['config_type']
            if config_type not in self.VALID_CONFIG_TYPES:
                self.raise_error(
                    f"Geçersiz config tipi. Geçerli değerler: {', '.join(self.VALID_CONFIG_TYPES)}",
                    "config_type"
                )
            validated['config_type'] = config_type
        
        # Description
        if 'description' in config:
            description = config['description']
            if description and len(description) > 500:
                self.raise_error("Açıklama en fazla 500 karakter olabilir", "description")
            validated['description'] = description
        
        return validated


class BulkOperationValidator(BaseValidator):
    """Toplu işlem doğrulama"""
    
    def validate_bulk_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Toplu işlem doğrula"""
        if not isinstance(operation, dict):
            self.raise_error("Bulk operation dictionary olmalıdır", "operation")
        
        validated = {}
        
        # Operation type
        if 'operation_type' in operation:
            valid_operations = [
                'bulk_upload', 'bulk_delete', 'bulk_update', 
                'bulk_reprocess', 'bulk_export'
            ]
            op_type = operation['operation_type']
            if op_type not in valid_operations:
                self.raise_error(
                    f"Geçersiz işlem tipi. Geçerli değerler: {', '.join(valid_operations)}",
                    "operation_type"
                )
            validated['operation_type'] = op_type
        
        # Items
        if 'items' in operation:
            items = operation['items']
            if not isinstance(items, list):
                self.raise_error("Items liste olmalıdır", "items")
            
            if len(items) == 0:
                self.raise_error("En az bir item gerekli", "items")
            
            if len(items) > 100:
                self.raise_error("En fazla 100 item işlenebilir", "items")
            
            validated['items'] = items
        
        # Options
        if 'options' in operation:
            options = operation['options']
            if not isinstance(options, dict):
                self.raise_error("Options dictionary olmalıdır", "options")
            validated['options'] = options
        
        return validated


# Composite validators
def validate_complete_chat_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tam chat isteği doğrulama"""
    required_fields = ['message', 'session_id']
    
    for field in required_fields:
        if field not in data:
            raise ValidationException(f"Gerekli alan eksik: {field}", field=field)
    
    # Ana doğrulama
    validated = validate_chat_message(
        data['message'],
        data['session_id'],
        data.get('user_type', 'user'),
        data.get('context')
    )
    
    # Ek alanlar
    if 'metadata' in data:
        user_validator = UserInputValidator()
        validated['metadata'] = user_validator.validate_json(
            json.dumps(data['metadata']) if isinstance(data['metadata'], dict) else data['metadata']
        )
    
    return validated


def validate_complete_document_request(file: UploadedFile, data: Dict[str, Any]) -> Dict[str, Any]:
    """Tam döküman isteği doğrulama"""
    if 'title' not in data:
        raise ValidationException("Döküman başlığı gerekli", field="title")
    
    # Ana doğrulama
    validated = validate_document_upload(
        file,
        data['title'],
        data.get('description'),
        data.get('tags')
    )
    
    # Dil doğrulama
    if 'language' in data:
        chat_validator = ChatMessageValidator()
        validated['language'] = chat_validator.validate_language(data['language'])
    
    return validated


def validate_complete_search_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tam arama isteği doğrulama"""
    if 'query' not in data:
        raise ValidationException("Arama sorgusu gerekli", field="query")
    
    # Ana doğrulama
    validated = validate_search_query(
        data['query'],
        data.get('filters')
    )
    
    # Sayfalama
    if 'page' in data:
        try:
            page = int(data['page'])
            if page < 1:
                raise ValidationException("Sayfa numarası 1'den küçük olamaz", field="page")
            validated['page'] = page
        except (ValueError, TypeError):
            raise ValidationException("Sayfa numarası integer olmalıdır", field="page")
    
    if 'page_size' in data:
        try:
            page_size = int(data['page_size'])
            if page_size < 1 or page_size > 100:
                raise ValidationException("Sayfa boyutu 1-100 arasında olmalıdır", field="page_size")
            validated['page_size'] = page_size
        except (ValueError, TypeError):
            raise ValidationException("Sayfa boyutu integer olmalıdır", field="page_size")
    
    return validated