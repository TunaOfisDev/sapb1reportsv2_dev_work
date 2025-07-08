# backend/report_orchestrator/tasks/run_all_reports_task.py

from celery import shared_task
from report_orchestrator.models.api_report_model import APIReportModel
from report_orchestrator.tasks.run_report import run_report
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_all_reports():
    """
    Sistemde tanımlı tüm aktif raporları çalıştırır.
    Her biri için ayrı Celery task tetikler (async).
    """
    reports = APIReportModel.objects.filter(is_active=True)
    total = reports.count()

    logger.info(f"[run_all_reports] Aktif {total} rapor sıraya alınıyor...")

    for report in reports:
        logger.info(f"[run_all_reports] {report.api_name} tetiklendi.")
        run_report.delay(report.api_name)
