# path: backend/stockcardintegration/services/sap/get_item_from_sap.py

import requests
from hanadbintegration.utils.hana_service_layer_config import HANADBServiceLayerConfig
from stockcardintegration.utils.logs import log_stockcard_request, log_stockcard_error
from stockcardintegration.utils.exceptions import StockCardIntegrationError

def get_item_from_sap(item_code: str) -> dict:
    try:
        # 1. Login to SAP
        login_url = f"{HANADBServiceLayerConfig.BASE_URL}/Login"
        auth_payload = HANADBServiceLayerConfig.get_auth_payload()

        log_stockcard_request("LOGIN", login_url, 0, "Login başlatılıyor")

        auth_response = requests.post(
            login_url,
            json=auth_payload,
            timeout=HANADBServiceLayerConfig.TIMEOUT,
            verify=HANADBServiceLayerConfig.TLS_VERIFY
        )

        if auth_response.status_code != 200:
            log_stockcard_error(f"SAP LOGIN HATASI: {auth_response.status_code} | {auth_response.text}")
            raise StockCardIntegrationError("SAP oturum açma başarısız!")

        session_id = auth_response.json().get("SessionId")
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"B1SESSION={session_id}"
        }

        # 2. GET Item from SAP
        item_url = f"{HANADBServiceLayerConfig.BASE_URL}/Items('{item_code}')"
        log_stockcard_request("GET", item_url, 0, f"ItemCode: {item_code}")

        item_response = requests.get(
            item_url,
            headers=headers,
            timeout=HANADBServiceLayerConfig.TIMEOUT,
            verify=HANADBServiceLayerConfig.TLS_VERIFY
        )

        log_stockcard_request("GET", item_url, item_response.status_code, item_response.text)

        if item_response.status_code == 200:
            return item_response.json()

        raise StockCardIntegrationError(f"SAP GET hatası: {item_response.status_code} - {item_response.text}")

    except requests.RequestException as req_err:
        error_msg = f"İstek hatası: {str(req_err)}"
        log_stockcard_error(error_msg)
        raise StockCardIntegrationError(error_msg)

    except Exception as ex:
        error_msg = f"SAP veri çekme hatası: {str(ex)}"
        log_stockcard_error(error_msg)
        raise StockCardIntegrationError(error_msg)
