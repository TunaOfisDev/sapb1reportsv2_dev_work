# backend\dynamicreport\data_services.py
from django.db import connections
from django.db.utils import OperationalError
from loguru import logger

def execute_sql_query(query, using='default'):
    try:
        # Veritabanı bağlantısını alır
        db_conn = connections[using]
        cursor = db_conn.cursor()

        # SQL sorgusunu çalıştırır
        cursor.execute(query)

        # Sorgu sonuçlarını alır
        result = cursor.fetchall()

        # Bağlantı ve cursor'ı kapatır
        cursor.close()
        db_conn.close()

        return result

    except OperationalError as e:
        logger.error(f"SQL Sorgusu Hatası: {str(e)}")
        raise OperationalError(f"SQL sorgusu çalıştırılırken bir hata oluştu: {str(e)}")
