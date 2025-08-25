# path: /var/www/sapb1reportsv2/backend/nexuscore/services/connection_manager.py

import uuid
from contextlib import contextmanager
from django.conf import settings
from django.db import connections
from typing import Dict, Any, List

# Type hinting için modellerimizi import edelim.
from ..models import DynamicDBConnection, VirtualTable
from ..utils import db_helpers

@contextmanager
def dynamic_database_connection(connection_config: Dict[str, Any]):
    """
    Verilen yapılandırma ile geçici bir veritabanı bağlantısı kuran
    ve işlem bittiğinde arkasını temizleyen bir context manager.
    Her kullanımda %100 benzersiz bir alias üretir.
    """
    # İYİLEŞTİRME: Sabit bir alias yerine, her seferinde benzersiz bir UUID kullanalım.
    # Bu, aynı anda birden fazla test veya sorgu çalıştığında çakışma riskini sıfırlar.
    alias = f"dyn_service_{uuid.uuid4().hex}"
    try:
        settings.DATABASES[alias] = connection_config
        yield alias
    finally:
        if alias in connections:
            connections[alias].close()
        if alias in settings.DATABASES:
            del settings.DATABASES[alias]


def execute_virtual_table_query(virtual_table: VirtualTable) -> Dict[str, Any]:
    """
    Bir VirtualTable nesnesini alır, ilgili dinamik bağlantıyı kurar,
    sorguyu çalıştırır ve sonucu (kolonlar ve satırlar) bir sözlük olarak döndürür.
    Modeldeki şifreleme değişikliğinden etkilenmez.
    """
    # Modelimiz şifre çözme işini şeffaf bir şekilde yaptığı için bu satır hala çalışır.
    connection_config = virtual_table.connection.json_config
    sql_query = virtual_table.sql_query

    try:
        with dynamic_database_connection(connection_config) as alias:
            with connections[alias].cursor() as cursor:
                cursor.execute(sql_query)
                
                columns: List[str] = [col[0] for col in cursor.description]
                rows: List[Dict[str, Any]] = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return {"success": True, "columns": columns, "rows": rows}
    
    except Exception as e:
        return {"success": False, "error": f"Sorgu çalıştırılırken hata oluştu: {str(e)}"}


def generate_metadata_for_query(connection: DynamicDBConnection, sql_query: str) -> Dict[str, Any]:
    """
    Yeni bir VirtualTable oluşturulurken, verilen sorguyu çalıştırıp
    sadece kolon bilgilerini çıkarır ve `column_metadata` formatında döndürür.
    """
    connection_config = connection.json_config

    try:
        with dynamic_database_connection(connection_config) as alias:
            with connections[alias].cursor() as cursor:
                cursor.execute(sql_query)
                
                columns: List[str] = [col[0] for col in cursor.description]
                metadata: Dict[str, Dict[str, Any]] = {
                    col: {"visible": True, "label": col} for col in columns
                }
                return {"success": True, "metadata": metadata}

    except Exception as e:
        return {"success": False, "error": f"Sorgu meta verisi alınırken hata oluştu: {str(e)}"}