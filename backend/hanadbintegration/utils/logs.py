# backend/hanadbintegration/utils/logs.py
import logging
import os
from django.conf import settings

# Log klasörünü doğrudan settings.LOG_DIR üzerinden tanımla
LOG_DIR = getattr(settings, "LOG_DIR", os.path.join(settings.BASE_DIR, "logs"))
HANA_LOG_FILE = os.path.join(LOG_DIR, "hanadb_integration.log")

# Log klasörü yoksa oluştur
os.makedirs(LOG_DIR, exist_ok=True)

# Logger'ı oluştur
logger = logging.getLogger("hanadb_integration")
logger.setLevel(logging.DEBUG)

# Tekrar log handler eklenmesini önle (dev server'da reload hatasını engeller)
if not logger.hasHandlers():
    # Log formatı
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )

    # Dosya handler
    file_handler = logging.FileHandler(HANA_LOG_FILE)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Konsol handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Handler'ları logger'a bağla
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_hana_request(request_type, endpoint, response_status, response_data=None):
    """
    HANA DB API çağrılarını loglar.
    """
    log_message = f"HANA {request_type} {endpoint} | Status: {response_status}"
    if response_data:
        log_message += f" | Response: {response_data}"
    
    if response_status >= 400:
        logger.error(log_message)
    else:
        logger.info(log_message)

def log_hana_error(error_message):
    """
    HANA DB hata mesajlarını loglar.
    """
    logger.error(f"HANA DB Hata: {error_message}")