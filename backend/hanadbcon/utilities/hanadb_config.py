# backend/hanadbcon/utilities/hanadb_config.py
from hdbcli import dbapi
from django.conf import settings
import logging

# Logger nesnesi oluştur
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def create_connection():
    """
    HANA veritabanına bağlantı oluşturur ve bağlantı nesnesini döndürür.
    """
    try:
        connection = dbapi.connect(
            address=settings.HANADB_HOST,
            port=int(settings.HANADB_PORT),
            user=settings.HANADB_USER,
            password=settings.HANADB_PASS,
            autocommit=True
        )
        return connection
    except dbapi.Error as e:
        logger.error(f"HANA veritabanına bağlanırken hata: {str(e)}")
        return None


