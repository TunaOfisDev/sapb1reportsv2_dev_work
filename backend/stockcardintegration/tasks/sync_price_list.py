# backend/stockcardintegration/tasks/sync_price_list.py
from __future__ import annotations
from datetime import timedelta, datetime, timezone

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from loguru import logger
from redis.exceptions import LockError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from stockcardintegration.models.productpricelist_models import ProductPriceList
from stockcardintegration.services.hana_fetcher import fetch_hana_product_price_list

LOCK_KEY = "lock:price_sync"
TTL_SEC  = 10           # => “son 10 saniyede senkron yapıldı mı?”

@shared_task(time_limit=120, soft_time_limit=90, bind=True)
def sync_price_list(self) -> str:
    # ❶ TTL – daha yeni ise atla
    if cache.get(LOCK_KEY):
        return "skip (fresh)"

    redis = cache.client.get_client()
    try:
        with redis.lock(LOCK_KEY, timeout=TTL_SEC, blocking_timeout=1):
            data = fetch_hana_product_price_list()
            if not data:
                raise ValueError("HANA empty")

            for row in data:
                ProductPriceList.upsert_from_hana(row)

            # ❷ TTL flag: sadece değerini set et
            cache.set(LOCK_KEY, datetime.utcnow().isoformat(), TTL_SEC)

            # ❸ WebSocket yayını
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "price_list", {"type": "price.refresh"}
            )

            logger.info("Price list sync OK – %s rows", len(data))
            return f"ok {len(data)}"

    except LockError:
        return "skip (locked)"
    except Exception as exc:
        self.retry(exc=exc, countdown=3)
