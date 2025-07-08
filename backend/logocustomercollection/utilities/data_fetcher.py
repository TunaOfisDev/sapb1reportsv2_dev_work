# backend/logocustomercollection/utilities/data_fetcher.py
import requests

def fetch_logo_db_data(token):
    """
    Logo ERP veritabanına ait logocustomercollection datasını çeken fonksiyon.
    Dış IP üzerinden tanımlı bir API'ye GET isteği atar.

    Parametre:
        token (str): JWT Bearer Token

    Dönüş:
        JSON (list[dict]) → Logo DB'den dönen veri seti
    """
    headers = {'Authorization': f'Bearer {token}'}
    url = 'http://10.130.212.112/api/v2/logodbcon/query/logocustomercollection/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
    return None
