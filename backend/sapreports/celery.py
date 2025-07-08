# backend/sapreports/celery.py

from __future__ import absolute_import, unicode_literals
import os
import logging
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# Tüm Celery ve ilgili log kanallarını sadece ERROR seviyesinde tut
for logger_name in [
    'celery', 'celery.worker', 'celery.app.trace',
    'celery.redirected', 'kombu', 'amqp'
]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# Django'nun varsayılan ayarları için varsayılan modülü belirleyin.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

# Celery uygulamasını oluşturun.
app = Celery('sapreports')

# Django ayarlarını yükle.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django'nun tüm registered task modüllerini yükle.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Token oluşturmak için bir yardımcı fonksiyon
def get_or_create_token():
    from django.core.cache import cache
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import RefreshToken

    logger = logging.getLogger('celery')
    jwt_token = cache.get('jwt_token')
    if not jwt_token:
        User = get_user_model()
        try:
            system_user, created = User.objects.get_or_create(
                email='system@example.com',
                defaults={'is_active': True, 'is_staff': True}
            )
            if created:
                system_user.set_password('some-secure-password')
                system_user.save()
            refresh = RefreshToken.for_user(system_user)
            jwt_token = str(refresh.access_token)
            cache.set('jwt_token', jwt_token, 3600)
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            return None
    return jwt_token

@app.task
def periodic_task():
    import requests
    logger = logging.getLogger('celery')
    jwt_token = get_or_create_token()
    if jwt_token:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(f'http://{settings.SERVER_HOST}/api/v2/rawmaterialwarehousestock/fetch-hana-data/', headers=headers)
        if response.status_code == 200:
            logger.info('Periodic task completed successfully')
        else:
            logger.error(f'API request failed with status code: {response.status_code}')
    else:
        logger.error('Failed to obtain JWT token')

# --- TAKVİMLERİ BİRLEŞTİR ---
from report_orchestrator.config.celery_settings import CELERY_BEAT_SCHEDULE as REPORT_SCHEDULE

LOCAL_BEAT_SCHEDULE = {
    'scan-and-save-files-every-night': {
        'task': 'filesharehub.tasks.scan_and_save_files',
        'schedule': crontab(minute=0, hour=0),
    },
    'run-every-10-minutes': {
        'task': 'sapreports.celery.periodic_task',
        'schedule': 600.0,
    },

}

app.conf.beat_schedule = getattr(settings, "CELERY_BEAT_SCHEDULE", {}).copy()
app.conf.beat_schedule.update(REPORT_SCHEDULE)
app.conf.beat_schedule.update(LOCAL_BEAT_SCHEDULE)

