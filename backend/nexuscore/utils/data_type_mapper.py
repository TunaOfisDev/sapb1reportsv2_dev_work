# path: backend/nexuscore/utils/data_type_mapper.py

from ..models import DBTypeMapping
from django.db.utils import IntegrityError
import logging

logger = logging.getLogger(__name__)

def _get_source_type_from_info(type_info: any) -> str:
    """Gelen tip bilgisini stringe çevirir."""
    if isinstance(type_info, int):
        return str(type_info)
    if hasattr(type_info, 'id') and isinstance(type_info.id, int):
        return str(type_info.id)
    if hasattr(type_info, 'name') and isinstance(type_info.name, str):
        return type_info.name
    return str(type_info)

def get_type_mapping(db_type: str, type_info: any) -> str:
    """
    Veritabanından gelen tip bilgisini alarak eşleştirmeyi çeker.
    Eğer eşleşme yoksa, yeni bir kayıt oluşturur ve 'other' döndürür.
    """
    source_type_str = _get_source_type_from_info(type_info)
    
    try:
        mapping = DBTypeMapping.objects.get(db_type=db_type, source_type=source_type_str)
        return mapping.general_category
    except DBTypeMapping.DoesNotExist:
        # Eşleşme yoksa, bir sonraki adımı tetiklemek için diğer olarak döneriz
        return 'other'