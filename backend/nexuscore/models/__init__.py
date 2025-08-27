# path: backend/nexuscore/models/__init__.py

from .dynamic_connection import DynamicDBConnection
from .virtual_table import VirtualTable, SharingStatus
from .report_template import ReportTemplate # <-- YENİ: Yeni modelimizi import ediyoruz
from nexuscore.fields import EncryptedJSONField

__all__ = [
    'DynamicDBConnection',
    'VirtualTable',
    'SharingStatus',
    'ReportTemplate', # <-- YENİ: Yeni modelimizi dış dünyaya açıyoruz
    'EncryptedJSONField',
]