# backend/activities/utilities/data_fetcher.py
import requests
from django.conf import settings

def fetch_hana_db_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/crmactivities/'
    try:
        response = requests.get(url, headers=headers, timeout=600)  # 10 dakikalık zaman aşımı
        response.raise_for_status()  # Bu, HTTP hatalarını otomatik olarak yakalar
        return response.json()
    except requests.exceptions.RequestException as e:
        # Hata işleme ve loglama
        print(f"Error fetching data from HANA DB: {e}")
        return None
