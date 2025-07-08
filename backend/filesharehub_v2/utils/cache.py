# backend/filesharehub_v2/utils/cache.py
import hashlib
import redis
from django.conf import settings

redis_client = redis.StrictRedis.from_url(settings.CELERY_BROKER_URL)

def _make_key(abs_path: str) -> str:
    """
    Absolut dosya yolu üzerinden Redis key üretir.
    """
    sha1 = hashlib.sha1(abs_path.encode()).hexdigest()
    return f"thumb:{sha1}"

def cache_thumbnail_path(abs_path: str, thumb_path: str, timeout=86400):
    """
    Thumbnail yolunu Redis'e cache'ler.
    """
    key = _make_key(abs_path)
    redis_client.setex(key, timeout, thumb_path)

def get_cached_thumbnail(abs_path: str) -> str | None:
    """
    Redis cache'de varsa thumbnail yolunu döner.
    """
    key = _make_key(abs_path)
    value = redis_client.get(key)
    return value.decode() if value else None
