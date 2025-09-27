# backend/stockcardintegration/services/productpricelist_services.py
"""
HANA’dan fiyat listesi verisini çekip `ProductPriceList` tablosuna yazan
hafif-servis katmanı.  Celery görevi ve API view burada tanımlı
yardımcıları çağırır; gereksiz log kalabalığından kaçınır.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Sequence

from django.core.cache import cache

from stockcardintegration.models.productpricelist_models import ProductPriceList
from stockcardintegration.services.hana_fetcher import (
    fetch_hana_product_price_list,
)

# ──────────────────────────────────────────────────────────────
# Ayar – API tarafıyla da aynı anahtar kullanıyoruz
LOCK_KEY = "lock:price_sync"
TTL_SEC = 10  # “son N saniyede senkron yapıldı mı?” kontrol süresi
# ──────────────────────────────────────────────────────────────


# ╭──────────────────────────────────────────────────────────╮
# │ 1. Yardımcı (tazelik kontrolü)                          │
# ╰──────────────────────────────────────────────────────────╯
def _is_recent_sync() -> bool:
    """
    Son senkronun `TTL_SEC`’ten eski olup olmadığını hızlıca kontrol eder.
    """
    stamp = cache.get(LOCK_KEY)
    if not stamp:
        return False

    try:
        last_run = datetime.fromisoformat(stamp)
    except ValueError:
        # Cache’de bozulmuş veri varsa güvenli tarafta kal
        return False

    return (datetime.now(timezone.utc) - last_run) < timedelta(seconds=TTL_SEC)


# ╭──────────────────────────────────────────────────────────╮
# │ 2. Çek + Upsert ana fonksiyonu                           │
# ╰──────────────────────────────────────────────────────────╯
def sync_price_list_if_needed() -> int:
    """
    • Cache TTL’i aşıldıysa HANA’dan veriyi çeker  
    • Her satır için `ProductPriceList.upsert_from_hana()` çağırır  
    • İşlem adedini döndürür (TTL taze ise 0)

    **Log politikası:**  
    - Başarılı senaryoda sessiz  
    - Hata fırlatırsa üst katman (Celery görevi / view) karar versin
    """
    if _is_recent_sync():
        return 0  # Zaten taze

    hana_rows: Sequence[dict] | None = fetch_hana_product_price_list()
    if not hana_rows:
        # HANA’dan boş/None geldi; üst katman hata yakalayabilir
        raise RuntimeError("HANA sorgusu boş döndü")

    processed = 0
    for row in hana_rows:
        ProductPriceList.upsert_from_hana(row)
        processed += 1

    # TTL damgasını güncelle
    cache.set(LOCK_KEY, datetime.now(timezone.utc).isoformat(), TTL_SEC)
    return processed
