# backend\dynamicreport\apps.py
from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class DynamicReportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dynamicreport'
    
    def ready(self):
        # Import your signals here
        autodiscover_modules('signals')
