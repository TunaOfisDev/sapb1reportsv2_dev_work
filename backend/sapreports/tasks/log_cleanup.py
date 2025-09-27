# backend/sapreports/tasks/log_cleanup.py
import os
from celery import shared_task
from django.conf import settings

@shared_task
def clean_log_files():
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    for root, _, files in os.walk(log_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                if os.path.isfile(path):
                    with open(path, 'w'):
                        pass  # Dosya içeriğini temizle
            except Exception:
                pass
