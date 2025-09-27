# backend/salesofferdocsum/utilities/data_fetcher.py
import requests
from django.conf import settings

def fetch_hana_db_data(token, last_update=None):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/salesofferdocsum/'
    if last_update:
        url += f'?last_update={last_update.isoformat()}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
    return None