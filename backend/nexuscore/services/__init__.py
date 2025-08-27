# path: backend/nexuscore/services/__init__.py

# Adım 1: Her servis modülünden, dış dünyanın kullanacağı
# "public" fonksiyonları import et.
from .connection_manager import (
    test_connection_config,
    execute_virtual_table_query,
    generate_metadata_for_query,
)

from .template_manager import (
    execute_report_template,
)

# Adım 2: __all__ listesini tanımla.
# Bu, `from nexuscore.services import *` komutu çalıştırıldığında
# hangi fonksiyonların import edileceğini belirleyen "beyaz liste"dir.
# Bu, servis paketimizin resmi API'ını tanımlar.
__all__ = [
    # connection_manager.py'dan gelenler
    'test_connection_config',
    'execute_virtual_table_query',
    'generate_metadata_for_query',

    # template_manager.py'dan gelenler
    'execute_report_template',
]