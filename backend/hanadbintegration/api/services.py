# backend/hanadbintegration/api/services.py

import requests
from ..utils.hana_service_layer_config import HANADBServiceLayerConfig
from ..utils.exceptions import (
    HANADBIntegrationError,
    HANADBAuthenticationError,
    HANADBConnectionError,
    HANADBTimeoutError,
    HANADBDataValidationError
)
from ..utils.logs import log_hana_request, log_hana_error

class HANADBServiceLayer:
    """
    HANA DB Service Layer ile iletişimi yöneten servis sınıfı.
    - Oturum açma
    - Veri çekme (GET)
    - Veri ekleme (POST)
    - Veri güncelleme (PATCH)
    """

    def __init__(self):
        """HANA DB Service Layer ile bağlantıyı başlatır."""
        self.base_url = HANADBServiceLayerConfig.BASE_URL
        self.auth_payload = HANADBServiceLayerConfig.get_auth_payload()
        self.session_id = None  # HANA DB oturum ID

    def login(self):
        """
        HANA DB Service Layer'a oturum açar ve session ID alır.
        """
        url = f"{self.base_url}/Login"
        try:
            response = requests.post(url, json=self.auth_payload, timeout=HANADBServiceLayerConfig.TIMEOUT)
            log_hana_request("POST", url, response.status_code, response.json())

            if response.status_code == 200:
                self.session_id = response.json().get("SessionId")
                return self.session_id
            elif response.status_code == 401:
                raise HANADBAuthenticationError()
            else:
                raise HANADBIntegrationError("HANA oturum açma başarısız!", response.status_code, response.json())

        except requests.ConnectionError:
            log_hana_error("HANA bağlantı hatası! Sunucuya ulaşılamıyor.")
            raise HANADBConnectionError()
        except requests.Timeout:
            log_hana_error("HANA isteği zaman aşımına uğradı!")
            raise HANADBTimeoutError()

    def get_data(self, endpoint):
        """
        HANA DB Service Layer'dan veri çeker (GET).
        """
        if not self.session_id:
            self.login()

        url = f"{self.base_url}/{endpoint}"
        headers = HANADBServiceLayerConfig.get_headers(self.session_id)

        try:
            response = requests.get(url, headers=headers, timeout=HANADBServiceLayerConfig.TIMEOUT)
            log_hana_request("GET", url, response.status_code, response.json())

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HANADBIntegrationError(f"HANA DB içinde '{endpoint}' verisi bulunamadı!", 404)
            else:
                raise HANADBIntegrationError("HANA GET işlemi başarısız!", response.status_code, response.json())

        except requests.ConnectionError:
            log_hana_error("HANA bağlantı hatası!")
            raise HANADBConnectionError()
        except requests.Timeout:
            log_hana_error("HANA isteği zaman aşımına uğradı!")
            raise HANADBTimeoutError()

    def post_data(self, endpoint, data):
        """
        HANA DB Service Layer'a yeni veri ekler (POST).
        """
        if not self.session_id:
            self.login()

        url = f"{self.base_url}/{endpoint}"
        headers = HANADBServiceLayerConfig.get_headers(self.session_id)

        try:
            response = requests.post(url, headers=headers, json=data, timeout=HANADBServiceLayerConfig.TIMEOUT)
            log_hana_request("POST", url, response.status_code, response.json())

            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 400:
                raise HANADBDataValidationError(response_data=response.json())
            else:
                raise HANADBIntegrationError("HANA POST işlemi başarısız!", response.status_code, response.json())

        except requests.ConnectionError:
            log_hana_error("HANA bağlantı hatası!")
            raise HANADBConnectionError()
        except requests.Timeout:
            log_hana_error("HANA isteği zaman aşımına uğradı!")
            raise HANADBTimeoutError()

    def patch_data(self, endpoint, data):
        """
        HANA DB Service Layer'da var olan veriyi günceller (PATCH).
        """
        if not self.session_id:
            self.login()

        url = f"{self.base_url}/{endpoint}"
        headers = HANADBServiceLayerConfig.get_headers(self.session_id)

        try:
            response = requests.patch(url, headers=headers, json=data, timeout=HANADBServiceLayerConfig.TIMEOUT)
            log_hana_request("PATCH", url, response.status_code, response.json())

            if response.status_code in [200, 204]:
                return response.json()
            elif response.status_code == 400:
                raise HANADBDataValidationError(response_data=response.json())
            else:
                raise HANADBIntegrationError("HANA PATCH işlemi başarısız!", response.status_code, response.json())

        except requests.ConnectionError:
            log_hana_error("HANA bağlantı hatası!")
            raise HANADBConnectionError()
        except requests.Timeout:
            log_hana_error("HANA isteği zaman aşımına uğradı!")
            raise HANADBTimeoutError()
