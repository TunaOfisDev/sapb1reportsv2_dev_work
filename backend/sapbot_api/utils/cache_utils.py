# backend/sapbot_api/utils/cache_utils.py
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import redis
import pickle

logger = logging.getLogger(__name__)


class CacheManager:
    """SAPBot için merkezi cache yöneticisi"""
    
    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.default_timeout = getattr(settings, 'SAPBOT_CACHE_TIMEOUT', 3600)
        
    def _get_redis_client(self) -> redis.Redis:
        """Redis client'ı al"""
        try:
            return redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB_SAPBOT', 3),
                password=getattr(settings, 'REDIS_PASS', None),
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Redis bağlantısı başarısız: {e}")
            return None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Cache anahtarı oluştur"""
        key_parts = [prefix]
        
        # Args'ları ekle
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            else:
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Kwargs'ları ekle
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        return "sapbot:" + ":".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        try:
            # Önce Django cache'de ara
            cached_data = cache.get(key)
            if cached_data is not None:
                return cached_data
            
            # Redis'te ara
            if self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    try:
                        return json.loads(cached_data)
                    except json.JSONDecodeError:
                        # Pickle ile dene
                        try:
                            return pickle.loads(cached_data.encode('latin-1'))
                        except:
                            return cached_data
            
            return None
        except Exception as e:
            logger.error(f"Cache get hatası: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Cache'e veri kaydet"""
        timeout = timeout or self.default_timeout
        
        try:
            # Django cache'e kaydet
            cache.set(key, value, timeout)
            
            # Redis'e de kaydet
            if self.redis_client:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, (str, int, float, bool)):
                    serialized_value = json.dumps(value)
                else:
                    # Pickle kullan
                    serialized_value = pickle.dumps(value).decode('latin-1')
                
                self.redis_client.setex(key, timeout, serialized_value)
            
            return True
        except Exception as e:
            logger.error(f"Cache set hatası: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Cache'den veri sil"""
        try:
            cache.delete(key)
            if self.redis_client:
                self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete hatası: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Pattern'e uyan tüm cache'leri temizle"""
        try:
            deleted_count = 0
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted_count = self.redis_client.delete(*keys)
            return deleted_count
        except Exception as e:
            logger.error(f"Cache clear pattern hatası: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Cache'de anahtar var mı?"""
        try:
            return cache.get(key) is not None or (
                self.redis_client and self.redis_client.exists(key)
            )
        except Exception as e:
            logger.error(f"Cache exists hatası: {e}")
            return False


class ChatCacheManager(CacheManager):
    """Chat özelinde cache yöneticisi"""
    
    def get_chat_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Chat geçmişini al"""
        key = self._generate_key("chat_history", session_id)
        
        try:
            if self.redis_client:
                # Redis list'den al
                messages = self.redis_client.lrange(key, 0, limit - 1)
                return [json.loads(msg) for msg in messages]
            
            # Django cache'den al
            cached_data = cache.get(key, [])
            return cached_data[:limit]
        except Exception as e:
            logger.error(f"Chat history cache hatası: {e}")
            return []
    
    def add_chat_message(self, session_id: str, message: Dict, max_history: int = 100) -> bool:
        """Chat mesajını cache'e ekle"""
        key = self._generate_key("chat_history", session_id)
        
        try:
            if self.redis_client:
                # Redis list'e ekle
                self.redis_client.lpush(key, json.dumps(message, ensure_ascii=False))
                self.redis_client.ltrim(key, 0, max_history - 1)
                self.redis_client.expire(key, 86400)  # 24 saat
            
            # Django cache'e de ekle
            history = cache.get(key, [])
            history.insert(0, message)
            history = history[:max_history]
            cache.set(key, history, 86400)
            
            return True
        except Exception as e:
            logger.error(f"Chat message cache hatası: {e}")
            return False
    
    def get_user_context(self, user_id: str) -> Dict:
        """Kullanıcı bağlamını al"""
        key = self._generate_key("user_context", user_id)
        return self.get(key) or {}
    
    def set_user_context(self, user_id: str, context: Dict, timeout: int = 7200) -> bool:
        """Kullanıcı bağlamını kaydet"""
        key = self._generate_key("user_context", user_id)
        return self.set(key, context, timeout)
    
    def get_response_cache(self, query_hash: str) -> Optional[Dict]:
        """Yanıt cache'ini al"""
        key = self._generate_key("response", query_hash)
        return self.get(key)
    
    def set_response_cache(self, query_hash: str, response: Dict, timeout: int = 3600) -> bool:
        """Yanıt cache'ini kaydet"""
        key = self._generate_key("response", query_hash)
        return self.set(key, response, timeout)


class EmbeddingCacheManager(CacheManager):
    """Embedding cache yöneticisi"""
    
    def get_embedding(self, content_hash: str) -> Optional[List[float]]:
        """Embedding'i al"""
        key = self._generate_key("embedding", content_hash)
        return self.get(key)
    
    def set_embedding(self, content_hash: str, embedding: List[float], timeout: int = 604800) -> bool:
        """Embedding'i kaydet (7 gün)"""
        key = self._generate_key("embedding", content_hash)
        return self.set(key, embedding, timeout)
    
    def get_batch_embeddings(self, content_hashes: List[str]) -> Dict[str, List[float]]:
        """Toplu embedding al"""
        embeddings = {}
        
        try:
            if self.redis_client:
                # Redis pipeline ile toplu işlem
                pipe = self.redis_client.pipeline()
                keys = [self._generate_key("embedding", hash_val) for hash_val in content_hashes]
                
                for key in keys:
                    pipe.get(key)
                
                results = pipe.execute()
                
                for i, result in enumerate(results):
                    if result:
                        try:
                            embeddings[content_hashes[i]] = json.loads(result)
                        except:
                            pass
            
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding cache hatası: {e}")
            return {}
    
    def set_batch_embeddings(self, embeddings: Dict[str, List[float]], timeout: int = 604800) -> bool:
        """Toplu embedding kaydet"""
        try:
            if self.redis_client:
                pipe = self.redis_client.pipeline()
                
                for content_hash, embedding in embeddings.items():
                    key = self._generate_key("embedding", content_hash)
                    pipe.setex(key, timeout, json.dumps(embedding))
                
                pipe.execute()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Batch embedding set hatası: {e}")
            return False


class SearchCacheManager(CacheManager):
    """Arama cache yöneticisi"""
    
    def get_search_results(self, query_hash: str, filters: Dict = None) -> Optional[List[Dict]]:
        """Arama sonuçlarını al"""
        filter_hash = self._hash_dict(filters) if filters else "no_filter"
        key = self._generate_key("search", query_hash, filter_hash)
        return self.get(key)
    
    def set_search_results(self, query_hash: str, results: List[Dict], filters: Dict = None, timeout: int = 1800) -> bool:
        """Arama sonuçlarını kaydet (30 dakika)"""
        filter_hash = self._hash_dict(filters) if filters else "no_filter"
        key = self._generate_key("search", query_hash, filter_hash)
        return self.set(key, results, timeout)
    
    def get_popular_queries(self, period: str = "daily") -> List[Dict]:
        """Popüler sorguları al"""
        key = self._generate_key("popular_queries", period)
        return self.get(key) or []
    
    def set_popular_queries(self, queries: List[Dict], period: str = "daily", timeout: int = 3600) -> bool:
        """Popüler sorguları kaydet"""
        key = self._generate_key("popular_queries", period)
        return self.set(key, queries, timeout)
    
    def _hash_dict(self, data: Dict) -> str:
        """Dictionary'yi hash'le"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8]


class SystemCacheManager(CacheManager):
    """Sistem cache yöneticisi"""
    
    def get_system_config(self, key: str) -> Optional[Any]:
        """Sistem konfigürasyonu al"""
        cache_key = self._generate_key("system_config", key)
        return self.get(cache_key)
    
    def set_system_config(self, key: str, value: Any, timeout: int = 3600) -> bool:
        """Sistem konfigürasyonu kaydet"""
        cache_key = self._generate_key("system_config", key)
        return self.set(cache_key, value, timeout)
    
    def get_user_session(self, session_id: str) -> Optional[Dict]:
        """Kullanıcı oturum bilgisi al"""
        key = self._generate_key("user_session", session_id)
        return self.get(key)
    
    def set_user_session(self, session_id: str, session_data: Dict, timeout: int = 86400) -> bool:
        """Kullanıcı oturum bilgisi kaydet"""
        key = self._generate_key("user_session", session_id)
        return self.set(key, session_data, timeout)
    
    def get_rate_limit_info(self, identifier: str) -> Optional[Dict]:
        """Rate limit bilgisi al"""
        key = self._generate_key("rate_limit", identifier)
        return self.get(key)
    
    def set_rate_limit_info(self, identifier: str, info: Dict, timeout: int = 3600) -> bool:
        """Rate limit bilgisi kaydet"""
        key = self._generate_key("rate_limit", identifier)
        return self.set(key, info, timeout)


# Decorator'lar
def cache_result(timeout: int = 3600, key_prefix: str = "func"):
    """Fonksiyon sonucunu cache'le"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = CacheManager()
            
            # Cache key oluştur
            key = cache_manager._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Cache'den al
            cached_result = cache_manager.get(key)
            if cached_result is not None:
                return cached_result
            
            # Fonksiyonu çalıştır ve cache'le
            result = func(*args, **kwargs)
            cache_manager.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_embedding(timeout: int = 604800):
    """Embedding fonksiyonunu cache'le"""
    def decorator(func):
        @wraps(func)
        def wrapper(content: str, *args, **kwargs):
            cache_manager = EmbeddingCacheManager()
            
            # Content hash oluştur
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Cache'den al
            cached_embedding = cache_manager.get_embedding(content_hash)
            if cached_embedding is not None:
                return cached_embedding
            
            # Embedding oluştur ve cache'le
            embedding = func(content, *args, **kwargs)
            cache_manager.set_embedding(content_hash, embedding, timeout)
            
            return embedding
        return wrapper
    return decorator


def cache_search_result(timeout: int = 1800):
    """Arama sonucunu cache'le"""
    def decorator(func):
        @wraps(func)
        def wrapper(query: str, filters: Dict = None, *args, **kwargs):
            cache_manager = SearchCacheManager()
            
            # Query hash oluştur
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            
            # Cache'den al
            cached_results = cache_manager.get_search_results(query_hash, filters)
            if cached_results is not None:
                return cached_results
            
            # Arama yap ve cache'le
            results = func(query, filters, *args, **kwargs)
            cache_manager.set_search_results(query_hash, results, filters, timeout)
            
            return results
        return wrapper
    return decorator


# Singleton cache manager instances
chat_cache = ChatCacheManager()
embedding_cache = EmbeddingCacheManager()
search_cache = SearchCacheManager()
system_cache = SystemCacheManager()


# Utility functions
def clear_all_cache():
    """Tüm cache'i temizle"""
    try:
        cache.clear()
        cache_manager = CacheManager()
        if cache_manager.redis_client:
            cache_manager.redis_client.flushdb()
        logger.info("Tüm cache temizlendi")
        return True
    except Exception as e:
        logger.error(f"Cache temizleme hatası: {e}")
        return False


def get_cache_stats() -> Dict:
    """Cache istatistiklerini al"""
    try:
        cache_manager = CacheManager()
        stats = {
            'redis_connected': cache_manager.redis_client is not None,
            'django_cache_active': True
        }
        
        if cache_manager.redis_client:
            redis_info = cache_manager.redis_client.info()
            stats.update({
                'redis_memory_used': redis_info.get('used_memory_human', 'N/A'),
                'redis_keyspace_hits': redis_info.get('keyspace_hits', 0),
                'redis_keyspace_misses': redis_info.get('keyspace_misses', 0),
                'redis_connected_clients': redis_info.get('connected_clients', 0)
            })
        
        return stats
    except Exception as e:
        logger.error(f"Cache stats hatası: {e}")
        return {'error': str(e)}


def warm_up_cache():
    """Cache'i ön yükleme"""
    try:
        # Sistem konfigürasyonlarını yükle
        from ..models import SystemConfiguration
        configs = SystemConfiguration.objects.all()
        
        for config in configs:
            system_cache.set_system_config(config.key, config.get_typed_value())
        
        logger.info("Cache ön yükleme tamamlandı")
        return True
    except Exception as e:
        logger.error(f"Cache ön yükleme hatası: {e}")
        return False