# path: backend/nexuscore/services/connection_manager.py

import uuid
import logging
import datetime
from decimal import Decimal
from contextlib import contextmanager
from typing import Dict, Any, Tuple, List, Optional
import json

from django.conf import settings
from django.db import connections, OperationalError
from hdbcli import dbapi as hanadb_api

from ..utils.popular_db_list import SUPPORTED_DB_VALUES
from ..models import DynamicDBConnection, VirtualTable, DBTypeMapping
from ..utils.data_type_mapper import get_type_mapping, _get_source_type_from_info

logger = logging.getLogger(__name__)

DIRECT_CONNECT_TYPES = {'sap_hana'}
MSSQL_DIALECT_TYPES = {'sql_server', 'azure_sql'}

@contextmanager
def _django_engine_connection(config: Dict[str, Any]):
    alias = f"dyn_django_{uuid.uuid4().hex}"
    try:
        connection_config = config.copy()
        connection_config.setdefault('TIME_ZONE', settings.TIME_ZONE)
        connection_config.setdefault('CONN_HEALTH_CHECKS', True)
        connection_config.setdefault('CONN_MAX_AGE', 0)
        settings.DATABASES[alias] = connection_config
        yield connections[alias]
    finally:
        if alias in connections:
            connections[alias].close()
        if alias in settings.DATABASES:
            del settings.DATABASES[alias]

@contextmanager
def _direct_hdb_connection(config: Dict[str, Any]):
    connection = None
    try:
        connection = hanadb_api.connect(
            address=config.get('HOST'),
            port=int(config.get('PORT')),
            user=config.get('USER'),
            password=config.get('PASSWORD'),
            currentSchema=config.get('OPTIONS', {}).get('schema')
        )
        yield connection
    finally:
        if connection:
            connection.close()

def _get_sample_data_for_type_inference(connection_obj: DynamicDBConnection, sql_query: str, limit: int = 3) -> Optional[List[Tuple]]:
    """
    Sorgudan ilk 'limit' kadar satırı çeker ve veri tipi tahmini için kullanır.
    """
    if not connection_obj.is_active:
        return None

    db_type = connection_obj.db_type
    config = connection_obj.config_json
    rows = []

    try:
        if db_type in DIRECT_CONNECT_TYPES:
            with _direct_hdb_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchmany(limit)
        elif db_type in MSSQL_DIALECT_TYPES:
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchmany(limit)
        else: # Varsayılan: PostgreSQL, MySQL, vb.
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchmany(limit)
        
        return rows
    except Exception as e:
        logger.error(f"Sorgudan örnek veri alınırken hata: {e}")
        return None

def test_connection_config(config: Dict[str, Any], db_type: str) -> Tuple[bool, str]:
    if db_type in DIRECT_CONNECT_TYPES:
        try:
            with _direct_hdb_connection(config):
                pass
            return True, "SAP HANA (Direkt) bağlantısı başarılı."
        except hanadb_api.Error as e:
            return False, f"SAP HANA (Direkt) bağlantı hatası: {e}"
        except Exception as e:
            return False, f"Genel bir hata oluştu: {e}"
    else:
        try:
            with _django_engine_connection(config) as conn:
                conn.ensure_connection()
            return True, "Standart Django Engine bağlantısı başarılı."
        except OperationalError as e:
            return False, f"Veritabanı operasyonel hatası: {e}"
        except Exception as e:
            return False, f"Genel bir hata oluştu: {e}"


def execute_virtual_table_query(virtual_table: VirtualTable) -> Dict[str, Any]:
    if not virtual_table.connection.is_active:
        return {"success": False, "error": "Bu sorgunun kullandığı veri kaynağı pasif durumdadır."}

    connection_obj = virtual_table.connection
    config = connection_obj.config_json
    sql_query = virtual_table.sql_query

    try:
        if connection_obj.db_type in DIRECT_CONNECT_TYPES:
            with _direct_hdb_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description or []]
                    rows = cursor.fetchall()
        else:
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description or []]
                    rows = cursor.fetchall()
        
        sanitized_rows = []
        for row in rows:
            sanitized_rows.append([
                cell.isoformat() if isinstance(cell, (datetime.datetime, datetime.date))
                else str(cell) if isinstance(cell, Decimal)
                else cell.decode('utf-8', 'replace') if isinstance(cell, bytes)
                else cell
                for cell in row
            ])
        
        return {"success": True, "columns": columns, "rows": sanitized_rows}

    except Exception as e:
        logger.error(f"Sorgu çalıştırılırken hata (VirtualTable ID: {virtual_table.id}): {e}")
        return {"success": False, "error": f"Sorgu çalıştırılırken hata oluştu: {str(e)}"}


def generate_metadata_for_query(connection_model: DynamicDBConnection, sql_query: str) -> Dict[str, Any]:
    """
    Verilen sorgudan, bağlantı türüne göre doğru yöntemle meta veri üretir.
    Bu fonksiyon artık veri tiplerini veritabanına kaydeder.
    """
    if not connection_model.is_active:
        return {"success": False, "error": "Kullanılan veri kaynağı pasif durumdadır."}

    db_type = connection_model.db_type
    
    if db_type not in SUPPORTED_DB_VALUES:
        return {"success": False, "error": f"Desteklenmeyen veritabanı türü: '{db_type}'. Lütfen yönetici ile görüşün."}

    config = connection_model.config_json

    try:
        description = [] 
        
        # SORGUNUN SADECE İLK 3 SATIRINI ÇEKEREK PERFORMANS KAZANIYORUZ
        sample_rows = _get_sample_data_for_type_inference(connection_model, sql_query, limit=3)
        if sample_rows is None:
            return {"success": False, "error": "Veri tipi tahmini için örnek veri alınamadı."}
        
        # description'ı almak için sorgu optimizasyonunu kullanmaya devam edebiliriz
        # bu, boş bir sorgu olduğu için hızlıdır
        if db_type in DIRECT_CONNECT_TYPES:
            with _direct_hdb_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    description = cursor.description or []
        
        elif db_type in MSSQL_DIALECT_TYPES:
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    optimized_query = f"SELECT TOP 0 * FROM ({sql_query}) AS subquery"
                    cursor.execute(optimized_query)
                    description = cursor.description or []
        
        else:
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    optimized_query = f"SELECT * FROM ({sql_query}) AS subquery LIMIT 0"
                    cursor.execute(optimized_query)
                    description = cursor.description or []
        
        metadata = {}
        for i, col_desc in enumerate(description):
            if not isinstance(col_desc, tuple) or len(col_desc) < 2:
                logger.warning(f"Beklenmeyen meta veri formatı saptandı: {col_desc}")
                continue
                
            col_name = col_desc[0]
            type_obj = col_desc[1]

            # Yeni dinamik veri tipi tespiti
            # Eğer get_type_mapping fonksiyonu tipi veritabanından alabiliyorsa onu kullanırız
            # Aksi halde, örnek veriden tipi tahmin ederiz.
            data_type = get_type_mapping(db_type, type_obj)
            
            # Eğer tip hala 'other' ise ve elimizde örnek veri varsa, tahmin etmeye çalışırız
            if data_type == 'other' and sample_rows:
                # Sütun bazında örnekleri al
                column_samples = [row[i] for row in sample_rows if len(row) > i and row[i] is not None]
                if column_samples:
                    inferred_type = _infer_type_from_samples(column_samples)
                    if inferred_type != 'other':
                        # Tahmin edilen tipi kaydetme
                        _save_inferred_type(db_type, type_obj, inferred_type)
                        data_type = inferred_type
            
            metadata[col_name] = {
                "label": col_name,
                "visible": True,
                "dataType": data_type
            }
        
        if not metadata:
            return {"success": False, "error": "Sorgu başarıyla çalıştı ancak hiçbir kolon bilgisi (meta veri) döndürmedi."}

        return {"success": True, "metadata": metadata}

    except Exception as e:
        logger.error(f"Sorgu meta verisi alınırken hata (Connection ID: {connection_model.id}): {e}", exc_info=True)
        return {"success": False, "error": f"Sorgu meta verisi alınırken hata oluştu: {str(e)}"}

# Yeni yardımcı fonksiyonlar
def _infer_type_from_samples(samples: List[Any]) -> str:
    """Örnek veri listesinden veri tipini tahmin eder."""
    # Sadece ilk 3 verinin tamamı sayısal veya ondalıklıysa 'number' olarak işaretle
    is_number = all(isinstance(s, (int, float, Decimal)) for s in samples)
    if is_number:
        return 'number'
    
    # Sadece ilk 3 verinin tamamı tarih veya datetime'sa 'datetime' olarak işaretle
    is_datetime = all(isinstance(s, (datetime.datetime, datetime.date)) for s in samples)
    if is_datetime:
        # Eğer hepsi tarihse ama datetime değilse 'date' olarak işaretle
        is_date = all(isinstance(s, datetime.date) and not isinstance(s, datetime.datetime) for s in samples)
        return 'date' if is_date else 'datetime'

    # Diğer durumlarda string olarak kabul edebiliriz
    return 'string'

def _save_inferred_type(db_type: str, type_obj: Any, general_category: str):
    """
    Tahmin edilen veri tipini DBTypeMapping tablosuna kaydeder.
    """
    source_type_str = _get_source_type_from_info(type_obj)
    try:
        DBTypeMapping.objects.update_or_create(
            db_type=db_type,
            source_type=source_type_str,
            defaults={'general_category': general_category}
        )
        logger.info(f"Yeni veri tipi otomatik olarak kaydedildi: '{db_type}' -> '{source_type_str}' -> '{general_category}'")
    except Exception as e:
        logger.error(f"Tahmin edilen veri tipi kaydedilirken hata oluştu: {e}")