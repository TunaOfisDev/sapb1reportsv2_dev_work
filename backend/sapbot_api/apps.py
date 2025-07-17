# backend/sapbot_api/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class SapbotApiConfig(AppConfig):
    """
    SAPBot API Application Configuration
    SAP Business One HANA ERP AI Support System
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sapbot_api'
    verbose_name = _('SAPBot API - SAP Business One AI Support')
    
    def ready(self):
        """
        Django app başlatılırken çalışacak initialization kodları
        """
        try:
            # Import signals
            from . import signals
            
            # System health check
            self._perform_startup_checks()
            
            # Cache warmup
            self._warmup_cache()
            
            # Initialize AI services
            self._initialize_ai_services()
            
            logger.info("✅ SAPBot API başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"❌ SAPBot API başlatma hatası: {e}")
            # Production'da hata varsa sistem dursun
            if not self._is_debug_mode():
                raise
    
    def _perform_startup_checks(self):
        """Sistem health check'leri"""
        from django.conf import settings
        from .utils.helpers import generate_hash
        
        # Required environment variables check
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(settings, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Eksik environment variables: {missing_vars}")
        
        # Database connection test
        try:
            from django.db import connection
            connection.ensure_connection()
            logger.info("✅ Database bağlantısı başarılı")
        except Exception as e:
            logger.error(f"❌ Database bağlantı hatası: {e}")
        
        # Redis connection test
        try:
            from django.core.cache import cache
            test_key = f"sapbot_startup_test_{generate_hash('test')[:8]}"
            cache.set(test_key, 'test', 60)
            cache.delete(test_key)
            logger.info("✅ Redis bağlantısı başarılı")
        except Exception as e:
            logger.error(f"❌ Redis bağlantı hatası: {e}")
    
    def _warmup_cache(self):
        """Critical cache'leri ön yükleme"""
        try:
            from .utils.cache_utils import warm_up_cache
            warm_up_cache()
            logger.info("✅ Cache warmup tamamlandı")
        except Exception as e:
            logger.warning(f"⚠️ Cache warmup hatası: {e}")
    
    def _initialize_ai_services(self):
        """AI servislerini initialize et"""
        try:
            from django.conf import settings
            
            # OpenAI API test
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                # Test connection without actual API call during startup
                logger.info("✅ OpenAI API key mevcut")
            else:
                logger.warning("⚠️ OpenAI API key bulunamadı")
            
            # Embedding service check
            sapbot_config = getattr(settings, 'SAPBOT_CONFIG', {})
            if sapbot_config.get('CACHE_EMBEDDINGS', True):
                logger.info("✅ Embedding cache aktif")
            
            # Language detection setup
            from .utils.text_processing import LanguageDetector
            test_result = LanguageDetector.detect_language("Test mesajı")
            logger.info(f"✅ Language detection test: {test_result}")
            
        except Exception as e:
            logger.warning(f"⚠️ AI services initialization hatası: {e}")
    
    def _is_debug_mode(self):
        """Debug mode check"""
        from django.conf import settings
        return getattr(settings, 'DEBUG', False)
    
    @staticmethod
    def get_version():
        """SAPBot API version"""
        return "1.0.0"
    
    @staticmethod
    def get_build_info():
        """Build bilgileri"""
        import os
        from datetime import datetime
        
        return {
            'version': SapbotApiConfig.get_version(),
            'build_date': datetime.now().isoformat(),
            'python_version': os.sys.version,
            'django_version': None,  # Will be filled by Django
            'environment': os.getenv('ENVIRONMENT', 'development'),
        }
    
    @staticmethod
    def get_system_info():
        """Sistem bilgileri"""
        import platform
        import psutil
        from django.conf import settings
        
        try:
            return {
                'platform': platform.platform(),
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'python_version': platform.python_version(),
                'sapbot_config': getattr(settings, 'SAPBOT_CONFIG', {}),
            }
        except Exception as e:
            logger.warning(f"Sistem bilgi alma hatası: {e}")
            return {'error': str(e)}