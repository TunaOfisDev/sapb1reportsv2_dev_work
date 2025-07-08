# backend/bomcostmanager/connect/bomproduct_data_fetcher.py

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def fetch_hana_db_data(token):
    """
    SAP HANA DB'den BOM ürün verisini çekmek için sorguyu tetikler.
    
    Args:
        token (str): SAP HANA API erişim token'ı.
    
    Returns:
        dict veya list: HANA DB'den dönen JSON verisi, hata durumunda None.
    """
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/bomproduct/'
    logger.debug("BOMProduct sorgusu URL: %s, Headers: %s", url, headers)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        logger.debug("BOMProduct sorgusuna yanıt: %s", response.status_code)
        if response.status_code == 200:
            data = response.json()
            logger.info("SAP HANA'dan BOMProduct verisi çekildi, kayıt sayısı: %d", len(data) if hasattr(data, '__len__') else 1)
            return data
        else:
            logger.error("HANA BOMProduct sorgusunda hata: %s, Mesaj: %s", response.status_code, response.text)
    except Exception as e:
        logger.exception("BOMProduct verisi çekilirken istisna oluştu: %s", e)
    return None
