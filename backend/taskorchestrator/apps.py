# backend/taskorchestrator/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class TaskorchestratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "taskorchestrator"

    def ready(self):
        from django.conf import settings
        if getattr(settings, "STARTUP_TASK_SYNC", False):
            post_migrate.connect(_sync_after_migrate, sender=self)

def _sync_after_migrate(**kwargs):
    from taskorchestrator.utils.beat_sync import sync_from_db
    sync_from_db()
