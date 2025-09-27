# backend/filesharehub_v2/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Ortam değişkeni tanımı (geliştirme ortamına göre ayarlanabilir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sapreports.settings")


app = Celery("filesharehub_v2")

# Django ayarlarını Celery'e yükle
app.config_from_object("django.conf:settings", namespace="CELERY")

# Görevleri otomatik keşfet
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

# Günlük saat 04:00'te fix_thumbnails görevini çalıştır
app.conf.beat_schedule = {
    "fix-thumbnails-daily": {
        "task": "filesharehub_v2.tasks.fix_thumbnails_task.run_fix_thumbnails",
        "schedule": crontab(hour=4, minute=0),
    },
}
