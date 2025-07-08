# backend/hanadbintegration/utils/hana_service_layer_config.py

import environ
import os

# Ortam değişkenlerini yükle
env = environ.Env()
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)


class HANADBServiceLayerConfig:
    """
    HANA DB Service Layer için merkezi yapılandırma yöneticisi.
    """
    BASE_URL = env("SAP_SERVICE_LAYER_URL", default="https://10.131.212.112:50000/b1s/v1")
    COMPANY_DB = env("SAP_COMPANY_DB", default="TUNADB24TEST")
    USERNAME = env("SAP_USERNAME", default="manager")
    PASSWORD = env("SAP_PASSWORD", default="Eropa2018!")
    TIMEOUT = env.int("SAP_TIMEOUT", default=30)
    RETRY_COUNT = env.int("SAP_RETRY_COUNT", default=3)
    CERT_PATH = env("SAP_CERT_PATH", default="/etc/ssl/certs/sap_ca_bundle.crt")  
    TLS_VERIFY = env.bool("SAP_TLS_VERIFY", default=True)

    @classmethod
    def get_auth_payload(cls):
        return {
            "CompanyDB": cls.COMPANY_DB,
            "UserName": cls.USERNAME,
            "Password": cls.PASSWORD
        }

    @classmethod
    def get_headers(cls, session_id=None):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if session_id:
            headers["Cookie"] = f"B1SESSION={session_id}"
        return headers

    @classmethod
    def get_hanadbintegration_url(cls):
        return f"{cls.BASE_URL}/Items"

    @classmethod
    def get_verify_tls(cls):
        return cls.CERT_PATH if cls.TLS_VERIFY else False
