# backend/stockcardintegration/utils/logs.py
import logging
import os
from django.conf import settings

# Log klasörü ve dosya yollarını belirle
LOG_DIR = os.path.join(settings.BASE_DIR, "logs")  # "backend" ekini kaldırdık
STOCKCARD_LOG_FILE = os.path.join(LOG_DIR, "stockcard_integration.log")

# Log klasörü yoksa oluştur
os.makedirs(LOG_DIR, exist_ok=True)

# Logger'ı oluştur
logger = logging.getLogger("stockcard_integration")
logger.setLevel(logging.DEBUG)

# Log formatı
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)

# Dosya log handler
file_handler = logging.FileHandler(STOCKCARD_LOG_FILE)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Konsol log handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Logger'a handler'ları ekle
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_stockcard_request(request_type, endpoint, response_status, response_data=None):
    """
    Stock Card API çağrılarını loglama fonksiyonu.
    - request_type: "GET", "POST", "PATCH" gibi HTTP metodunu belirtir.
    - endpoint: API uç noktası.
    - response_status: HTTP yanıt kodu.
    - response_data: Opsiyonel, dönen yanıt.
    """
    log_message = f"StockCard {request_type} {endpoint} | Status: {response_status}"
    if response_data:
        log_message += f" | Response: {response_data}"
    
    if response_status >= 400:
        logger.error(log_message)
    else:
        logger.info(log_message)

def log_stockcard_error(error_message):
    """
    Stock Card API ile ilgili hataları loglama fonksiyonu.
    """
    logger.error(f"StockCard Hata: {error_message}")