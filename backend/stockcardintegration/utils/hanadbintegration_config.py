# backend/stockcardintegration/utils/hanadbintegration_config.py
import requests
from django.conf import settings
from ..models.models import StockCard
from ..utils.logs import log_stockcard_request, log_stockcard_error
from ..utils.exceptions import StockCardIntegrationError

class HANADBIntegrationConnector:
    """
    Stock Card Entegrasyonu için HANA DB Entegrasyon Merkezi ile bağlantı yöneticisi.
    - Hangi `HANADBIntegration` URL'sinin tetikleneceğini belirler.
    - Senkronizasyon durumunu günceller.
    """

    @staticmethod
    def get_hanadbintegration_url(integration_type="Stok Kart Entegrasyonu"):
        """
        Verilen `integration_type` için `HANADBIntegration` nesnesinin URL’sini getirir.
        """
        try:
            integration = StockCard.objects.get(integration_type=integration_type)
            return integration.external_api_url
        except StockCard.DoesNotExist:
            log_stockcard_error(f"{integration_type} için uygun HANA DB Entegrasyonu bulunamadı.")
            raise StockCardIntegrationError(f"{integration_type} için uygun HANA DB Entegrasyonu bulunamadı.", status_code=404)

    @staticmethod
    def trigger_hanadb_integration(stock_card_data):
        """
        Stock Card Entegrasyonu için ilgili `HANADBIntegration` URL’sini tetikler.
        """
        url = HANADBIntegrationConnector.get_hanadbintegration_url()
        
        try:
            response = requests.post(url, json=stock_card_data, timeout=30)
            log_stockcard_request("POST", url, response.status_code, response.json())

            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise StockCardIntegrationError("HANA DB Entegrasyonu başarısız!", response.status_code, response.json())

        except requests.ConnectionError:
            log_stockcard_error("HANA DB Entegrasyonu bağlantı hatası!")
            raise StockCardIntegrationError("HANA DB Entegrasyonu bağlantı hatası!", status_code=500)
        except requests.Timeout:
            log_stockcard_error("HANA DB Entegrasyonu zaman aşımı hatası!")
            raise StockCardIntegrationError("HANA DB Entegrasyonu zaman aşımı hatası!", status_code=408)
