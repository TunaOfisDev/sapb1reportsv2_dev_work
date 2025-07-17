# backend/sapreports/logger_settings.py - SAPBot logger'larını ekle

import os
from pathlib import Path

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
       # SAPBot özel formatter
       'sapbot': {
           'format': '[SAPBot] {asctime} - {name} - {levelname} - {message}',
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
           'filters': ['suppress_worker_lost'],
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
       'filesharehubv2': {
           'level': 'ERROR',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'filesharehubv2.log'),
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
       # ═══════════════ SAPBot Logger'ları ═══════════════
       'sapbot_main': {
           'level': 'ERROR',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'sapbot.log'),
           'formatter': 'sapbot',
           'maxBytes': 5 * 1024 * 1024,  # 5MB
           'backupCount': 3,
       },
       'sapbot_error': {
           'level': 'ERROR',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'sapbot_errors.log'),
           'formatter': 'sapbot',
           'maxBytes': 10 * 1024 * 1024,  # 10MB
           'backupCount': 5,
       },
       'sapbot_chat': {
           'level': 'ERROR',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'sapbot_chat.log'),
           'formatter': 'sapbot',
           'maxBytes': 5 * 1024 * 1024,  # 5MB
           'backupCount': 3,
       },
       'sapbot_tasks': {
           'level': 'ERROR',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'sapbot_tasks.log'),
           'formatter': 'sapbot',
           'maxBytes': 10 * 1024 * 1024,  # 10MB
           'backupCount': 5,
       },
       'sapbot_security': {
           'level': 'WARNING',  # Security için WARNING level
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'sapbot_security.log'),
           'formatter': 'sapbot',
           'maxBytes': 5 * 1024 * 1024,  # 5MB
           'backupCount': 10,  # Security log'ları daha uzun sakla
       },
       'sapbot_analytics': {
           'level': 'ERROR',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.path.join(LOG_DIR, 'sapbot_analytics.log'),
           'formatter': 'sapbot',
           'maxBytes': 5 * 1024 * 1024,  # 5MB
           'backupCount': 3,
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
       'filesharehub_v2': {
           'handlers': ['filesharehubv2'],
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
       # ═══════════════ SAPBot Logger'ları ═══════════════
       'sapbot_api': {
           'handlers': ['sapbot_main', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.chat': {
           'handlers': ['sapbot_chat', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.tasks': {
           'handlers': ['sapbot_tasks', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.tasks.document_processing': {
           'handlers': ['sapbot_tasks', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.tasks.embedding_tasks': {
           'handlers': ['sapbot_tasks', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.tasks.chat_analytics': {
           'handlers': ['sapbot_analytics', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.tasks.system_maintenance': {
           'handlers': ['sapbot_tasks', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.security': {
           'handlers': ['sapbot_security', 'sapbot_error'],
           'level': 'WARNING',  # Security için WARNING
           'propagate': False,
       },
       'sapbot_api.middleware': {
           'handlers': ['sapbot_main', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.ai': {
           'handlers': ['sapbot_main', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.search': {
           'handlers': ['sapbot_main', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.views': {
           'handlers': ['sapbot_main', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
       'sapbot_api.serializers': {
           'handlers': ['sapbot_main', 'sapbot_error'],
           'level': 'ERROR',
           'propagate': False,
       },
   }
}