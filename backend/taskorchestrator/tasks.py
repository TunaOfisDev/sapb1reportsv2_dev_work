# backend/taskorchestrator/tasks.py

from celery import shared_task
from taskorchestrator.utils.dispatcher import run_task
from taskorchestrator.utils.logger_config import logger  # 🔥 Merkezi log kullanımı


@shared_task(bind=True, name="taskorchestrator.tasks.run_scheduled_task")
def run_scheduled_task(self, task_id: int):
    """
    Celery tarafından tetiklenen ana görev fonksiyonu.
    Verilen ScheduledTask ID'sine göre ilgili fonksiyonu çalıştırır.
    Sadece hata durumları loglanır.
    """
    try:
        run_task(task_id)
    except Exception as e:
        logger.exception(f"🔥 Celery run_scheduled_task hatası: {str(e)}")
