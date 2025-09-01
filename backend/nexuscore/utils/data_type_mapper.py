# path: backend/nexuscore/utils/data_type_mapper.py

from django.db import connection

def map_db_type_to_general_category(type_code: int) -> str:
    """
    Python DB API 2.0 standardındaki (cursor.description) type_code'ları,
    genel kategorilere ('string', 'number', 'date', 'datetime', 'other') çevirir.
    
    Bu, farklı veritabanları arasındaki tip farklılıklarını soyutlamamızı sağlar.
    """
    # Bu eşleştirme, Django'nun kendi içindeki tiplere dayanmaktadır.
    # PEP 249 -- Python Database API Specification v2.0
    
    # String tipleri
    if type_code in connection.Database.STRING:
        return 'string'
    # Sayısal tipler
    if type_code in connection.Database.NUMBER:
        return 'number'
    # Tarih tipleri
    if type_code in connection.Database.DATE:
        return 'date'
    # Tarih ve Saat tipleri
    if type_code in connection.Database.DATETIME:
        return 'datetime'
    
    return 'other'