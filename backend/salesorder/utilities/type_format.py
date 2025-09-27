# backend/salesorder/utilities/type_format.py

from datetime import datetime

def format_date(value):
    """Tarih verilerini formatlar. Gelen değer string ise doğrudan döndürür."""
    # Eğer value zaten string tipinde ve doğru formatta ise, doğrudan döndür
    if isinstance(value, str):
        try:
            # Önce gelen formatı kontrol et, eğer 'DD.MM.YYYY' formatında ise doğrudan döndür
            datetime.strptime(value, '%d.%m.%Y')
            return value
        except ValueError:
            # Eğer format hatalıysa, hata mesajı döndür veya None döndür
            return None  # veya 'Hatalı Format'
    elif hasattr(value, 'strftime'):
        # Eğer value datetime nesnesi ise, formatla ve döndür
        return value.strftime('%d.%m.%Y')
    else:
        return None

def format_datetime(value):
    """Datetime verilerini formatlar."""
    return value.strftime('%d-%m-%Y %H:%M') if value else ''

def format_float(value):
    """Float verilerini Türkçe formatlar."""
    try:
        formatted_value = "{:,.2f}".format(value)
        # Türk formatına dönüştürmek için virgül ve nokta yerlerini değiştiriyoruz.
        return formatted_value.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    except Exception as e:
        print(f"Float biçimlendirilirken hata: {str(e)}")
        return str(value) if value is not None else ''


def format_decimal(value):
    """Decimal verilerini Türkçe formatlar."""
    try:
        formatted_value = "{:,.2f}".format(value)
        return formatted_value.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    except Exception as e:
        print(f"Decimal biçimlendirilirken hata: {str(e)}")
        return str(value) if value is not None else ''    


def format_value_according_to_type(value, data_type):
    """Verilen değeri, belirtilen veri tipine göre formatlar."""
    if data_type == 'date':
        return format_date(value)
    elif data_type == 'datetime':
        return format_datetime(value)
    elif data_type in ['decimal', 'smalldecimal', 'float', 'double', 'real']:
        return format_decimal(value)

    else:
        return value