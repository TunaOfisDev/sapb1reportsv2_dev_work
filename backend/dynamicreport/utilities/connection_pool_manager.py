# backend\dynamicreport\connection_pool_manager.py
from django.db import connections
from django.db.utils import OperationalError
from loguru import logger

def check_database_connection():
    """
    Bu fonksiyon, veritabanına bağlantı sağlamaya çalışır ve bağlantı sağlanamazsa hata verir.
    """
    try:
        # varsayılan veritabanı bağlantısını alır ve bağlantıyı kontrol eder
        default_conn = connections['default']
        default_conn.ensure_connection()
    except OperationalError as e:
        logger.error(f"Veritabanı bağlantısı başarısız oldu: {str(e)}")
        raise OperationalError(f"Veritabanı bağlantısı başarısız oldu: {str(e)}")


