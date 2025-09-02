# backend/customersales/utils/data_fetcher.py

import requests
from django.conf import settings

def fetch_raw_sales_data_from_hana(token):
    """
    HANA veritabanından ham satış verilerini çeker.
    Bu fonksiyon, referans alınan 'salesbudgeteur' yapısına göre güncellenmiştir.
    """
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/customersales_v2_data/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
    return None