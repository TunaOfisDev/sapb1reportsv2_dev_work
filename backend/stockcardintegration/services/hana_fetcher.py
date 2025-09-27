"""
HANA veri çekme yardımcıları
"""

import logging
import requests
from django.conf import settings

from sapreports.jwt_utils import get_access_token_for_system_user

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
#  Ürün Fiyat Listesi (product-price-list) çekici
# ──────────────────────────────────────────────────────────────
def fetch_hana_product_price_list() -> list[dict]:
    """
    SAP HANA servisinden fiyat listesi json’u döndürür.

    • Sistem kullanıcısı için access token alır.
    • Token yoksa headers’sız dener (geri uyum için).
    • Başarısız olursa boş liste döner.
    """
    token = get_access_token_for_system_user()
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    url = f"http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/product-price-list/"
    try:
        resp = requests.get(url, headers=headers, timeout=60)
        if resp.status_code == 200:
            return resp.json()  # örn: [{Ürün Kodu: …}, …]
        else:
            logger.error(
                "[hana_fetcher] Fiyat listesi isteği başarısız: %s - %s",
                resp.status_code,
                resp.text[:300],
            )
    except requests.RequestException as e:
        logger.error("[hana_fetcher] HANA fiyat listesi isteği hatası: %s", e)

    return []
