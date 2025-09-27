# backend/stockcardintegration/services/sap/update_stock_card.py

import requests
import os
from django.conf import settings
from stockcardintegration.models.models import StockCard
from hanadbintegration.utils.hana_service_layer_config import HANADBServiceLayerConfig
from stockcardintegration.utils.logs import log_stockcard_request, log_stockcard_error
from stockcardintegration.utils.exceptions import StockCardIntegrationError
from stockcardintegration.services.formatters.stockcard_formatter import build_sap_stock_card_payload
from stockcardintegration.services.mail.send_stockcard_summary_email import send_stockcard_summary_email

os.environ["REQUESTS_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"

def update_stock_card_on_hanadb(stock_card_id):
    try:
        stock_card = StockCard.objects.get(id=stock_card_id)
        hana_url = f"{HANADBServiceLayerConfig.get_hanadbintegration_url()}('{stock_card.item_code}')"
        payload = build_sap_stock_card_payload(stock_card)

        log_stockcard_request("LOGIN", f"{HANADBServiceLayerConfig.BASE_URL}/Login", 0, "Login başlatılıyor")
        auth_payload = HANADBServiceLayerConfig.get_auth_payload()
        auth_response = requests.post(
            f"{HANADBServiceLayerConfig.BASE_URL}/Login",
            json=auth_payload,
            timeout=HANADBServiceLayerConfig.TIMEOUT,
            verify=HANADBServiceLayerConfig.get_verify_tls()
        )

        if auth_response.status_code != 200:
            log_stockcard_error(f"LOGIN HATASI: {auth_response.status_code} | {auth_response.text}")
            raise StockCardIntegrationError("SAP HANA oturum açma başarısız")

        session_id = auth_response.json().get("SessionId")
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"B1SESSION={session_id}"
        }

        log_stockcard_request("PATCH", hana_url, 0, f"GÜNCELLEME verisi: {payload}")
        response = requests.patch(
            hana_url,
            json=payload,
            headers=headers,
            timeout=HANADBServiceLayerConfig.TIMEOUT,
            verify=HANADBServiceLayerConfig.get_verify_tls()
        )

        log_stockcard_request("PATCH", hana_url, response.status_code, response.text)

        if response.status_code in [200, 204]:
            stock_card.mark_as_synced()
            return response.json() if response.content else {"status": "updated"}
        else:
            stock_card.mark_as_failed()
            raise StockCardIntegrationError(f"SAP HANA güncelleme hatası: {response.text}")

    except StockCard.DoesNotExist:
        raise StockCardIntegrationError("Stok kartı bulunamadı")

    except requests.RequestException as req_err:
        error_msg = f"İstek hatası: {str(req_err)}"
        log_stockcard_error(error_msg)
        raise StockCardIntegrationError(error_msg)

    except Exception as ex:
        error_msg = f"Genel SAP hatası: {str(ex)}"
        log_stockcard_error(error_msg)
        raise StockCardIntegrationError(error_msg)

