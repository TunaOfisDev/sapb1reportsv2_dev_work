# path: backend/report_orchestrator/tasks/run_report.py

import time
import requests
import logging
from celery import shared_task
from django.utils.timezone import now

from report_orchestrator.models.api_report_model import APIReportModel
from report_orchestrator.models.api_execution_log import APIExecutionLog
from report_orchestrator.rules.rule_engine import apply_rules
from report_orchestrator.utils.time_utils import now_tr
from report_orchestrator.utils.lock_utils import TaskLock
from mailservice.other_api.report_orchestrator.api_name_loader import load_mail_service_for_report
from mailservice.services.report_orchestrator.system_alert_service import SystemAlertService

logger = logging.getLogger(__name__)

DEFAULT_RETRY_ATTEMPTS = 2
DEFAULT_RETRY_INTERVAL = 60
LOCK_TIMEOUT = 300  # saniye

@shared_task(bind=True, name="report_orchestrator.tasks.run_report", max_retries=5)
def run_report(self, api_name: str):
    start_time = time.time()
    status = "SUCCESS"
    error_msg = ""
    result_json = {}
    report = None

    lock = TaskLock(api_name, timeout=LOCK_TIMEOUT)
    if not lock.acquire():
        logger.warning(f"[LOCKED] {api_name} için aktif görev zaten çalışıyor. İşlem atlandı.")
        return

    try:
        report = APIReportModel.objects.get(api_name=api_name)
        rule = report.rule_json or {}
        retry_attempts = rule.get("retry_attempts", DEFAULT_RETRY_ATTEMPTS)
        retry_interval = rule.get("retry_interval", DEFAULT_RETRY_INTERVAL)

        response = requests.get(report.data_pull_url)
        response.raise_for_status()
        raw_data = response.json()

        processed = apply_rules(raw_data, rule)

        if not processed["filtered_data"]:
            raise ValueError("Boş veri kümesi döndü. Rapor başarısız olarak işaretlenecek.")

        result_json = {
            "report_date": now_tr().strftime('%Y-%m-%d %H:%M'),
            "data": processed["filtered_data"],
            "totals": processed["totals"]
        }

        report.result_json = result_json
        report.last_error_message = ""
        report.last_run_at = now()
        report.save()

        MailServiceClass = load_mail_service_for_report(report.api_name)
        if MailServiceClass:
            context = {
                "report_title": rule.get("title", "Özet Rapor"),
                "report_date": result_json.get("report_date"),
                "columns": list(result_json["data"][0].keys()) if result_json["data"] else [],
                "data": result_json["data"],
                "subtotal": result_json.get("totals", {}).get("subtotal", {}),
                "cumulative_total": result_json.get("totals", {}).get("cumulative", {})
            }
            MailServiceClass().send_mail(context, result_json.get("report_date"))

    except Exception as e:
        status = "FAILED"
        error_msg = str(e)

        if report:
            retry_attempts = rule.get("retry_attempts", DEFAULT_RETRY_ATTEMPTS)
            retry_interval = rule.get("retry_interval", DEFAULT_RETRY_INTERVAL)

            if self.request.retries < retry_attempts:
                logger.warning(f"[RETRY] {api_name} - {error_msg} - {self.request.retries + 1}/{retry_attempts}")
                raise self.retry(exc=e, countdown=retry_interval)

            logger.error(f"[MAIL ALERT] {api_name} - {error_msg}")
            SystemAlertService().send_alert(
                api_name=api_name,
                error_message=error_msg,
                report_context={
                    "report_title": rule.get("title", "Tanımsız"),
                    "failure_time": now_tr().strftime('%d.%m.%Y %H:%M'),
                    "retry_count": self.request.retries + 1,
                    "max_retries": retry_attempts
                }
            )
            report.last_error_message = error_msg
            report.last_run_at = now()
            report.save(update_fields=["last_error_message", "last_run_at"])

    finally:
        duration = int(time.time() - start_time)
        if report:
            APIExecutionLog.objects.create(
                api=report,
                status=status,
                error_message=error_msg,
                duration_seconds=duration
            )
        lock.release()
