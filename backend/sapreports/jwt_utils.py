# backend/sapreports/jwt_utils.py

from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger('celery')


def get_or_create_jwt_token():
    """
    Sistem kullanıcısı için önbellekten JWT token getirir,
    yoksa oluşturur ve 1 saat cache'e alır.
    """
    jwt_token = cache.get('jwt_token')
    if jwt_token:
        return jwt_token

    try:
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email='system@example.com',
            defaults={'is_active': True, 'is_staff': True}
        )
        if created:
            user.set_password('some-secure-password')
            user.save()

        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)
        cache.set('jwt_token', jwt_token, timeout=3600)
        return jwt_token

    except Exception as e:
        logger.error(f"[JWT ERROR] Token üretilemedi: {e}")
        return None
