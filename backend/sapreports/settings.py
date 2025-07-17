from dotenv import load_dotenv
from pathlib import Path
from loguru import logger
from datetime import timedelta
from decouple import config
import os

from .spectacular_settings import SPECTACULAR_SETTINGS

load_dotenv()  # .env dosyasından ayarları yükler
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Ortam ayarları  -------------------------------------------------
ENVIRONMENT   = os.getenv('ENVIRONMENT', 'development')
SERVER_HOST   = os.getenv('SERVER_HOST', '127.0.0.1')
API_PORT      = os.getenv('INTERNAL_API_PORT', '8000')
SITE_URL      = f"http://{SERVER_HOST}:{API_PORT}"
# --------------------------------------------------------------------

# Local settings.py
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'sapbot_api', 'locale'),
]

""" 
LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
]
"""
LANGUAGE_CODE = 'tr'

LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = False
USE_TZ = False
USE_L10N = True
# sayısal format ###.###,##
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
USE_THOUSAND_SEPARATOR = True


ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()

SERVER_HOST ="192.168.2.124"

# hana servis
HANADB_HOST = os.getenv('HANADB_HOST')
HANADB_PORT = os.getenv('HANADB_PORT')
HANADB_USER = os.getenv('HANADB_USER')
HANADB_PASS = os.getenv('HANADB_PASS')
HANADB_SCHEMA = os.getenv('HANADB_SCHEMA')

# logo db servis
LOGO_DB_DSN = os.getenv('LOGO_DB_DSN')
LOGO_DB_HOST = os.getenv('LOGO_DB_HOST')
LOGO_DB_PORT = os.getenv('LOGO_DB_PORT')
LOGO_DB_USER = os.getenv('LOGO_DB_USER')
LOGO_DB_PASS = os.getenv('LOGO_DB_PASS')
LOGO_DB_NAME = os.getenv('LOGO_DB_NAME')



# eamil settings.py
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.yandex.ru")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "tunaapp@tunacelik.com.tr")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "tunaapp@tunacelik.com.tr")

# .env dosyasından veya doğrudan sabit bir değerden NETWORK_FOLDER_PATH alın
PRIMARY_PATH = os.getenv("NETWORK_FOLDER_PRIMARY")
FALLBACK_PATH = os.getenv("NETWORK_FOLDER_FALLBACK", "/mnt/product_picture")
NETWORK_FOLDER_PATH = PRIMARY_PATH if os.path.exists(PRIMARY_PATH) else FALLBACK_PATH

# settings.py heliosforgev2
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELIOS_STORAGE = {
    "BASE": os.path.join(BASE_DIR, "heliosforgev2", "storage"),
    "PDF": os.path.join(BASE_DIR, "heliosforgev2", "storage", "pdf"),
    "JSON": os.path.join(BASE_DIR, "heliosforgev2", "storage", "json"),
    "IMAGES": os.path.join(BASE_DIR, "heliosforgev2", "storage", "images"),
}

# API anahtarını .env dosyasından alın
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# YouTube API anahtarı ve playlis id
YOUTUBE_DATA_API_KEY = os.getenv('YOUTUBE_DATA_API_KEY')
YOUTUBE_PLAYLIST_ID =  os.getenv('YOUTUBE_PLAYLIST_ID')

# github api key systemnotebook api icin
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

ALLOWED_HOSTS = [
    SERVER_HOST,
    'localhost',
    '127.0.0.1',
]

# CORS ayarları
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Bunu False yapıyoruz

# Spesifik origin'leri listeleyelim
CORS_ALLOWED_ORIGINS = [
    f"http://{SERVER_HOST}",
    f"https://{SERVER_HOST}",
    f"http://{SERVER_HOST}:{API_PORT}",
    # Lokal geliştiriciler için
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Ek CORS ayarları
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    # SAPBot özel header'ları
    'x-api-key',
    'x-session-id',
    'x-user-type',
]

INSTALLED_APPS = [
    # Django admin teması
    'jazzmin',

    # Django çekirdek uygulamaları
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # yeni eklendi 05.05.2025

    # Üçüncü parti uygulamalar
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_extensions',
    'import_export',
    'channels',
    'celery_progress',

    # SAPBot API (öncelikli)
    'sapbot_api',

    # Özel uygulamalar (öncelikli olanlar)
    'authcentral.apps.AuthCentralConfig',
    'dpap',
    'sapreports',

    # Diğer özel uygulamalar (alfabetik sırayla)
    'bomcostmanager',
    'activities',
    'crmblog',
    'customercollection',
    'deliverydocsum',
    'deliverydocsumv2',
    'docarchivev2',
    'dynamicreport',
    'eduvideo',
    'filesharehub',
    'filesharehub_v2',
    'girsbergerordropqt',
    'hanadbcon',
    'hanadbintegration',
    'heliosforgev2',
    'logo_supplier_receivables_aging',
    'logocustomerbalance',
    'logocustomercollection',
    'logodbcon',
    'logosupplierbalance',
    'mailservice',
    'newcustomerform',
    'openorderdocsum',
    'orderarchive',
    'procure_compare',
    'productconfig',
    'productconfigv2',
    'productconfig_simulator',
    'productgroupdeliverysum',
    # 'productpicture',
    'rawmaterialwarehousestock',
    'report_orchestrator',
    'salesbudget',
    'salesbudgeteur',
    'salesbudgetv2',
    'salesinvoicesum',
    'salesofferdocsum',
    'salesorder',
    'salesorderdetail',
    'salesorderdocsum',
    'stockcardintegration',
    'shipweekplanner',
    'supplierpayment',
    'systemnotebook',
    'taskorchestrator',
    'totalrisk',
    # Tuna inşaat API'leri
    'tunainstotalrisk',
    'tunainssupplierpayment',
    'tunainssupplieradvancebalance',
]

# Özel uygulamaları filtreleme
CUSTOM_APPS = [
    app.split('.')[0] if '.' in app else app  # 'authcentral.apps.AuthCentralConfig' -> 'authcentral'
    for app in INSTALLED_APPS 
    if not app.startswith('django.') 
    and not app.startswith('rest_') 
    and not app.startswith('corsheaders') 
    and not app.startswith('drf_') 
    and not app.startswith('jazzmin') 
    and not app.startswith('django_') 
    and not app.startswith('channels') 
    and not app.startswith('celery_')
    and app not in ['import_export']  # Üçüncü parti uygulamayı hariç tut
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'sapbot_api.utils.exceptions.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 99999,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'sapbot_api.throttling.ChatRateThrottle',    # ✅ Mevcut
        'sapbot_api.throttling.UploadRateThrottle',  # ✅ Mevcut (UploadRateThrottle)
        'sapbot_api.throttling.BurstProtectionThrottle',  # ➕ Yeni eklenen
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100000/hour',    # ✅ Mevcut
        'user': '200000/hour',    # ✅ Mevcut  
        'chat': '60/hour',        # ✅ Mevcut
        'upload': '10/hour',      # ✅ Mevcut
        'search': '120/hour',     # ✅ Mevcut
        'burst': '30/min',        # ➕ Yeni - DDoS koruması
        'api_key': '1000/hour',   # ➕ Yeni - API key throttling
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # cors
    'django.middleware.locale.LocaleMiddleware',  # i18n için
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sapbot_api.middleware.SecurityMiddleware',  # SAPBot güvenlik middleware
    'sapbot_api.middleware.RequestLoggingMiddleware',  # SAPBot request logging
    #'authcentral.middleware.CheckBlacklistedTokenMiddleware',  # Güncellenmiş yol
]

ROOT_URLCONF = 'sapreports.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'sapbot_api', 'templates'),  # SAPBot templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # i18n için
            ],
        },
    },
]

# Redis ayarları .env den ayarlari al
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASS = os.getenv('REDIS_PASS', 'Tuna2023*')

redis_url = f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/2"

# Genel Redis Cache yapılandırması
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASS,
        }
    },
    # SAPBot özel cache
    "sapbot": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASS,
        }
    },
    # SAPBot embeddings cache
    "sapbot_embeddings": {
        "BACKEND": "django_redis.cache.RedisCache", 
        "LOCATION": f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASS,
        }
    },
    # SAPBot search cache
    "sapbot_search": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASS,
        }
    }
}

# Cache süresi 60 saniye
CACHE_TTL = 5 * 1
CACHE_CLEAR_THRESHOLD = 1000

# Celery Configuration Options
CELERY_BROKER_URL = f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Worker kontrol ve optimizasyon ayarları
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50  # Her worker 50 görevden sonra yenilenir (hafıza sızıntılarını önler, performansı artırır)
CELERY_WORKER_CONCURRENCY = 8  # 8 çekirdek için ideal, CPU'ya uygun
CELERYD_PREFETCH_MULTIPLIER = 2  # Her worker 2 görev prefetch eder, kuyruk tıkanıklığını azaltır
CELERY_ACKS_LATE = True  # Görev tamamlanmadan ACK gönderilmez, güvenilirlik için
CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT = True  # Hatalı veya timeout görevler için ACK, tekrar deneme için
CELERY_TASK_TIME_LIMIT = 600  # Maksimum 5 dakika (thumbnail oluşturma için yeterli)
CELERY_TASK_SOFT_TIME_LIMIT = 540  # 4.5 dakika uyarı, 5 dakikada öldür

STARTUP_TASK_SYNC = True

# Zamanlanmış görevler (beat) settings.py içinde
from report_orchestrator.config.celery_settings import CELERY_BEAT_SCHEDULE as REPORT_ORCHESTRATOR_SCHEDULE
from sapreports.beat_schedule_config import BEAT_SCHEDULE as CORE_BEAT_SCHEDULE


CELERY_IMPORTS = [
    "taskorchestrator.tasks",
    "report_orchestrator.tasks.run_report",
    "report_orchestrator.tasks.run_all_reports",  
    "filesharehub_v2.tasks.generate_thumbnail",
    "filesharehub_v2.tasks.fix_thumbnails_task",
    # SAPBot tasks
    "sapbot_api.tasks.document_processing",
    "sapbot_api.tasks.embedding_generation",
    "sapbot_api.tasks.chat_analytics", 
    "sapbot_api.tasks.system_maintenance",
    
]

# SAPBot Beat Schedule
SAPBOT_BEAT_SCHEDULE = {
    'sapbot-cleanup-old-analytics': {
        'task': 'sapbot_api.tasks.system_maintenance.cleanup_old_analytics',
        'schedule': 86400.0,  # Günlük
        'options': {'queue': 'sapbot_maintenance'}
    },
    'sapbot-generate-daily-reports': {
        'task': 'sapbot_api.tasks.chat_analytics.generate_daily_report',
        'schedule': 86400.0,  # Günlük
        'options': {'queue': 'sapbot_analytics'}
    },
    'sapbot-health-check': {
        'task': 'sapbot_api.tasks.system_maintenance.system_health_check',
        'schedule': 300.0,  # 5 dakikada bir
        'options': {'queue': 'sapbot_monitoring'}
    },
    'sapbot-cache-warmup': {
        'task': 'sapbot_api.tasks.system_maintenance.cache_warmup',
        'schedule': 3600.0,  # Saatlik
        'options': {'queue': 'sapbot_maintenance'}
    },
    'sapbot-embedding-optimization': {
        'task': 'sapbot_api.tasks.embedding_generation.optimize_embeddings',
        'schedule': 7200.0,  # 2 saatte bir
        'options': {'queue': 'sapbot_processing'}
    },
}

# Tüm beat schedule'ları birleştir
CELERY_BEAT_SCHEDULE = {
    **REPORT_ORCHESTRATOR_SCHEDULE,
    **CORE_BEAT_SCHEDULE,
    **SAPBOT_BEAT_SCHEDULE,

}

# Channels Configuration
ASGI_APPLICATION = 'sapreports.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [redis_url],
        },
    },
}

# WSGI uygulaması
WSGI_APPLICATION = 'sapreports.wsgi.application'

# settings.py postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDB_NAME'),
        'USER': os.getenv('PGDB_USER'),
        'PASSWORD': os.getenv('PGDB_PASSWORD'),
        'HOST': os.getenv('PGDB_HOST'),
        'PORT': os.getenv('PGDB_PORT'),
        'OPTIONS': {
            'options': '-c client_encoding=UTF8'  # Veritabanı ile iletişimde UTF-8 kullanımı
        },
        'TEST': {
            'NAME': 'test_sapb1reports_v2',  # Test veritabanının ismini burada belirtin
        },
    }
}

AUTH_USER_MODEL = 'authcentral.CustomUser'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),  # Örneğin 1 saat
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),  # Örneğin 1 hafta
    'ROTATE_REFRESH_TOKENS': False,  # Refresh token'ları döndürmeyeceksek False
    'BLACKLIST_AFTER_ROTATION': False,  # Blacklist kullanılmayacaksa False
    'ALGORITHM': 'HS256',  # Basit ve yaygın bir algoritma
    'SIGNING_KEY': SECRET_KEY,  # İmza için kullanılan anahtar
    'VERIFYING_KEY': None,  # HS256 için VERIFYING_KEY'e gerek yok
    'AUTH_HEADER_TYPES': ('Bearer',),  # Authorization header tipi
    'USER_ID_FIELD': 'id',  # Kullanıcı ID alanı
    'USER_ID_CLAIM': 'user_id',  # Token içindeki kullanıcı ID claim'i
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),  # Kullanılan token sınıfları
}

AUTH_PASSWORD_VALIDATORS = [] # django customuser basit sifre kabul etmesi icin

# settings.py
# Media Settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Statik dosyaların toplanacağı klasör
STATIC_ROOT = '/var/www/sapb1reportsv2/backend/backend_static/'

# Statik dosyaların servis edileceği URL
STATIC_URL = '/backend_static/'

# Statik dosyaların bulunduğu yerlerin listesi
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Eğer proje içinde başka statik dosyalarınız varsa
    os.path.join(BASE_DIR, 'sapbot_api', 'static'),  # SAPBot static files
    #'/mnt/product_picture/',  # Bu kısmı kendi statik dosyalarınızın bulunduğu klasör ile değiştirin
]

# POST ve GET isteklerinde izin verilen maksimum alan sayısını artırın
DATA_UPLOAD_MAX_NUMBER_FIELDS = 999999

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# SAPBot API Özel Konfigürasyonları
# =============================================================================

SAPBOT_CONFIG = {
    # AI Configuration
    'OPENAI_MODEL': os.getenv('SAPBOT_OPENAI_MODEL', 'gpt-4-turbo-preview'),
    'OPENAI_EMBEDDING_MODEL': os.getenv('SAPBOT_EMBEDDING_MODEL', 'text-embedding-3-small'),
    'EMBEDDING_DIMENSION': 1536,
    'TEMPERATURE': 0.3,
    'MAX_TOKENS': 1500,
    
    # Document Processing
    'MAX_DOCUMENT_SIZE_MB': 100,
    'SUPPORTED_DOCUMENT_TYPES': ['pdf', 'video', 'image', 'text'],
    'CHUNK_SIZE': 1000,
    'CHUNK_OVERLAP': 200,
    'MAX_PDF_PAGES': 2000,
    'MAX_VIDEO_DURATION_MINUTES': 120,
    'SUPPORTED_VIDEO_FORMATS': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
    'SUPPORTED_IMAGE_FORMATS': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
    
    # Chat Configuration  
    'MAX_CHAT_HISTORY': 20,
    'CHAT_TIMEOUT_SECONDS': 30,
    'MAX_SOURCES_RETURNED': 5,
    'CONTEXT_WINDOW_SIZE': 4000,
    'ENABLE_CONVERSATION_MEMORY': True,
    'AUTO_SUMMARIZE_THRESHOLD': 50,  # 50 mesaj sonra özetleme
    
    # Search Configuration
    'SIMILARITY_THRESHOLD': 0.7,
    'MAX_SEARCH_RESULTS': 10,
    'SEARCH_CACHE_TTL': 1800,  # 30 dakika
    'ENABLE_SEMANTIC_SEARCH': True,
    'ENABLE_KEYWORD_SEARCH': True,
    'SEARCH_BOOST_FACTORS': {
        'title': 2.0,
        'section_title': 1.5,
        'content': 1.0,
        'keywords': 1.8,
    },
    
    # Cache Configuration
    'CACHE_EMBEDDINGS': True,
    'CACHE_CHAT_RESPONSES': True, 
    'CACHE_SEARCH_RESULTS': True,
    'EMBEDDING_CACHE_TTL': 604800,  # 7 gün
    'RESPONSE_CACHE_TTL': 3600,  # 1 saat
    'SEARCH_CACHE_TTL': 1800,  # 30 dakika
    'SESSION_CACHE_TTL': 86400,  # 24 saat
    
    # Security & Rate Limiting
    'ENABLE_RATE_LIMITING': True,
    'ENABLE_INPUT_SANITIZATION': True,
    'ENABLE_AUDIT_LOGGING': True,
    'MAX_QUERY_LENGTH': 2000,
    'MIN_QUERY_LENGTH': 2,
    'BLOCKED_PATTERNS': [
        r'<script.*?>.*?</script>',
        r'javascript\s*:',
        r'(\bUNION\b|\bSELECT\b|\bINSERT\b)',
        r'(\||&&|;|\$\(|\`)',
        r'(\.\./|\.\.\\)',
    ],
    'ENABLE_IP_FILTERING': True,
    'MAX_UPLOAD_ATTEMPTS_PER_HOUR': 10,
    'MAX_FAILED_ATTEMPTS_BEFORE_LOCK': 5,
    
    # Performance & Processing
    'ENABLE_ASYNC_PROCESSING': True,
    'BATCH_PROCESSING_SIZE': 10,
    'WORKER_CONCURRENCY': 2,
    'PROCESSING_TIMEOUT': 1800,  # 30 dakika
    'ENABLE_PARALLEL_EMBEDDING': True,
    'MAX_CONCURRENT_EMBEDDINGS': 5,
    'CHUNK_PROCESSING_BATCH_SIZE': 50,
    
    # Analytics & Monitoring
    'ENABLE_ANALYTICS': True,
    'ANALYTICS_RETENTION_DAYS': 90,
    'ENABLE_PERFORMANCE_TRACKING': True,
    'ENABLE_ERROR_TRACKING': True,
    'ENABLE_USER_BEHAVIOR_TRACKING': True,
    'ANALYTICS_SAMPLING_RATE': 1.0,  # %100 tracking
    'ERROR_REPORTING_THRESHOLD': 10,
    
    # SAP Business One Integration
    'SAP_B1_VERSION': '10.0',
    'SAP_B1_PLATFORM': 'HANA',
    'DEFAULT_COMPANY_CODE': 'TUNA',
    'DEFAULT_CURRENCY': 'TRY',
    'SAP_MODULES': [
        'FI', 'MM', 'SD', 'CRM', 'PROD', 'HR', 'QM', 'PM', 
        'CO', 'WM', 'BI', 'ADMIN', 'INV', 'RES', 'SVC', 'MRP'
    ],
    'SAP_MODULE_PRIORITIES': {
        'FI': 1, 'SD': 1, 'MM': 2, 'CRM': 2, 'PROD': 2,
        'HR': 3, 'QM': 3, 'PM': 3, 'CO': 3, 'WM': 3
    },
    
    # User Types & Permissions
    'USER_TYPES': {
        'user': {'max_daily_requests': 100, 'max_upload_size_mb': 50},
        'technical': {'max_daily_requests': 500, 'max_upload_size_mb': 100},
        'admin': {'max_daily_requests': 1000, 'max_upload_size_mb': 200},
        'super_admin': {'max_daily_requests': -1, 'max_upload_size_mb': 500},
    },
    
    # File Storage & Paths
    'UPLOAD_PATH': 'sapbot_api/documents',
    'TEMP_PATH': '/tmp/sapbot_temp',
    'BACKUP_PATH': 'sapbot_api/backups',
    'THUMBNAIL_PATH': 'sapbot_api/thumbnails',
    'EXPORT_PATH': 'sapbot_api/exports',
    
    # Language & Localization
    'DEFAULT_LANGUAGE': 'tr',
    'SUPPORTED_LANGUAGES': ['tr', 'en'],
    'AUTO_DETECT_LANGUAGE': True,
    'TRANSLATION_CACHE_TTL': 86400,  # 24 saat
    
    # Notification Settings
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'ADMIN_EMAIL': 'admin@tunacelik.com.tr',
    'ERROR_NOTIFICATION_THRESHOLD': 10,
    'DAILY_REPORT_RECIPIENTS': ['admin@tunacelik.com.tr'],
    'ENABLE_SLACK_NOTIFICATIONS': False,
    'SLACK_WEBHOOK_URL': os.getenv('SLACK_WEBHOOK_URL', ''),
    
    # API Integration
    'ENABLE_WEBHOOK_NOTIFICATIONS': True,
    'WEBHOOK_TIMEOUT': 30,
    'WEBHOOK_RETRY_ATTEMPTS': 3,
    'API_VERSION': '1.0',
    
    # Development & Debug
    'ENABLE_DEBUG_LOGGING': DEBUG,
    'MOCK_OPENAI_RESPONSES': False,
    'ENABLE_PROFILING': DEBUG,
    'LOG_SQL_QUERIES': DEBUG,
   'ENABLE_REQUEST_LOGGING': True,
   'LOG_RETENTION_DAYS': 30,
   
   # Business Logic
   'ENABLE_INTENT_DETECTION': True,
   'ENABLE_SAP_MODULE_DETECTION': True,
   'ENABLE_TECHNICAL_LEVEL_DETECTION': True,
   'CONFIDENCE_THRESHOLD': 0.8,
   'FALLBACK_RESPONSE_ENABLED': True,
   'ENABLE_CONTEXT_AWARENESS': True,
   
   # Data Quality & Validation
   'ENABLE_CONTENT_VALIDATION': True,
   'DUPLICATE_DETECTION_THRESHOLD': 0.95,
   'MIN_CHUNK_LENGTH': 50,
   'MAX_CHUNK_LENGTH': 2000,
   'ENABLE_AUTO_TAGGING': True,
   'QUALITY_SCORE_THRESHOLD': 0.7,
   
   # System Health & Maintenance
   'HEALTH_CHECK_INTERVAL': 300,  # 5 dakika
   'AUTO_CLEANUP_ENABLED': True,
   'CLEANUP_RETENTION_DAYS': 30,
   'ENABLE_SYSTEM_MONITORING': True,
   'MEMORY_USAGE_THRESHOLD': 0.8,  # %80
   'DISK_USAGE_THRESHOLD': 0.9,  # %90
   
   # Backup & Recovery
   'ENABLE_AUTO_BACKUP': True,
   'BACKUP_INTERVAL_HOURS': 24,
   'BACKUP_RETENTION_DAYS': 7,
   'ENABLE_INCREMENTAL_BACKUP': True,
}

# Environment specific SAPBot settings
if DEBUG:
   SAPBOT_CONFIG.update({
       'ENABLE_DEBUG_LOGGING': True,
       'MOCK_OPENAI_RESPONSES': False,  # Test için True yapabilirsin
       'CACHE_EMBEDDINGS': False,  # Development'ta her seferinde yeniden üret
       'ENABLE_PROFILING': True,
       'LOG_SQL_QUERIES': True,
       'ANALYTICS_SAMPLING_RATE': 1.0,  # Development'ta %100 tracking
       'PROCESSING_TIMEOUT': 300,  # 5 dakika (development için kısa)
       'MAX_CONCURRENT_EMBEDDINGS': 2,  # Development için düşük
   })
else:
   # Production ortamında güvenlik artırımları  
   SAPBOT_CONFIG.update({
       'ENABLE_STRICT_VALIDATION': True,
       'ENABLE_ADVANCED_SECURITY': True,
       'RATE_LIMIT_STRICT_MODE': True,
       'ENABLE_AUDIT_TRAIL': True,
       'LOG_SQL_QUERIES': False,
       'ENABLE_DEBUG_LOGGING': False,
       'ANALYTICS_SAMPLING_RATE': 0.1,  # Production'da %10 sampling
       'CACHE_EMBEDDINGS': True,  # Production'da mutlaka cache
       'MAX_CONCURRENT_EMBEDDINGS': 5,  # Production için yüksek
   })

# SAPBot Database Router (opsiyonel - SAP HANA entegrasyonu için)
if HANADB_HOST:
   DATABASES['sap_hana'] = {
       'ENGINE': 'django_hana',
       'NAME': HANADB_SCHEMA,
       'USER': HANADB_USER,
       'PASSWORD': HANADB_PASS,
       'HOST': HANADB_HOST,
       'PORT': HANADB_PORT,
       'OPTIONS': {
           'driver': 'SAPHANA',
           'autocommit': True,
       }
   }

# SAPBot File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
FILE_UPLOAD_TEMP_DIR = '/tmp/sapbot_uploads'

import os
os.makedirs(FILE_UPLOAD_TEMP_DIR, exist_ok=True)


# SAPBot AI Settings
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
OPENAI_API_KEY =  os.getenv('OPENAI_API_KEY', None)

# Processing Settings  
SAPBOT_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
SAPBOT_CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
SAPBOT_MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100')) * 1024 * 1024

# Temp directory
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp/sapbot_temp')

# SAPBot Spectacular Settings Update
SPECTACULAR_SETTINGS.update({
   'TITLE': 'SAP B1 Reports & SAPBot API',
   'DESCRIPTION': '''
   SAP Business One HANA ERP Reports and AI Support System
   
   ## SAPBot Features:
   - AI-powered chat support for SAP B1
   - Document processing and knowledge management
   - Semantic search across SAP documentation
   - Multi-language support (Turkish/English)
   - Real-time analytics and monitoring
   ''',
   'VERSION': '2.0.0',
   'TAGS': SPECTACULAR_SETTINGS.get('TAGS', []) + [
       {'name': 'SAPBot Chat', 'description': 'AI Chat operations for SAP B1 support'}, 
       {'name': 'SAPBot Documents', 'description': 'Document upload and processing'},
       {'name': 'SAPBot Search', 'description': 'Semantic and keyword search'},
       {'name': 'SAPBot Analytics', 'description': 'Usage analytics and reporting'},
       {'name': 'SAPBot System', 'description': 'System health and configuration'},
       {'name': 'SAPBot User', 'description': 'User management and preferences'},
   ],
   'COMPONENTS': {
       'securitySchemes': {
           'bearerAuth': {
               'type': 'http',
               'scheme': 'bearer',
               'bearerFormat': 'JWT',
           },
           'apiKey': {
               'type': 'apiKey',
               'in': 'header',
               'name': 'X-API-Key'
           }
       }
   },
   'SECURITY': [{'bearerAuth': []}, {'apiKey': []}],
})

# SAPBot Celery Routes (Queue Management)
CELERY_ROUTES = {
   # SAPBot specific queues
   'sapbot_api.tasks.document_processing.*': {'queue': 'sapbot_processing'},
   'sapbot_api.tasks.embedding_generation.*': {'queue': 'sapbot_embeddings'},
   'sapbot_api.tasks.chat_analytics.*': {'queue': 'sapbot_analytics'},
   'sapbot_api.tasks.system_maintenance.*': {'queue': 'sapbot_maintenance'},
   
   # High priority tasks
   'sapbot_api.tasks.*.urgent_*': {'queue': 'sapbot_urgent'},
   
   # Low priority tasks
   'sapbot_api.tasks.*.cleanup_*': {'queue': 'sapbot_cleanup'},
}

# SAPBot WebSocket Settings (for real-time chat)
SAPBOT_WEBSOCKET_CONFIG = {
   'ENABLE_WEBSOCKETS': True,
   'MAX_CONNECTIONS_PER_USER': 3,
   'HEARTBEAT_INTERVAL': 30,
   'CONNECTION_TIMEOUT': 300,
   'MESSAGE_SIZE_LIMIT': 32768,  # 32KB
   'RATE_LIMIT_MESSAGES_PER_MINUTE': 60,
}

# Production optimizations
if not DEBUG:
   # Production cache optimization
   CACHES['sapbot']['OPTIONS'].update({
       'CONNECTION_POOL_KWARGS': {
           'max_connections': 20,
           'retry_on_timeout': True,
       },
       'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
   })
   
   # Production security headers
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   X_FRAME_OPTIONS = 'DENY'
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True

# SAPBot Custom Error Pages
SAPBOT_ERROR_PAGES = {
   400: 'sapbot_api/errors/400.html',
   403: 'sapbot_api/errors/403.html', 
   404: 'sapbot_api/errors/404.html',
   429: 'sapbot_api/errors/429.html',
   500: 'sapbot_api/errors/500.html',
}

# SAPBot Health Check URLs (for load balancer)
SAPBOT_HEALTH_CHECK_URLS = [
   '/api/sapbot/health/',
   '/api/sapbot/system/status/',
]

# settings.py'de Log yapılandırması (original LOGGING with SAPBot updates)
from sapreports.logger_settings import LOGGING


# Success message
print(f"✅ SAPBot API konfigürasyonu başarıyla yüklendi")
print(f"🌍 Environment: {ENVIRONMENT}")
print(f"🤖 OpenAI Model: {SAPBOT_CONFIG['OPENAI_MODEL']}")
print(f"🧠 Embedding Model: {SAPBOT_CONFIG['OPENAI_EMBEDDING_MODEL']}")
print(f"📊 Analytics: {'Enabled' if SAPBOT_CONFIG['ENABLE_ANALYTICS'] else 'Disabled'}")
print(f"🔒 Security: {'Strict' if not DEBUG else 'Development'}")
print(f"💾 Cache Layers: {len(CACHES)}")
print(f"⚡ Celery Queues: {len(CELERY_ROUTES)} routes configured")
