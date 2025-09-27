# backend/salesorder/utilities/data_fetcher.py
import requests
from django.conf import settings

def fetch_hana_db_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/salesorder/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
    return None


def fetch_hana_db_customersales(token):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/customersalesorder/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
    return None