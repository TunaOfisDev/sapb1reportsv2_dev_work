# File: backend/report_orchestrator/services/task_retry_service.py

import traceback
from celery import Task
from report_orchestrator.logging.report_logger import log_report_error
from mailservice.utils.report_failure_notifier import notify_report_failure


class ReportTaskRetryHandler:
    """
    Rapor çalıştırma görevleri için yeniden deneme (retry) ve 
    son başarısızlık durumunda sistem yöneticisini uyarma servisidir.
    """

    def __init__(self, task: Task, api_name: str, max_retries: int = 3):
        """
        :param task: Celery görevi (self parametresi)
        :param api_name: İlgili raporun api_name değeri
        :param max_retries: Maksimum yeniden deneme sayısı
        """
        self.task = task
        self.api_name = api_name
        self.max_retries = max_retries

    def handle_failure(self, exc: Exception, context: dict = None):
        """
        Görev hata aldığında çağrılır. Otomatik olarak retry yapar.
        Tüm denemeler tükenirse uyarı maili gönderir.
        """
        retry_count = self.task.request.retries
        error_msg = str(exc)
        trace = traceback.format_exc()

        # Hatalı loglama
        log_report_error(api_name=self.api_name, error_message=error_msg, traceback_text=trace)

        if retry_count < self.max_retries:
            # Bir dakika sonra yeniden dene
            raise self.task.retry(exc=exc, countdown=60)
        else:
            # Tüm denemeler başarısız olduysa bilgi sistemine uyarı gönder
            notify_report_failure(
                api_name=self.api_name,
                error_message=trace,
                report_context=context or {}
            )
            return False

