# backend/sapreports/__init__.py
from __future__ import absolute_import, unicode_literals

# .env yükle
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Celery yükle
from .celery import app as celery_app

__all__ = ('celery_app',)
