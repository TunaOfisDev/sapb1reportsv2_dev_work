# /var/www/sapb1reportsv2/backend/totalrisk/utilities/chatgpt_conn.py
import requests
from django.conf import settings

def analyze_total_risk_data(report_data):
    api_key = settings.OPENAI_API_KEY
    url = f"http://{settings.SERVER_HOST}/api/v2/chatgpt/analysis/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "report_data": report_data
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            response_json = response.json()
            return response_json.get('analysis', '')
        except ValueError as e:
            print(f"JSON decode error: {e}")
            return None
    else:
        print(f"Hata: {response.status_code}, Mesaj: {response.text}")
        return None
