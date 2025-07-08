# backend/productconfig/utils/data_fetcher.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def fetch_hana_db_data(token, variant_code=None):
    try:
        if not token or not variant_code:
            logger.debug("Token veya Variant Code eksik!")
            return {"success": False, "error": "Token veya variant code eksik"}

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/query_variant_status_hana_db/'
        params = {'variant_code': variant_code}

        logger.debug(f"HANA sorgusu gönderiliyor: URL={url}, Headers={headers}, Params={params}")

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        logger.debug(f"HANA yanıt durumu: {response.status_code}")
        logger.debug(f"HANA yanıt içeriği: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.warning("HANA sorgusundan sonuç alınamadı.")
                return {"success": False, "error": "Veri bulunamadı"}

            item = data[0]
            return {
                "success": True,
                "data": {
                    "sap_item_code": item["ItemCode"],
                    "sap_item_description": item["ItemName"],
                    "sap_U_eski_bilesen_kod": item["U_eski_bilesene_kod"],
                    "sap_price": float(item["Price"]),
                    "sap_currency": item["Currency"]
                }
            }

    except Exception as e:
        logger.error(f"HANA sorgu hatası: {str(e)}")
        return {"success": False, "error": str(e)}
