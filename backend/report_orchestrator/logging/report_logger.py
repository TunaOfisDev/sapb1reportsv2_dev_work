# backend/report_orchestrator/logging/report_logger.py
import logging

logger = logging.getLogger("django")  # ya da "sapreports" logger'ı kullanacaksan "django" yerine "sapreports"

def log_report_error(api_name: str, error_message: str, traceback_text: str = ""):
    logger.error(f"[{api_name}] Hata: {error_message}\nİz: {traceback_text}")
