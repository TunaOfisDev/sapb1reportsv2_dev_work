# backend/sapreports/logger_settings.py

import os
from pathlib import Path

# Ortam değişkenine göre temel log seviyesini belirle
# Production'da sadece önemli bilgileri (INFO ve üstü) logla
# Development'ta ise tüm detayları (DEBUG ve üstü) gör
LOG_LEVEL = 'INFO' if os.environ.get('ENVIRONMENT') == 'production' else 'DEBUG'

# BASE_DIR projenin kök dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# Log klasörü tanımı ve oluşturulması
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# ───────────── LOGGING AYARI (Yalnızca ERROR) ─────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname} {asctime} [{name}] {message}',
            'style': '{',
        },
    },
        'filters': {
        'suppress_worker_lost': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'WorkerLostError' not in str(record.getMessage()),
        },
    
    },
    'handlers': {
        'sapreports': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'sapreports.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'celery': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'celery.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
            'filters': ['suppress_worker_lost'], # İki tanımı birleştirin
        },
        'hanadb': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'hanadb.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'productconfig': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'productconfig.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'report_orchestrator': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'report_orchestrator.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'backend': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'backend.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'celerybeat': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'celerybeat.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'gunicorn.error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'gunicorn-error.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },

        'taskorchestrator_handler': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'taskorchestrator.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'procure_compare': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'procure_compare.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
        },
        'celery': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'celery.log'),
            'formatter': 'standard',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 0,
            'filters': ['suppress_worker_lost'],  # ⬅️ ekle
        },

    },
    'loggers': {
        'django': {
            'handlers': ['sapreports'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery': {
            'handlers': ['celery'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery.worker': {
            'handlers': ['celery'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery.app.trace': {
            'handlers': ['celery'],
            'level': 'ERROR',
            'propagate': False,
        },
        'hanadbcon.models.hanadb_model': {
            'handlers': ['hanadb'],
            'level': 'ERROR',
            'propagate': False,
        },
        'backend.productconfig': {
            'handlers': ['productconfig'],
            'level': 'ERROR',
            'propagate': False,
        },
        'report_orchestrator': {
            'handlers': ['report_orchestrator'],
            'level': 'ERROR',
            'propagate': False,
        },
        'backend': {
            'handlers': ['backend'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celerybeat': {
            'handlers': ['celerybeat'],
            'level': 'ERROR',
            'propagate': False,
        },
        'gunicorn.error': {
            'handlers': ['gunicorn.error'],
            'level': 'ERROR',
            'propagate': False,
        },

        'taskorchestrator': {
            'handlers': ['taskorchestrator_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
        'procure_compare': {
            'handlers': ['procure_compare'],
            'level': 'ERROR',
            'propagate': False,
        },


    }
}
