# backend/sapreports/wsgi.py

import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv(dotenv_path="/var/www/sapb1reportsv2/backend/.env")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
