# File: procure_compare/services/hana_fetcher.py
import requests
from django.conf import settings
from django.core.cache import cache
from loguru import logger

def fetch_hana_procure_compare_data(token, days=None):
    """
    SAP HANA'dan satınalma teklif ve sipariş karşılaştırma verisini çeker.
    """
    try:
        headers = {'Authorization': f'Bearer {token}'}
        url = f"http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/procure_compare/"
        if days:
            url += f"?days={days}"

        response = requests.get(url, headers=headers, timeout=60)

        if response.status_code == 200:
            
            return response.json()
        else:
            logger.error(f"HANA API Hatası - Status: {response.status_code}, Mesaj: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"HANA API bağlantı hatası: {e}")
        return None



def fetch_item_purchase_history(token, item_code):
    """
    Belirli bir ürün kodu için satınalma geçmişi verilerini SAP HANA'dan çeker.
    """
    try:
        cache_key = f"item_purchase_history:{item_code}"
        cached_data = cache.get(cache_key)

        if cached_data:
            
            return {
                "source": "cache",
                "data": cached_data
            }

        headers = {'Authorization': f'Bearer {token}'}
        url = f"http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/item_purchase_history/?item_code={item_code}"

        response = requests.get(url, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()

            if isinstance(result, list):
                cache.set(cache_key, result, timeout=60*60*2)  # 2 saatlik cache
                
                return {
                    "source": "hana",
                    "data": result
                }
            else:
                
                return None
        else:
            logger.error(f"HATA - HANA API Status: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"HANA bağlantı hatası: {e}")
        return None


