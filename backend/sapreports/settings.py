# backend/sapreports/settings.py
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger
from datetime import timedelta
from decouple import config
import os

from .spectacular_settings import SPECTACULAR_SETTINGS

load_dotenv()  # .env dosyasından ayarları yükler

# --- Ortam ayarları  -------------------------------------------------
ENVIRONMENT   = os.getenv('ENVIRONMENT', 'development')
SERVER_HOST   = os.getenv('SERVER_HOST', '127.0.0.1')
API_PORT      = os.getenv('INTERNAL_API_PORT', '8000')
SITE_URL      = f"http://{SERVER_HOST}:{API_PORT}"
# --------------------------------------------------------------------

# Local settings.py
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True
# sayısal format ###.###,##
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
USE_L10N = True
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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


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
    'EXCEPTION_HANDLER': 'sapreports.custom_exception_handler.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 99999,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100000/hour',  # Anonim kullanıcılar için saatlik istek limiti
        'user': '200000/hour'   # Oturum açmış kullanıcılar için saatlik istek limiti
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # cors
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'authcentral.middleware.CheckBlacklistedTokenMiddleware',  # Güncellenmiş yol
]


ROOT_URLCONF = 'sapreports.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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
CELERY_BEAT_SCHEDULE = {
    **REPORT_ORCHESTRATOR_SCHEDULE,
    **CORE_BEAT_SCHEDULE,
}

CELERY_IMPORTS = [
    "taskorchestrator.tasks",
    "report_orchestrator.tasks.run_report",
    "report_orchestrator.tasks.run_all_reports",  
    "filesharehub_v2.tasks.generate_thumbnail",
    "filesharehub_v2.tasks.fix_thumbnails_task",
    
]


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
    #'/mnt/product_picture/',  # Bu kısmı kendi statik dosyalarınızın bulunduğu klasör ile değiştirin
]

# POST ve GET isteklerinde izin verilen maksimum alan sayısını artırın
DATA_UPLOAD_MAX_NUMBER_FIELDS = 999999


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py'de Log yapılandırması
from sapreports.logger_settings import LOGGING
