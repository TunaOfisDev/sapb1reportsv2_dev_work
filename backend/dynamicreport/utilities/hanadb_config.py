# backend/dynamicreport/hanadb_config.py
from hdbcli import dbapi
from django.conf import settings
from loguru import logger
from django.db import DatabaseError

# .env dosyasındaki ayarları yükleyin
DB_HOST = settings.HANADB_HOST
DB_PORT = settings.HANADB_PORT
DB_USER = settings.HANADB_USER
DB_PASS = settings.HANADB_PASS
DB_SCHEMA = settings.HANADB_SCHEMA

def create_hana_connection(retries=3):
    while retries > 0:
        try:
            conn = dbapi.connect(
                address  = DB_HOST,
                port     = int(DB_PORT),
                user     = DB_USER,
                password = DB_PASS,
                currentSchema = DB_SCHEMA
            )
            return conn
        except dbapi.Error as e:
            retries -= 1
            logger.warning(f"HANA Bağlantı Hatası: {str(e)}. Kalan deneme sayısı: {retries}")

    raise DatabaseError(f"HANA server ile bağlantı kurulamadı.")

