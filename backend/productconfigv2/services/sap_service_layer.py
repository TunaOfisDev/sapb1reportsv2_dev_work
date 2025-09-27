# backend/productconfigv2/services/sap_service_layer.py
import requests
import json
from django.conf import settings
from decimal import Decimal

_session = None

def _login():
    """SAP Service Layer'a login olur ve session cookie'lerini döner."""
    global _session
    login_payload = {
        "CompanyDB": settings.SAP_COMPANY_DB,
        "UserName": settings.SAP_USERNAME,
        "Password": settings.SAP_PASSWORD,
    }
    login_url = f"{settings.SAP_SERVICE_LAYER_URL}/Login"
    response = requests.post(
        login_url, data=json.dumps(login_payload), 
        verify=settings.SAP_TLS_VERIFY, timeout=settings.SAP_TIMEOUT
    )
    response.raise_for_status()
    _session = response.cookies
    return response.cookies

def get_price_by_item_code(item_code: str, price_list: int = 1):
    """
    Verilen ürün koduna göre SAP Service Layer'dan fiyatı çeker.
    Başarılı olursa (True, fiyat), başarısız olursa (False, hata_mesajı) döner.
    """
    global _session
    try:
        session_cookies = _session or _login()
        
        # GÜNCELLEME: URL'i ItemPrices yerine doğrudan Items'a yapıyoruz. 
        # Service Layer, ItemPrices listesini otomatik olarak döndürür.
        item_url = f"{settings.SAP_SERVICE_LAYER_URL}/Items('{item_code}')"
        
        response = requests.get(
            item_url, cookies=session_cookies, 
            verify=settings.SAP_TLS_VERIFY, timeout=settings.SAP_TIMEOUT
        )
        
        if response.status_code == 401:
            session_cookies = _login()
            response = requests.get(item_url, cookies=session_cookies, verify=settings.SAP_TLS_VERIFY)

        if response.status_code != 200:
            error_message = f"SAP API Hatası: Status {response.status_code}, Yanıt: {response.text}"
            return False, error_message

        data = response.json()
        
        # GÜNCELLEME: İç içe olan doğru JSON yapısını burada işliyoruz.
        if 'ItemPrices' in data and isinstance(data['ItemPrices'], list):
            # PriceList'i bizim istediğimiz olan (varsayılan 1) fiyat objesini buluyoruz.
            price_entry = next((item for item in data['ItemPrices'] if item['PriceList'] == price_list), None)
            
            if price_entry and price_entry.get('Price') is not None:
                # Fiyatı bulduk, başarıyla döndürüyoruz.
                return True, Decimal(price_entry['Price'])

        # Eğer ItemPrices listesi veya içinde doğru fiyat bulunamazsa hata döndür.
        return False, f"Yanıt başarılı ancak aranan fiyata ulaşılamadı. Gelen yanıt: {data}"

    except requests.exceptions.RequestException as e:
        error_message = f"SAP Service Layer'a bağlanırken hata: {str(e)}"
        _session = None
        return False, error_message