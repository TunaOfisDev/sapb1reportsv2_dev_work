# backend/tunainssupplierpayment/utilities/data_fetcher.py
import requests
from django.conf import settings
from loguru import logger

def fetch_hana_db_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/tunainssupplierpayment/'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data from HANA DB: {str(e)}")
        logger.error(f"Response content: {response.text}")
        return None