# backend/filesharehub_v2/tasks/fix_thumbnails_task.py
from celery import shared_task
from django.core.management import call_command

@shared_task(bind=True, max_retries=2)
def run_fix_thumbnails(self):
    """
    Django'nun 'fix_thumbnails' yönetim komutunu çalıştırır.
    Bu sürümde loglama kaldırılmıştır. Hatalar konsola yazdırılır.
    """
    try:
        call_command("fix_thumbnails")
    except Exception as e:
        # Hata log dosyası yerine konsola yazdırılır.
        print(f"[FixThumbnails-Task-Error] 'fix_thumbnails' komutu hata verdi: {e}")
        # Görevin yeniden denenmesi için hata fırlatılır.
        raise self.retry(exc=e, countdown=60)