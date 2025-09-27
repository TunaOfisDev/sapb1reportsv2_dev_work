# backend\dynamicreport\tests2.py
from django.test import TestCase
import requests

url = 'http://127.0.0.1:8000/api/v1/dynamicreport/format_value/'

data = {
    'type': 'decimal',
    'value': 1234.5678
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    formatted_value = result.get('formatted_value')
    print(f'Formatted Value: {formatted_value}')
else:
    print(f'Error: {response.status_code} - {response.text}')
