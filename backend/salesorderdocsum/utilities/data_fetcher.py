# backend/salesorderdocsum/utilities/data_fetcher.py
import requests
from django.conf import settings
from loguru import logger

def fetch_hana_db_data(token, days=None):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/salesorderdocsum/'
        if days:
            url += f'?days={days}'

        response = requests.get(url, headers=headers, timeout=60)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"HANA API Hatası - Status: {response.status_code}, Mesaj: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"HANA API bağlantı hatası: {e}")
        return None
