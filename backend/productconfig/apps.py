# backend/productconfig/apps.py
from django.apps import AppConfig

class ProductconfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productconfig'
    
    def ready(self):
        import productconfig.signals  # signals.py'yi import et