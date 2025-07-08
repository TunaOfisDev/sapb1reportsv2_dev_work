# backend/report_orchestrator/services/result_saver.py

from django.utils.timezone import now
from report_orchestrator.models.api_report_model import APIReportModel
import logging

logger = logging.getLogger(__name__)

def save_result_json(api_name: str, result_json: dict):
    """
    İşlenmiş özet veriyi (result_json) APIReportModel'e yazar.
    Hata mesajını temizler, son çalıştırma zamanını günceller.
    """

    try:
        report = APIReportModel.objects.get(api_name=api_name)
        report.result_json = result_json
        report.last_error_message = ""
        report.last_run_at = now()
        
        # Yeni alanı kaydediyoruz
        if 'extra_headers' in result_json:
            report.extra_headers = result_json['extra_headers']
        
        report.save()

        logger.info(f"[save_result_json] Rapor kaydedildi: {api_name}")

    except APIReportModel.DoesNotExist:
        logger.error(f"[save_result_json] APIReportModel bulunamadı: {api_name}")

    except Exception as e:
        logger.error(f"[save_result_json] Hata oluştu: {str(e)}")
