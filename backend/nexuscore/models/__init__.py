# path: backend/nexuscore/models/__init__.py

from .dynamic_connection import DynamicDBConnection
from .virtual_table import VirtualTable, SharingStatus
from .data_app import DataApp  # <-- YENİ: Veri Uygulaması modelimiz
from .app_relationship import AppRelationship, JoinType  # <-- YENİ: İlişki modelimiz ve Enum
from .report_template import ReportTemplate
from nexuscore.fields import EncryptedJSONField

__all__ = [
    'DynamicDBConnection',
    'VirtualTable',
    'SharingStatus',
    'DataApp',          # <-- YENİ
    'AppRelationship',  # <-- YENİ
    'JoinType',         # <-- YENİ (JoinType Enum'u da dışarı açıyoruz)
    'ReportTemplate',
    'EncryptedJSONField',
]