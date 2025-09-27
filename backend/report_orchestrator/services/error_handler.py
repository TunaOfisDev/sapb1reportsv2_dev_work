# backend/report_orchestrator/services/error_handler.py

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_failure_alert(api_name: str, error_message: str, extra_headers: dict = None):
    """
    Rapor çalıştırma sırasında oluşan hataları loglar ve sistem adminine e-posta ile bildirir.
    Mail gönderimi mailservice API üzerinden yapılır.
    """

    try:
        mail_payload = {
            "subject": f"[HATA] AI Center – Rapor Çalıştırılamadı: {api_name}",
            "body": (
                f"<h3 style='color:red;'>❌ Rapor Hatası: {api_name}</h3>"
                f"<p><strong>Hata Mesajı:</strong> {error_message}</p>"
                f"<p><em>Sunucu: {settings.SERVER_HOST}</em></p>"
                f"<p><strong>Extra Headers:</strong> {extra_headers}</p>"  # Yeni alan loglanıyor
            ),
            "recipients": ["itadmin@firma.com"]  # Ayarlanabilir hedef e-posta listesi
        }

        response = requests.post(
            f"{settings.SITE_URL}/api/v2/mailservice/send",
            json=mail_payload,
            timeout=10
        )

        if response.status_code == 200:
            logger.info(f"[send_failure_alert] Hata maili gönderildi: {api_name}")
        else:
            logger.warning(f"[send_failure_alert] Mail gönderimi başarısız: {response.status_code}")

    except Exception as ex:
        logger.error(f"[send_failure_alert] Hata maili gönderilemedi: {str(ex)}")

    # Her durumda loglama yap
    logger.error(f"[{api_name}] çalıştırılırken hata oluştu: {error_message}")
