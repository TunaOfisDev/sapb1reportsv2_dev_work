# backend/sapbot_api/tasks/maintenance_schedule.py

"""
Sadece Celery beat ayarlarını içerir – **MODELS İÇE AKTARMA!**
"""
from celery.schedules import crontab

MAINTENANCE_TASKS = {
    # örnek: her gece 03:00’de eski logları sil
    "clear_old_logs": {
        "task": "sapbot_api.tasks.maintenance_tasks.clear_old_logs",
        "schedule": crontab(minute=0, hour=3),
        "options": {"queue": "maintenance"},
    },
    # burada başka görevler...
}
