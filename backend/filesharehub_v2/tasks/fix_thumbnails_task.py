# backend/filesharehub_v2/tasks/fix_thumbnails_task.py
import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger('filesharehub')

@shared_task(bind=True, max_retries=2)
def run_fix_thumbnails(self):
    try:
        call_command("fix_thumbnails")
    except Exception as e:
        logger.error(f"fix_thumbnails komutu hata verdi: {e}")
        raise self.retry(countdown=60)
