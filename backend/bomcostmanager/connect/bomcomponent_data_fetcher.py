# backend/bomcostmanager/connect/bomcomponent_data_fetcher.py

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def fetch_hana_db_data(token, item_code=None):
    """
    SAP HANA DB'den BOM bileşen verisini çekmek için sorguyu tetikler.
    Eğer item_code parametresi gönderilirse, sorguya filtre olarak eklenir.
    
    Örnek:
        ?item_code=30.BW.A14070.M1.E1
    
    Args:
        token (str): SAP HANA API erişim token'ı.
        item_code (str, optional): Belirli bir ürün koduna göre filtreleme.
    
    Returns:
        dict veya list: HANA DB'den dönen JSON verisi, hata durumunda None.
    """
    headers = {'Authorization': f'Bearer {token}'}
    url = f'http://{settings.SERVER_HOST}/api/v2/hanadbcon/query/bomcomponent/'
    
    params = {}
    if item_code:
        params['item_code'] = item_code
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        logger.debug("BOMComponent sorgusu URL: %s, Params: %s", url, params)
        if response.status_code == 200:
            data = response.json()
            logger.info("SAP HANA'dan BOMComponent verisi çekildi, kayıt sayısı: %d", len(data) if hasattr(data, '__len__') else 1)
            return data
        else:
            logger.error("HANA BOMComponent sorgusunda hata: %s, Mesaj: %s", response.status_code, response.text)
    except Exception as e:
        logger.exception("BOMComponent verisi çekilirken istisna oluştu: %s", e)
    return None
