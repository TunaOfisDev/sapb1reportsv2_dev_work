# backend/sapreports/tasks/periodic.py

import logging
import time
import requests
from celery import shared_task
from django.conf import settings
from sapreports.jwt_utils import get_access_token_for_system_user, get_token_for_email

logger = logging.getLogger(__name__)

API_PATH = "/api/v2/rawmaterialwarehousestock/fetch-hana-data/"
DEFAULT_TIMEOUT = (5, 30)  # (connect, read) saniye
MAX_RETRY = 3
BACKOFF_BASE = 2  # üssel backoff

def _build_base_url() -> str:
    """
    Tercihen settings.SITE_URL, yoksa SERVER_HOST kullan.
    SITE_URL formatı genelde 'http://host:port'
    """
    base = getattr(settings, "SITE_URL", None)
    if base:
        return base.rstrip("/")
    server_host = getattr(settings, "SERVER_HOST", "127.0.0.1")
    api_port = getattr(settings, "API_PORT", "8000")
    return f"http://{server_host}:{api_port}"

def _fetch_with_token(token: str) -> requests.Response:
    url = f"{_build_base_url()}{API_PATH}"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)

@shared_task(name="sapreports.periodic_task")
def periodic_task():
    """
    Her 10 dakikada bir tetiklenen görev:
    - Sistem kullanıcısı access token’ı ile protected endpoint’e istek atar.
    - 401 olursa token’ı yenilemeyi dener (bir kez).
    - Network hataları için üssel backoff ile toplam MAX_RETRY denemesi yapar.
    """
    # 1) Sistem token al
    token = get_access_token_for_system_user()
    if not token:
        logger.error("[PERIODIC] SYSTEM_USER_EMAIL tanımlı değil, kullanıcı yok veya token üretilemedi.")
        return "no-token"

    # 2) İstek + retry/backoff
    attempt = 0
    while attempt < MAX_RETRY:
        try:
            resp = _fetch_with_token(token)

            # 401 ise: cache’deki token bayat olabilir → bir kez yenile (email ile)
            if resp.status_code == 401:
                logger.warning("[PERIODIC] 401 Unauthorized. Token yenileme deneniyor...")
                # SYSTEM_USER_EMAIL üzerinden token tazele (cache miss → yeni üretir)
                system_email = getattr(settings, "SYSTEM_USER_EMAIL", None)
                if system_email:
                    refreshed = get_token_for_email(system_email)
                    token = (refreshed or {}).get("access")
                    if not token:
                        logger.error("[PERIODIC] Token yenileme başarısız. Görev sonlandırılıyor.")
                        return "token-refresh-failed"
                    resp = _fetch_with_token(token)  # hemen tekrar dene
                else:
                    logger.error("[PERIODIC] SYSTEM_USER_EMAIL ayarsız; token yenileme yapılamadı.")
                    return "no-system-email"

            if resp.status_code == 200:
                logger.info("[PERIODIC] Veri çekme başarılı.")
                return "ok"

            # Diğer HTTP durumları: logla ve retry et
            logger.error(f"[PERIODIC] API başarısız: {resp.status_code} - {resp.text[:500]}")
        except requests.RequestException as e:
            logger.warning(f"[PERIODIC] İstek hatası (attempt {attempt+1}/{MAX_RETRY}): {e}")

        attempt += 1
        if attempt < MAX_RETRY:
            sleep_s = BACKOFF_BASE ** attempt
            time.sleep(sleep_s)

    logger.error("[PERIODIC] Azami deneme sayısı aşıldı, görev başarısız.")
    return "failed"
