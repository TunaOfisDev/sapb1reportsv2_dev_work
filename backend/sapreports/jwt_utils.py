# backend/sapreports/jwt_utils.py

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

SYSTEM_USER_EMAIL = getattr(settings, "SYSTEM_USER_EMAIL", None)

def get_token_for_user(user):
    """Verilen user için {access, refresh} döndürür."""
    try:
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}
    except Exception as e:
        logger.error(f"[JWT] get_token_for_user failed: {e}")
        return None

def get_token_for_email(email: str, cache_ttl=3600):
    """
    Var olan bir email için {access, refresh} üretir (create YAPMAZ).
    access token'ı cache'ler. Kullanıcı yoksa None döner.
    """
    if not email:
        logger.error("[JWT] get_token_for_email: email boş")
        return None

    cache_key = f"jwt_access:{email}"
    cached_access = cache.get(cache_key)
    if cached_access:
        return {"access": cached_access, "refresh": None}

    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.error(f"[JWT] Kullanıcı bulunamadı: {email}")
        return None

    tokens = get_token_for_user(user)
    if tokens and tokens.get("access"):
        cache.set(cache_key, tokens["access"], timeout=cache_ttl)
    return tokens

def get_access_token_for_system_user():
    """SYSTEM_USER_EMAIL için access token döndürür (create YAPMAZ)."""
    if not SYSTEM_USER_EMAIL:
        logger.error("[JWT] SYSTEM_USER_EMAIL tanımlı değil.")
        return None
    res = get_token_for_email(SYSTEM_USER_EMAIL)
    return res.get("access") if res else None

# ==== Geriye uyumluluk shimi (ESKİ API) ====
def get_or_create_jwt_token():
    """
    ESKİ KULLANIMI DESTEKLER:
    - Eski kodlar bu fonksiyonu import ediyor.
    - Access token (str) döndürür.
    - Sistem kullanıcısını otomatik oluşturmaz; yoksa None döner.
    """
    access = get_access_token_for_system_user()
    if not access:
        logger.error("[JWT] get_or_create_jwt_token: sistem access üretilemedi (email yok/USER yok).")
    return access
