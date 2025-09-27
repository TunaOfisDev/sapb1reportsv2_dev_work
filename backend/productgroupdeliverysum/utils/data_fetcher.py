# backend/productgroupdeliverysum/utils/data_fetcher.py
import requests
from django.conf import settings
from loguru import logger

def fetch_hana_db_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/productgroupdeliverysum/'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Eğer HTTP hatası varsa, exception fırlatır
        data = response.json()
        
        # Log ekleyelim ve veriyi kontrol edelim
        logger.info(f"HANA DB'den gelen veri: {data}")
        
        return data
    except requests.RequestException as e:
        logger.error(f"Hata: {e}")
        logger.error(f"Response content: {response.text}")
        return None
