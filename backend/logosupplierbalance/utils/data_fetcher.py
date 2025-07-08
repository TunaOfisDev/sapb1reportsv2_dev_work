# backend/logosupplierbalance/utils/data_fetcher.py
import requests
from django.conf import settings

def fetch_logo_db_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = 'http://10.130.212.112/api/v2/logodbcon/query/logosupplierbalance/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
    return None

