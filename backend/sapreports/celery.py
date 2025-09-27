# backend/sapreports/celery.py

from __future__ import absolute_import, unicode_literals
import os
import logging
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# BU BLOK SORUNA NEDEN OLUYORDU, YORUM SATIRI YAPILDI VEYA SİLİNDİ
# # Celery/kombu/amqp log seviyelerini düşür (isteğe bağlı)
# for logger_name in ['celery', 'celery.worker', 'celery.app.trace', 'celery.redirected', 'kombu', 'amqp']:
#     logging.getLogger(logger_name).setLevel(logging.ERROR)

# Django ayar modülü
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

# Celery app
app = Celery('sapreports')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Task autodiscovery
app.autodiscover_tasks()

# Basit debug task
@app.task(bind=True, name="sapreports.celery.debug_task")
def debug_task(self):
    return "ok"

# --- TAKVİMLERİ BİRLEŞTİR ---
from report_orchestrator.config.celery_settings import CELERY_BEAT_SCHEDULE as REPORT_SCHEDULE

LOCAL_BEAT_SCHEDULE = {
    'scan-and-save-files-every-night': {
        'task': 'filesharehub.tasks.scan_and_save_files',
        'schedule': crontab(minute=0, hour=0),
    },
    'run-every-10-minutes': {
        'task': 'sapreports.periodic_task',
        'schedule': 600.0,
    },
}

app.conf.beat_schedule = getattr(settings, "CELERY_BEAT_SCHEDULE", {}).copy()
app.conf.beat_schedule.update(REPORT_SCHEDULE)
app.conf.beat_schedule.update(LOCAL_BEAT_SCHEDULE)