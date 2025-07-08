# backend/taskorchestrator/utils/logger_config.py

import os
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings

# 🔐 Log klasörü kontrolü
LOG_DIR = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 📄 TaskOrchestrator log dosyası
TASKORCH_LOG_FILE = os.path.join(LOG_DIR, 'taskorchestrator.log')

# 🧱 Formatter
formatter = logging.Formatter(
    fmt='ERROR {asctime} [{name}] {message}',
    style='{'
)

# 🔁 RotatingFileHandler – 1 MB sınır, yedek yok
handler = RotatingFileHandler(
    TASKORCH_LOG_FILE,
    maxBytes=1 * 1024 * 1024,
    backupCount=0
)
handler.setLevel(logging.ERROR)
handler.setFormatter(formatter)

# 🧠 Logger – modül genelini kapsar
logger = logging.getLogger("taskorchestrator")
logger.setLevel(logging.ERROR)
logger.addHandler(handler)
logger.propagate = False  # başka loglara sızmasın
