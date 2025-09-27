# backend\dynamicreport\hana_services.py
from .hanadb_config import create_hana_connection
from .dynamic_headers_type_temp import generate_dynamic_headers_template
from .hana_data_types import format_value_according_to_type, detect_hana_data_type
from django.core.exceptions import ObjectDoesNotExist
from ..models.models import DynamicTable, SqlQuery, DynamicHeaders
from django.db import DatabaseError
from django.db import connections
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from loguru import logger
import socket
import json


DB_HOST = settings.HANADB_HOST
DB_PORT = settings.HANADB_PORT

def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
    return result == 0

# HANA servisinin çalışıp çalışmadığını ve bağlantının kurulup kurulmadığını kontrol eder
def check_hana_service():
    host = DB_HOST  # hanadb_config.py dosyasından alınan değer
    port = int(DB_PORT)  # hanadb_config.py dosyasından alınan değer
    if is_port_open(host, port):
        try:
            conn = create_hana_connection()
            # conn.ping() kodunu kaldırdık
            logger.info("HANA servisi başarıyla çalışıyor.")
            conn.close()
            return True
        except DatabaseError:
            logger.error("HANA servisiyle bağlantı kurulamadı.")
            return False
    else:
        logger.error("HANA servisiyle bağlantı kurulamadı. Port kapalı.")
        return False


# Dinamik başlıklar oluşturur veya günceller
def update_dynamic_headers(column_names, query_table_name):
    for i, column_name in enumerate(column_names):
        defaults = {'header_name': column_name}
        existing_dynamic_header = DynamicHeaders.objects.filter(table_name=query_table_name, line_no=i).first()
        
        if existing_dynamic_header:
            defaults['type'] = existing_dynamic_header.type

        DynamicHeaders.objects.update_or_create(
            table_name=query_table_name, line_no=i, defaults=defaults
        )

# Verileri HANA veri kümesine kaydeder
def save_to_hana_data_set(query_table_name, result_converted):
    try:
        dynamic_table = DynamicTable.objects.get(table_name=query_table_name)
        result_converted = [[str(cell) if isinstance(cell, Decimal) else cell for cell in row] for row in result_converted]
        dynamic_table.hana_data_set = result_converted
        dynamic_table.fetched_at = timezone.now()
        dynamic_table.save()
        logger.info("HANA veri kümesi başarıyla güncellendi.")
    except ObjectDoesNotExist:
        logger.error("HANA veri kümesi kaydedilemedi.")

# HANA SQL sorgusunu yürütür ve sonuçları işler
def execute_hana_sql_query(sql_query, query_table_name):
    if not check_hana_service():
        raise Exception("HANA servisi çalışmıyor. Lütfen HANA servisini başlatın.")
        
    conn = cursor = None
    result_converted = []  # Sonuçları depolamak için liste
    try:
        conn = create_hana_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        # HANA'dan dönen ilk satırı alıyoruz
        first_row = result[0] if result else None

        for i, value in enumerate(first_row):
            column_name = column_names[i]

            # Hana türünü algılamak için detect_hana_data_type fonksiyonunu kullanıyoruz
            detected_type = detect_hana_data_type(value)
            if detected_type:
                DynamicHeaders.objects.update_or_create(
                    table_name=query_table_name,
                    line_no=i,
                    defaults={
                        'header_name': column_name,
                        'type': detected_type,  # Şimdi burada bir HanaDataType örneği var
                    }
                )

        headers_template = generate_dynamic_headers_template(query_table_name)

        for row in result:
            formatted_row = []
            for i, value in enumerate(row):
                column_name = column_names[i]
                column_type = headers_template.get(column_name, "default")
                if column_type:
                    type_code = column_type.type_code  # HanaDataType nesnesinin 'type_code' özelliğini al
                else:
                    type_code = "default"
                formatted_value = format_value_according_to_type(value, type_code)  # Yeni fonksiyon burada çağırılıyor
                formatted_row.append(formatted_value)
                if formatted_row not in result_converted:
                    result_converted.append(formatted_row)

        # Kolon adlarını ve veri türlerini yazdır
        for i, value in enumerate(row):
            column_name = column_names[i]
            column_type = headers_template.get(column_name, "default")
            formatted_value = format_value_according_to_type(value, column_type)
            logger.info(f"Kolon Adı: {column_name}, Kolon Türü: {column_type}, Formatlanmış Değer: {formatted_value}")

        update_dynamic_headers(column_names, query_table_name)
        save_to_hana_data_set(query_table_name, result_converted)
        logger.info("SQL sorgusu başarıyla yürütüldü.")
        return result_converted
    except (DatabaseError, Exception) as e:
        logger.error(f"Hata: {str(e)}")
        raise DatabaseError(f"Hata: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Decimal'ı string'e dönüştüren bir yardımcı fonksiyon
def decimal_to_str(o):
    if isinstance(o, Decimal):
        return str(o)
    raise TypeError("Object of type 'Decimal' is not JSON serializable")

def save_to_hana_data_set(query_table_name, result_converted):
    try:
        dynamic_table = DynamicTable.objects.get(table_name=query_table_name)
        # Convert Decimal objects to strings
        result_converted = [[decimal_to_str(cell) if isinstance(cell, Decimal) else cell for cell in row] for row in result_converted]
        dynamic_table.hana_data_set = result_converted
        dynamic_table.fetched_at = timezone.now()
        dynamic_table.save()
    except ObjectDoesNotExist:
        with connections['default'].cursor() as local_cursor:
            current_time = timezone.now()
            # decimal_to_str fonksiyonunu default olarak kullan
            local_cursor.execute(
                "INSERT INTO dynamicreport_dynamictable (sql_query_id, table_name, hana_data_set, fetched_at) VALUES (%s, %s, %s, %s)",
                (SqlQuery.objects.get(table_name=query_table_name).id, query_table_name, json.dumps(result_converted, ensure_ascii=False, default=decimal_to_str), current_time)
            )