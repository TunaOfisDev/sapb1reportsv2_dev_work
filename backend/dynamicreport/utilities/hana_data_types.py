# backend\dynamicreport\hana_data_types.py
from ..models.models import HanaDataType
from decimal import Decimal
import datetime

# Cache for Hana data types
hana_data_types_cache = None

# Date, Datetime ve Decimal için formatlama fonksiyonları
def format_date(value):
    return value.strftime('%d-%m-%Y')

def format_datetime(value):
    return value.strftime('%d-%m-%Y %H:%M')

def format_decimal(value):
    try:
        # Virgül ile binlik ayracı eklemek için "{:,.2f}" formatını kullanıyoruz.
        formatted_value = "{:,.2f}".format(value)
        # Türk formatına dönüştürmek için virgül ve nokta yerlerini değiştiriyoruz.
        formatted_value = formatted_value.replace(',', ' ').replace('.', ',').replace(' ', '.')
        return formatted_value
    except Exception as e:
        print(f"Decimal biçimlendirilirken bir hata oluştu: {str(e)}")
        return str(value)

def format_double(value):
    try:
        # Virgül ile binlik ayracı eklemek için "{:,.2f}" formatını kullanıyoruz.
        formatted_value = "{:,.2f}".format(value)
        # Türk formatına dönüştürmek için virgül ve nokta yerlerini değiştiriyoruz.
        formatted_value = formatted_value.replace(',', ' ').replace('.', ',').replace(' ', '.')
        return formatted_value
    except Exception as e:
        print(f"Decimal biçimlendirilirken bir hata oluştu: {str(e)}")
        return str(value)

def detect_hana_data_type(value, column_name=None):
    global hana_data_types_cache
    if hana_data_types_cache is None:
        hana_data_types_cache = HanaDataType.objects.all()
    
    # Eğer sütun adı "PicturName" ise ve değer bir string ise nVarChar tipini döndür
    if column_name == "PicturName" and isinstance(value, str):
        return next((hana_type for hana_type in hana_data_types_cache if hana_type.type_code == 'nvarchar'), None)
    
    detected_type = None
    for hana_type in hana_data_types_cache:
        type_code = hana_type.type_code

       
        if type_code == 'varchar' and isinstance(value, str):
            return hana_type
        elif type_code == 'varbinary' and isinstance(value, bytes):
            return hana_type
        elif type_code == 'tinyint' and isinstance(value, int) and -128 <= value <= 127:
            return hana_type
        elif type_code == 'timestamp' and isinstance(value, datetime.datetime):
            return hana_type
        elif type_code == 'time' and isinstance(value, datetime.time):
            return hana_type
        elif type_code == 'text' and isinstance(value, str):
            return hana_type
        elif type_code == 'st_point' and isinstance(value, str):
            return hana_type
        elif type_code == 'st_geometry' and isinstance(value, str):
            return hana_type
        elif type_code == 'smallint' and isinstance(value, int) and -32768 <= value <= 32767:
            return hana_type
        elif type_code == 'smalldecimal' and isinstance(value, Decimal):
            return hana_type
        elif type_code == 'shorttext' and isinstance(value, str):
            return hana_type
        elif type_code == 'seconddate' and isinstance(value, datetime.datetime):
            return hana_type
        elif type_code == 'real' and isinstance(value, float):
            return hana_type
        elif type_code == 'nvarchar' and isinstance(value, str):
            return hana_type
        elif type_code == 'nclob' and isinstance(value, str):
            return hana_type
        elif type_code == 'integer' and isinstance(value, int) and -2147483648 <= value <= 2147483647:
            return hana_type
        elif type_code == 'double' and isinstance(value, float):
            return hana_type
        elif type_code == 'decimal' and isinstance(value, Decimal):
            return hana_type
        elif type_code == 'date' and isinstance(value, datetime.date):
            return hana_type
        elif type_code == 'clob' and isinstance(value, str):
            return hana_type
        elif type_code == 'boolean' and isinstance(value, bool):
            return hana_type
        elif type_code == 'blob' and isinstance(value, bytes):
            return hana_type
        elif type_code == 'bigint' and isinstance(value, int) and -9223372036854775808 <= value <= 9223372036854775807:
            return hana_type
        elif type_code == 'array' and isinstance(value, list):
            return hana_type
        elif type_code == 'alphanum' and isinstance(value, str):
            return hana_type
    
        elif type_code == 'alphanum' and isinstance(value, str):
                detected_type = hana_type
                break  # Tip bulundu, döngüyü kes
    
    # Yeni eklenen kontrol
    if detected_type and not isinstance(detected_type.type_code, str):
        print(f"Uyarı: {column_name} için algılanan Hana tipi bir string değil. Tip: {type(detected_type.type_code)}")
        return None  # Eğer tip string değilse None döndür


    return None  # Tanınmayan tipler için None döndür

# HanaDataType modelinden alınan tipler için bir sözlük oluşturun
def load_hana_type_formatters():
    hana_type_formatters = {}
    hana_data_types = HanaDataType.objects.all()

    for hana_type in hana_data_types:
        type_code = hana_type.type_code
        formatter_function_name = hana_type.formatter_function_name
        # globals() fonksiyonu ile global kapsamdaki fonksiyonu al
        formatter = globals().get(formatter_function_name, lambda x: x)
        hana_type_formatters[type_code] = formatter

    return hana_type_formatters


# Yüklü tip biçimlendiricilerini saklayacak bir cache
hana_type_formatters_cache = None

def format_value_according_to_type(value, type_code):
    global hana_type_formatters_cache
    if hana_type_formatters_cache is None:
        hana_type_formatters_cache = load_hana_type_formatters()

    formatter = hana_type_formatters_cache.get(type_code, lambda x: x)
    
    try:
        return formatter(value)
    except Exception as e:
        print(f"Error formatting value: {e}")
        return value