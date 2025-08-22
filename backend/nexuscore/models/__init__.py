# path: /var/www/sapb1reportsv2/backend/nexuscore/models/__init__.py

# 1. Adım: Her model dosyasından ilgili sınıfları bu paketin ana isim alanına (namespace) taşı.
from .dynamic_connection import DynamicDBConnection
from .virtual_table import VirtualTable, SharingStatus
from .fields import EncryptedJSONField  # <-- YENİ: Özel alanımızı da dahil ediyoruz.

# 2. Adım: __all__ listesini tanımla.
# Bu, `from nexuscore.models import *` komutu çalıştırıldığında hangi isimlerin
# import edileceğini belirleyen bir "beyaz liste" (whitelist) görevi görür.
# Aynı zamanda, bu paketin dış dünyaya sunduğu resmi arayüzü de tanımlar.
__all__ = [
    'DynamicDBConnection',
    'VirtualTable',
    'SharingStatus',
    'EncryptedJSONField',  # <-- YENİ: Özel alanımızı da resmi arayüze ekliyoruz.
]