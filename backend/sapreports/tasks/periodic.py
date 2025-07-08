# backend/sapreports/tasks/periodic.py

import logging
import requests
from celery import shared_task
from django.conf import settings
from sapreports.jwt_utils import get_or_create_jwt_token

logger = logging.getLogger('celery')

@shared_task
def periodic_task():
    """
    Her 10 dakikada bir çalışarak belirli bir API'den veri çeker.
    """
    jwt_token = get_or_create_jwt_token()
    if not jwt_token:
        logger.error('[PERIODIC TASK] JWT token alınamadı.')
        return

    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        url = f'http://{settings.SERVER_HOST}/api/v2/rawmaterialwarehousestock/fetch-hana-data/'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logger.info('[PERIODIC TASK] Veri çekme başarılı.')
        else:
            logger.error(f'[PERIODIC TASK] API başarısız: {response.status_code} - {response.text}')
    except Exception as e:
        logger.error(f'[PERIODIC TASK] İstek gönderilirken hata oluştu: {e}')

