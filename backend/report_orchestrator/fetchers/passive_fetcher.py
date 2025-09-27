# backend/report_orchestrator/fetchers/passive_fetcher.py

import requests
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def fetch_passive_mode_data(data_pull_url: str) -> Tuple[dict, str]:
    """
    Pasif modlu raporlarda:
    - doğrudan data_pull_url'den veri çekilir
    - kural motoru bu veriyi işleyecek

    Returns:
        (raw_json_data, error_message)
    """
    try:
        response = requests.get(data_pull_url, timeout=10)
        response.raise_for_status()
        return response.json(), ""

    except requests.exceptions.RequestException as e:
        logger.error(f"[passive_fetcher] Ağ hatası: {str(e)}")
        return {}, f"Ağ hatası: {str(e)}"
    except ValueError as e:
        logger.error(f"[passive_fetcher] JSON dönüşüm hatası: {str(e)}")
        return {}, f"Geçersiz JSON: {str(e)}"
    except Exception as e:
        logger.error(f"[passive_fetcher] Bilinmeyen hata: {str(e)}")
        return {}, f"Bilinmeyen hata: {str(e)}"
