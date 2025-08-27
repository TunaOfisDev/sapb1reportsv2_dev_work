# path: backend/nexuscore/services/connection_manager.py

import uuid
import logging
from contextlib import contextmanager
from django.conf import settings
from django.db import connections, OperationalError
from typing import Dict, Any, Tuple

# HANA için doğrudan bağlantı kütüphanesi
from hdbcli import dbapi as hanadb_api
# Modellerimiz
from ..models import DynamicDBConnection, VirtualTable

logger = logging.getLogger(__name__)

# --- BAĞLANTI YÖNTEMİ 1: Standart Django ENGINE Bağlantısı ---
@contextmanager
def _django_engine_connection(config: Dict[str, Any]):
    """ (İç Kullanım) Django'nun standart veritabanı motoru üzerinden geçici bağlantı kurar. """
    alias = f"dyn_django_{uuid.uuid4().hex}"
    try:
        connection_config = config.copy()

        # TIME_ZONE için akıllı varsayılan
        if 'TIME_ZONE' not in connection_config:
            connection_config['TIME_ZONE'] = settings.TIME_ZONE

        # CONN_HEALTH_CHECKS için akıllı varsayılan
        if 'CONN_HEALTH_CHECKS' not in connection_config:
            connection_config['CONN_HEALTH_CHECKS'] = True

        # ### NİHAİ DÜZELTME: CONN_MAX_AGE için akıllı varsayılan ###
        # Django'nun yeni sürümleri bu ayarı da bekliyor.
        # 0 değeri, her istek sonunda bağlantının kapatılmasını sağlar. Bu, dinamik
        # bağlantılar için en güvenli ve en stabil ayardır.
        if 'CONN_MAX_AGE' not in connection_config:
            connection_config['CONN_MAX_AGE'] = 0

        settings.DATABASES[alias] = connection_config
        yield connections[alias]
    finally:
        if alias in connections:
            connections[alias].close()
        if alias in settings.DATABASES:
            del settings.DATABASES[alias]

# --- BAĞLANTI YÖNTEMİ 2: Direkt SAP HANA Bağlantısı ---
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

# --- AKILLI SANTRAL FONKSİYONLARI ---

def test_connection_config(config: Dict[str, Any], db_type: str) -> Tuple[bool, str]:
    """ Verilen yapılandırmayı, türüne göre doğru yöntemle test eder. """
    if db_type == 'sap_hana':
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
    """ Bir sorguyu, bağlantı türüne göre doğru yöntemle çalıştırır. """
    if not virtual_table.connection.is_active:
        return {"success": False, "error": "Bu sorgunun kullandığı veri kaynağı pasif durumdadır."}

    connection_obj = virtual_table.connection
    config = connection_obj.config_json
    sql_query = virtual_table.sql_query

    try:
        if connection_obj.db_type == 'sap_hana':
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
        
        return {"success": True, "columns": columns, "rows": rows}
    except Exception as e:
        logger.error(f"Sorgu çalıştırılırken hata: {e}")
        return {"success": False, "error": f"Sorgu çalıştırılırken hata oluştu: {str(e)}"}


def generate_metadata_for_query(connection_model: DynamicDBConnection, sql_query: str) -> Dict[str, Any]:
    """ Verilen sorgudan, bağlantı türüne göre doğru yöntemle meta veri üretir. """
    if not connection_model.is_active:
        return {"success": False, "error": "Kullanılan veri kaynağı pasif durumdadır."}

    config = connection_model.config_json

    try:
        if connection_model.db_type == 'sap_hana':
            with _direct_hdb_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description or []]
        else:
            with _django_engine_connection(config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0] for col in cursor.description or []]

        metadata = {col: {"visible": True, "label": col} for col in columns}
        return {"success": True, "metadata": metadata}

    except Exception as e:
        logger.error(f"Sorgu meta verisi alınırken hata: {e}")
        return {"success": False, "error": f"Sorgu meta verisi alınırken hata oluştu: {str(e)}"}