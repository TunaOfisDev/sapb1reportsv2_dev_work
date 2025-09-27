# backend/report_orchestrator/fetchers/active_fetcher.py

import time
import requests
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def fetch_active_mode_data(trigger_url: str, data_pull_url: str, wait_seconds: int = 300) -> Tuple[dict, str]:
    """
    Aktif modlu raporlarda:
    - trigger_url ile veri tetiklenir
    - wait_seconds kadar beklenir
    - data_pull_url'den sonuç çekilir
    Hata varsa mesaj döner.
    
    Returns:
        (result_json, error_message)
    """
    try:
        trigger_response = requests.post(trigger_url, timeout=10)

        if trigger_response.status_code not in [200, 202]:
            return {}, f"Tetikleme başarısız oldu: {trigger_response.status_code}"

        logger.info(f"[active_fetcher] Bekleniyor: {wait_seconds} sn")
        time.sleep(wait_seconds)

        logger.info(f"[active_fetcher] Veri çekiliyor: {data_pull_url}")
        data_response = requests.get(data_pull_url, timeout=15)
        data_response.raise_for_status()

        return data_response.json(), ""

    except requests.exceptions.RequestException as e:
        logger.error(f"[active_fetcher] Ağ hatası: {str(e)}")
        return {}, f"Ağ hatası: {str(e)}"
    except ValueError as e:
        logger.error(f"[active_fetcher] JSON dönüşüm hatası: {str(e)}")
        return {}, f"Geçersiz JSON: {str(e)}"
    except Exception as e:
        logger.error(f"[active_fetcher] Bilinmeyen hata: {str(e)}")
        return {}, f"Bilinmeyen hata: {str(e)}"
