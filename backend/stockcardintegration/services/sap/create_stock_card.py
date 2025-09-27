# backend/stockcardintegration/services/sap/create_stock_card.py

import requests
from django.conf import settings
from stockcardintegration.models.models import StockCard
from hanadbintegration.utils.hana_service_layer_config import HANADBServiceLayerConfig
from stockcardintegration.utils.logs import log_stockcard_request, log_stockcard_error
from stockcardintegration.utils.exceptions import StockCardIntegrationError
from stockcardintegration.services.formatters.stockcard_formatter import build_sap_stock_card_payload
from celery import shared_task

@shared_task(bind=True)
def send_stock_card_to_hanadb(self, stock_card_id, skip_email=True):
    response = None
    stock_card = None
    try:
        stock_card = StockCard.objects.get(id=stock_card_id)

        if stock_card.hana_status == "completed":
            log_stockcard_request("SKIP", "SAP Gönderim Atlandı", 0, f"{stock_card.item_code} zaten gönderilmiş.")
            return {"message": "Bu stok kartı zaten SAP'ya başarıyla gönderilmiş."}

        hana_url = HANADBServiceLayerConfig.get_hanadbintegration_url()
        payload = build_sap_stock_card_payload(stock_card)

        # Login
        log_stockcard_request("LOGIN", f"{HANADBServiceLayerConfig.BASE_URL}/Login", 0, "Login başlatılıyor")
        auth_payload = HANADBServiceLayerConfig.get_auth_payload()
        auth_response = requests.post(
            f"{HANADBServiceLayerConfig.BASE_URL}/Login",
            json=auth_payload,
            timeout=HANADBServiceLayerConfig.TIMEOUT,
            verify=HANADBServiceLayerConfig.TLS_VERIFY
        )

        if auth_response.status_code != 200:
            log_stockcard_error(f"LOGIN HATASI: {auth_response.status_code} | {auth_response.text}")
            raise StockCardIntegrationError("SAP HANA oturum açma başarısız")

        session_id = auth_response.json().get("SessionId")
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"B1SESSION={session_id}"
        }

        # POST to SAP
        log_stockcard_request("POST", hana_url, 0, f"POST verisi: {payload}")
        response = requests.post(
            hana_url,
            json=payload,
            headers=headers,
            timeout=HANADBServiceLayerConfig.TIMEOUT,
            verify=HANADBServiceLayerConfig.TLS_VERIFY
        )

        log_stockcard_request("POST", hana_url, response.status_code, response.text)

        if response.status_code in [200, 201]:
            stock_card.mark_as_synced()
            return response.json()
        else:
            stock_card.mark_as_failed()
            raise StockCardIntegrationError(f"HANA DB hata: {response.text}")

    except StockCard.DoesNotExist:
        log_stockcard_error(f"Stok kartı bulunamadı: ID {stock_card_id}")
        raise StockCardIntegrationError("Stok kartı bulunamadı")

    except requests.RequestException as req_err:
        error_msg = f"İstek hatası: {str(req_err)}"
        log_stockcard_error(error_msg)
        raise StockCardIntegrationError(error_msg)

    except Exception as ex:
        error_msg = f"Genel SAP hatası: {str(ex)}"
        log_stockcard_error(error_msg)
        raise StockCardIntegrationError(error_msg)
