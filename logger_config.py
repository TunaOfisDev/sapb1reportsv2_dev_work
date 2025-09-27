# backend/logger_config.py

from loguru import logger
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'backend.log')

logger.remove()  # Eski hedefleri sil

logger.add(
    LOG_FILE,
    level="ERROR",  # ← SADECE ERROR ve üstü loglar (WARNING, CRITICAL) yazılır
    rotation="1 MB",
    retention="3 hours",  # sadece kısa süreli tut
    compression=None,
    enqueue=True
)
