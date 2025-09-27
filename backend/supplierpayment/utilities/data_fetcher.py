# backend/supplierpayment/utilities/data_fetcher.py
import requests
from django.conf import settings
from loguru import logger

def fetch_hana_db_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/supplierpayment/'
    try:
        response = requests.get(url, headers=headers, timeout=900)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"HANA DB hatası: {str(e)}, URL: {url}, Response: {response.text if 'response' in locals() else 'No response'}")
        return None