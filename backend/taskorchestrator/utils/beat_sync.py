# backend/taskorchestrator/utils/beat_sync.py

from django_celery_beat.models import PeriodicTask
from taskorchestrator.models.scheduled_task import ScheduledTask
from django.utils import timezone
from taskorchestrator.utils.logger_config import logger  # 🔥 Merkezi log yapılandırması
import json


def sync_from_db():
    """
    ScheduledTask kayıtlarını django-celery-beat ile senkronize eder.
    Enabled = False olan kayıtlar silinir.
    Hatalar dışında log kaydı tutulmaz.
    """
    try:
        existing_tasks = {
            pt.name: pt for pt in PeriodicTask.objects.filter(name__startswith="taskorchestrator:")
        }

        active_tasks = ScheduledTask.objects.filter(enabled=True)

        for task in active_tasks:
            try:
                task_name = f"taskorchestrator:{task.name}"

                task_kwargs = {
                    "task_id": task.id
                }

                PeriodicTask.objects.update_or_create(
                    name=task_name,
                    defaults={
                        "task": "taskorchestrator.tasks.run_scheduled_task",
                        "crontab": task.crontab,
                        "enabled": True,
                        "args": json.dumps([]),
                        "kwargs": json.dumps(task_kwargs),
                        "description": task.notes or f"{task.task.name} görevi",
                        "start_time": timezone.now()
                    }
                )

                existing_tasks.pop(task_name, None)

            except Exception as e:
                logger.exception(f"❌ Görev senkronizasyon hatası: {task.name} - {str(e)}")

        # Orphan görevleri temizle
        for orphan_name, orphan_task in existing_tasks.items():
            try:
                orphan_task.delete()
            except Exception as e:
                logger.exception(f"❌ Orphan görev silinirken hata: {orphan_name} - {str(e)}")

    except Exception as e:
        logger.exception(f"🔥 Genel beat_sync senkronizasyon hatası: {str(e)}")
