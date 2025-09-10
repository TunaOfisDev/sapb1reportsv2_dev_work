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
            port=int(config.get('PORT')), # <-- DİKKAT: Port'u integer'a çeviriyor
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
    [DEBUG VERSİYONU]
    Verilen sorgudan meta veri üretir ve teşhis için terminale detaylı bilgi basar.
    """
    if not connection_model.is_active:
        return {"success": False, "error": "Kullanılan veri kaynağı pasif durumdadır."}

    db_type = connection_model.db_type
    if db_type not in SUPPORTED_DB_VALUES:
        return {"success": False, "error": f"Desteklenmeyen veritabanı türü: '{db_type}'."}

    config = connection_model.config_json
    
    # --- DEBUG BAŞLANGIÇ ---
    print("\n" + "="*20 + " META VERİ AYIKLAMA BAŞLADI " + "="*20)
    
    try:
        description: List[Tuple] = []
        
        if db_type in DIRECT_CONNECT_TYPES:
            with _direct_hdb_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    description = cursor.description or []
        else:
            optimized_query = sql_query
            if db_type in MSSQL_DIALECT_TYPES:
                if not sql_query.strip().upper().startswith('WITH'):
                    optimized_query = f"SELECT TOP 0 * FROM ({sql_query}) AS subquery"
            else:
                if not sql_query.strip().upper().startswith('WITH'):
                    optimized_query = f"SELECT * FROM ({sql_query}) AS subquery LIMIT 0"
            
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(optimized_query)
                    description = cursor.description or []

        if not description:
             return {"success": False, "error": "Sorgu çalıştı ancak kolon bilgisi döndürmedi."}

        # --- DEBUG ADIM 1: ÖRNEK VERİYİ GÖRSELLEŞTİR ---
        sample_rows = _get_sample_data_for_type_inference(connection_model, sql_query, limit=5)
        print(f"\n[DEBUG 1] _get_sample_data_for_type_inference'dan dönen örnek satırlar:")
        print(sample_rows)
        if sample_rows:
            print(f"[DEBUG 1.1] İlk satırdaki ilk hücrenin tipi: {type(sample_rows[0][0])}")


        metadata = {}
        for i, col_desc in enumerate(description):
            col_name = col_desc[0]
            type_obj = col_desc[1]
            source_type = _get_source_type_str(type_obj)
            
            data_type = _get_type_mapping_from_db(db_type, source_type)
            
            # --- DEBUG ADIM 2: SAYISAL BİR KOLON İÇİN TAHMİN SÜRECİNİ İZLE ---
            is_bakiye_column = col_name.lower() == 'bakiye' # 'Bakiye' kolonunu özel olarak izleyelim

            if data_type == 'other' and sample_rows:
                column_samples = [row[i] for row in sample_rows if len(row) > i and row[i] is not None]
                
                if is_bakiye_column:
                    print(f"\n[DEBUG 2] 'Bakiye' kolonu için örnekler (None'lar hariç):")
                    print(column_samples)
                    if column_samples:
                        print(f"[DEBUG 2.1] 'Bakiye' kolonundaki ilk örneğin tipi: {type(column_samples[0])}")

                inferred_type = _infer_type_from_samples(column_samples)
                
                if is_bakiye_column:
                     print(f"[DEBUG 2.2] 'Bakiye' kolonu için tahmin edilen tip: {inferred_type}")

                _save_inferred_type(db_type, source_type, inferred_type)
                data_type = inferred_type
            
            metadata[col_name] = {
                "label": col_name.replace("_", " ").title(),
                "visible": True, "dataType": data_type, "nativeType": source_type
            }
        
        print("\n" + "="*20 + " META VERİ AYIKLAMA BİTTİ " + "="*23 + "\n")
        return {"success": True, "metadata": metadata}

    except Exception as e:
        logger.error(f"Sorgu meta verisi alınırken hata (Connection ID: {connection_model.id}): {e}", exc_info=True)
        return {"success": False, "error": f"Sorgu meta verisi alınırken hata oluştu: {str(e)}"}


# Yeni yardımcı fonksiyonlar
def _infer_type_from_samples(samples: List[Any]) -> str:
    """
    Örnek veri listesinden veri tipini tahmin eder.
    BU GÜNCELLENMİŞ VERSİYON, string olarak gelen sayıları da tanıyabilir.
    """
    if not samples:
        return 'string'

    # Önce orijinal tipleri kontrol edelim (iyi sürücüler için)
    if all(isinstance(s, bool) for s in samples): return 'boolean'
    if all(isinstance(s, int) for s in samples): return 'integer'
    if all(isinstance(s, datetime.datetime) for s in samples): return 'datetime'
    if all(isinstance(s, datetime.date) for s in samples): return 'date'
    
    # Şimdi "ambalajı açma" kısmı: Her örneğin sayıya benzip benzemediğini kontrol et.
    # try-except bloğu, metinleri sayıya çevirmeye çalışırken oluşacak hataları yakalar.
    is_numeric = True
    is_integer = True
    for sample in samples:
        if isinstance(sample, (int, float, Decimal)):
            if not isinstance(sample, int):
                is_integer = False
            continue # Zaten sayısal, sonraki örneğe geç
            
        # Eğer string ise, sayıya çevirmeyi dene
        if isinstance(sample, str):
            try:
                float(sample.replace(',', '.')) # Ondalık için virgülü noktaya çevir
                if '.' in sample or ',' in sample:
                    is_integer = False
            except (ValueError, TypeError):
                # Bu örnek sayıya çevrilemedi, demek ki bu kolon sayısal değil.
                is_numeric = False
                break # Döngüyü kır, daha fazla kontrol anlamsız.
        else:
            # String, int, float, Decimal dışında bir tip (örn: NoneType)
            is_numeric = False
            break

    if is_numeric:
        return 'integer' if is_integer else 'decimal'
        
    # Hiçbirine uymuyorsa, bu kesinlikle bir string'dir.
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

def _get_source_type_str(type_obj: Any) -> str:
    """Veritabanı sürücüsünden gelen ham tip nesnesini güvenli bir string'e çevirir."""
    # SAP HANA hdbcli.dbapi.FIELD_TYPE nesneleri için
    if hasattr(type_obj, 'name') and isinstance(type_obj.name, str):
        return type_obj.name
    # Django cursor.description'dan gelen tamsayı kodları için
    return str(type_obj)

def _get_type_mapping_from_db(db_type: str, source_type: str) -> str:
    """Verilen ham tipi, DBTypeMapping tablosundan arar."""
    try:
        mapping = DBTypeMapping.objects.get(db_type=db_type, source_type=source_type)
        return mapping.general_category
    except DBTypeMapping.DoesNotExist:
        return 'other'