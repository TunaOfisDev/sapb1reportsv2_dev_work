# backend/logodbcon/utilities/logodb_config.py
import pyodbc
import logging
from django.conf import settings

# Logger nesnesi oluştur
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def create_connection():
    """
    LOGO veritabanına ODBC bağlantısı oluşturur ve bağlantı nesnesini döndürür.
    """
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={settings.LOGO_DB_HOST},{settings.LOGO_DB_PORT};'
            f'DATABASE={settings.LOGO_DB_NAME};'
            f'UID={settings.LOGO_DB_USER};'
            f'PWD={settings.LOGO_DB_PASS}'
        )
        logger.info("Veritabanına başarıyla bağlanıldı.")
        return connection
    except pyodbc.Error as e:
        logger.error(f"LOGO veritabanına bağlanırken hata: {str(e)}")
        return None
