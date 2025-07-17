
# backend/sapbot_api/utils/helpers.py
"""
SAPBot API Helper Functions

Bu modül genel amaçlı yardımcı fonksiyonları içerir.
String işleme, validasyon, format dönüştürme vb.
"""

import re
import uuid
import hashlib
import secrets
import string
import json
import math
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, quote, unquote
from decimal import Decimal, ROUND_HALF_UP
import logging

from django.utils import timezone as django_timezone
from django.utils.text import slugify
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_session_id() -> str:
    """Unique session ID oluştur"""
    return f"session_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp())}"


def generate_api_key(length: int = 48) -> str:
    """API key oluştur"""
    return f"sapbot_{secrets.token_urlsafe(length)}"


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """String'den hash oluştur"""
    try:
        if algorithm == "md5":
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data.encode('utf-8')).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
        else:
            raise ValueError(f"Desteklenmeyen algoritma: {algorithm}")
    except Exception as e:
        logger.error(f"Hash oluşturma hatası: {e}")
        return ""


def generate_short_hash(data: str, length: int = 8) -> str:
    """Kısa hash oluştur"""
    return generate_hash(data)[:length]


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Kullanıcı girişini temizle"""
    if not text:
        return ""
    
    # HTML etiketlerini kaldır
    text = re.sub(r'<[^>]+>', '', text)
    
    # Zararlı script'leri kaldır
    text = re.sub(r'(javascript:|vbscript:|on\w+\s*=)', '', text, flags=re.IGNORECASE)
    
    # SQL injection pattern'larını kaldır
    text = re.sub(r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)', '', text, flags=re.IGNORECASE)
    
    # Özel karakterleri escape et
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Fazla boşlukları temizle
    text = ' '.join(text.split())
    
    # Uzunluk kontrolü
    if max_length and len(text) > max_length:
        text = text[:max_length].strip()
    
    return text


def clean_text(text: str) -> str:
    """Metin temizleme - SAP dökümanları için özelleştirilmiş"""
    if not text:
        return ""
    
    # Gereksiz boşlukları temizle
    text = ' '.join(text.split())
    
    # Türkçe karakter düzeltmeleri
    turkish_fixes = {
        'ð': 'ğ', 'Ð': 'Ğ',
        'ý': 'ı', 'Ý': 'İ', 
        'þ': 'ş', 'Þ': 'Ş',
        'ç': 'ç', 'Ç': 'Ç',
        'ü': 'ü', 'Ü': 'Ü', 
        'ö': 'ö', 'Ö': 'Ö',
        'â': 'a', 'Â': 'A',
        'î': 'i', 'Î': 'İ',
        'û': 'u', 'Û': 'U'
    }
    
    for wrong, correct in turkish_fixes.items():
        text = text.replace(wrong, correct)
    
    # Satır sonlarını normalize et
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Fazla satır boşluklarını temizle
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def extract_sap_module_from_text(text: str) -> Optional[str]:
    """Metinden SAP modülünü tespit et"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # SAP modül pattern'ları - firmaya özel
    module_patterns = {
        'FI': [
            r'\bfi\b', r'finansal', r'mali', r'muhasebe', r'genel muhasebe',
            r'chart of accounts', r'hesap planı', r'journal entry',
            r'muhasebe kaydı', r'financial', r'accounting'
        ],
        'MM': [
            r'\bmm\b', r'malzeme', r'satın alma', r'stok', r'material',
            r'purchasing', r'procurement', r'vendor', r'tedarikçi',
            r'purchase order', r'satın alma siparişi'
        ],
        'SD': [
            r'\bsd\b', r'satış', r'dağıtım', r'sales', r'distribution',
            r'müşteri', r'customer', r'sales order', r'satış siparişi',
            r'quotation', r'teklif', r'invoice', r'fatura'
        ],
        'CRM': [
            r'\bcrm\b', r'customer relationship', r'müşteri ilişkileri',
            r'opportunity', r'fırsat', r'lead', r'campaign', r'kampanya'
        ],
        'PROD': [
            r'üretim', r'production', r'manufacturing', r'imalat',
            r'work order', r'iş emri', r'bom', r'bill of material'
        ],
        'INV': [
            r'inventory', r'envanter', r'stok yönetimi', r'warehouse',
            r'depo', r'stock', r'item master', r'malzeme kartı'
        ],
        'HR': [
            r'\bhr\b', r'human resources', r'insan kaynakları',
            r'personel', r'employee', r'çalışan', r'payroll', r'bordro'
        ]
    }
    
    module_scores = {}
    
    for module, patterns in module_patterns.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, text_lower))
            score += matches
        
        if score > 0:
            module_scores[module] = score
    
    if module_scores:
        # En yüksek skora sahip modülü döndür
        return max(module_scores, key=module_scores.get)
    
    return None


def detect_language(text: str) -> str:
    """Basit dil tespiti"""
    if not text:
        return 'tr'
    
    text_lower = text.lower()
    
    # Türkçe karakterler
    turkish_chars = ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü']
    turkish_words = [
        've', 'bir', 'bu', 'için', 'ile', 'olan', 'olan', 'var',
        'yok', 'gibi', 'kadar', 'sonra', 'önce', 'şimdi', 'nasıl'
    ]
    
    # İngilizce kelimeler
    english_words = [
        'the', 'and', 'for', 'with', 'this', 'that', 'have',
        'from', 'they', 'know', 'want', 'been', 'good', 'much'
    ]
    
    turkish_score = 0
    english_score = 0
    
    # Türkçe karakter kontrolü
    for char in turkish_chars:
        turkish_score += text_lower.count(char) * 2
    
    # Kelime kontrolü
    words = text_lower.split()
    for word in words:
        if word in turkish_words:
            turkish_score += 1
        elif word in english_words:
            english_score += 1
    
    return 'tr' if turkish_score > english_score else 'en'


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 1000, 
    overlap: int = 200,
    preserve_paragraphs: bool = True
) -> List[Dict[str, Any]]:
    """Metni chunk'lara böl"""
    if not text:
        return []
    
    chunks = []
    
    if preserve_paragraphs:
        # Paragraf bazlı bölme
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            if current_size + para_size > chunk_size and current_chunk:
                # Mevcut chunk'ı kaydet
                chunks.append({
                    'text': current_chunk.strip(),
                    'size': current_size,
                    'chunk_index': len(chunks)
                })
                
                # Overlap için son kısmı al
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + "\n\n" + paragraph
                    current_size = len(current_chunk)
                else:
                    current_chunk = paragraph
                    current_size = para_size
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                    current_size += para_size + 2
                else:
                    current_chunk = paragraph
                    current_size = para_size
        
        # Son chunk'ı ekle
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'size': current_size,
                'chunk_index': len(chunks)
            })
    
    else:
        # Karakter bazlı bölme
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunk_text = text[start:]
            else:
                # Kelime sınırında kes
                end = text.rfind(' ', start, end)
                if end == -1 or end <= start:
                    end = start + chunk_size
                chunk_text = text[start:end]
            
            chunks.append({
                'text': chunk_text.strip(),
                'size': len(chunk_text),
                'chunk_index': chunk_index,
                'start_pos': start,
                'end_pos': end
            })
            
            # Overlap ile başlangıcı ayarla
            start = max(start + chunk_size - overlap, end)
            chunk_index += 1
    
    return chunks


def calculate_similarity(text1: str, text2: str) -> float:
    """Basit metin benzerlik hesaplama"""
    if not text1 or not text2:
        return 0.0
    
    # Kelimelere böl ve küçük harfe çevir
    words1 = set(clean_text(text1.lower()).split())
    words2 = set(clean_text(text2.lower()).split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def format_response_time(seconds: float) -> str:
    """Yanıt süresini formatla"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def format_file_size(bytes_size: int) -> str:
    """Dosya boyutunu formatla"""
    if bytes_size == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_size, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_size / p, 2)
    
    return f"{s} {size_names[i]}"


def format_currency(amount: Union[int, float, Decimal], currency: str = "TRY") -> str:
    """Para birimi formatla"""
    try:
        if isinstance(amount, str):
            amount = float(amount)
        
        # Türkiye formatı: ###.###,##
        if currency == "TRY":
            formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return f"{formatted} ₺"
        else:
            return f"{amount:,.2f} {currency}"
    
    except (ValueError, TypeError):
        return f"0,00 {currency}"


def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """Yüzde formatla"""
    try:
        if isinstance(value, str):
            value = float(value)
        
        return f"{value:.{decimal_places}f}%"
    
    except (ValueError, TypeError):
        return "0.0%"


def parse_boolean(value: Any) -> bool:
    """String'i boolean'a çevir"""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'on', 'evet', 'doğru']
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    return False


def validate_email_address(email: str) -> bool:
    """Email adresini validate et"""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def validate_url(url: str) -> bool:
    """URL'yi validate et"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Metni belirtilen uzunlukta kes"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix


def extract_keywords(text: str, min_length: int = 3, max_count: int = 10) -> List[str]:
    """Metinden anahtar kelime çıkar"""
    if not text:
        return []
    
    # Stop words - Türkçe
    stop_words = {
        've', 'bir', 'bu', 'şu', 'o', 'için', 'ile', 'de', 'da',
        'ki', 'gibi', 'kadar', 'çok', 'az', 'en', 'daha', 'çünkü',
        'ama', 'fakat', 'ancak', 'ya', 'yada', 'veya', 'hem', 'ne',
        'hiç', 'her', 'bazı', 'kimi', 'hangi', 'nasıl', 'neden',
        'nerede', 'ne zaman', 'kim', 'kime', 'kimin', 'the', 'and',
        'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
    }
    
    # Metni temizle ve kelimelere böl
    cleaned_text = clean_text(text.lower())
    words = re.findall(r'\b[a-zçğıöşüA-ZÇĞIİÖŞÜ]+\b', cleaned_text)
    
    # Filtreleme
    keywords = []
    word_freq = {}
    
    for word in words:
        if (len(word) >= min_length and 
            word.lower() not in stop_words and
            not word.isdigit()):
            
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Frekansa göre sırala
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:max_count]]
    
    return keywords


def generate_slug(text: str, max_length: int = 50) -> str:
    """URL-friendly slug oluştur"""
    if not text:
        return ""
    
    # Django'nun slugify fonksiyonunu kullan
    slug = slugify(text)
    
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Güvenli JSON parse"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Güvenli JSON serialize"""
    try:
        return json.dumps(data, ensure_ascii=False, indent=None)
    except (TypeError, ValueError):
        return default


def get_client_ip(request) -> str:
    """İstemci IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


def get_user_agent(request) -> str:
    """User agent bilgisini al"""
    return request.META.get('HTTP_USER_AGENT', '')[:500]  # Max 500 karakter


def time_ago(dt: datetime) -> str:
    """Zaman farkını human-readable formatla"""
    if not dt:
        return ""
    
    # Timezone aware yap
    if dt.tzinfo is None:
        dt = django_timezone.make_aware(dt)
    
    now = django_timezone.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "az önce"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} dakika önce"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} saat önce"
    elif seconds < 2592000:  # 30 gün
        days = int(seconds // 86400)
        return f"{days} gün önce"
    elif seconds < 31536000:  # 1 yıl
        months = int(seconds // 2592000)
        return f"{months} ay önce"
    else:
        years = int(seconds // 31536000)
        return f"{years} yıl önce"


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Hassas veriyi maskele"""
    if not data or len(data) <= visible_chars * 2:
        return mask_char * len(data) if data else ""
    
    start = data[:visible_chars]
    end = data[-visible_chars:]
    middle = mask_char * (len(data) - visible_chars * 2)
    
    return start + middle + end


def generate_random_string(length: int = 8, include_numbers: bool = True, include_symbols: bool = False) -> str:
    """Rastgele string oluştur"""
    chars = string.ascii_letters
    
    if include_numbers:
        chars += string.digits
    
    if include_symbols:
        chars += "!@#$%^&*"
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def is_valid_uuid(uuid_string: str) -> bool:
    """UUID geçerliliğini kontrol et"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def merge_dicts(*dicts: Dict) -> Dict:
    """Sözlükleri birleştir"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """İç içe sözlüğü düzleştir"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_get(dictionary: Dict, keys: str, default: Any = None) -> Any:
    """Nested dictionary'den güvenli değer alma"""
    try:
        keys_list = keys.split('.')
        value = dictionary
        for key in keys_list:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


# Singleton cache for expensive operations
_cache = {}

def memoize(func):
    """Basit memoization decorator"""
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in _cache:
            _cache[key] = func(*args, **kwargs)
        return _cache[key]
    return wrapper


def clear_memoize_cache():
    """Memoization cache'ini temizle"""
    global _cache
    _cache.clear()