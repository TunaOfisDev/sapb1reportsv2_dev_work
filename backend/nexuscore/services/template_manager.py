# path: backend/nexuscore/services/template_manager.py

import logging
from typing import Dict, Any, List
from decimal import Decimal
# Diğer servisimize ve modellerimize ihtiyacımız olacak.
from . import connection_manager
from ..models import ReportTemplate

logger = logging.getLogger(__name__)

def _get_sortable_value(value):
    """
    Sıralama için None değerlerini ve farklı tipleri güvenli bir şekilde ele alır.
    None değerleri en sona atılır.
    """
    if value is None:
        # Python'da None diğer her şeyden küçük olduğu için, büyük bir değerle değiştirerek
        # ters sıralamada en başa, normal sıralamada en sona gelmesini sağlarız.
        return (1, float('inf')) 
    if isinstance(value, (int, float, Decimal)):
        return (0, value)
    return (1, str(value))


def execute_report_template(report_template: ReportTemplate) -> Dict[str, Any]:
    """
    Bir ReportTemplate nesnesini alır, kaynak veriyi çeker, yapılandırmayı
    (kolon seçimi, sıralama vb.) bu veriye uygular ve nihai raporu oluşturur.
    """
    try:
        # 1. Adım: Kaynak Veriyi Çek
        source_table = report_template.source_virtual_table
        raw_data_result = connection_manager.execute_virtual_table_query(source_table)
        
        if not raw_data_result.get('success'):
            return raw_data_result

        original_columns = raw_data_result.get('columns', [])
        original_rows = raw_data_result.get('rows', [])
        
        # 2. Adım: Yapılandırmayı Al
        config = report_template.configuration_json
        if not config:
            return raw_data_result
            
        # 3. Adım: Veriyi Sırala (Eğer sıralama kuralı varsa)
        sort_rule = config.get('sort_by')
        sorted_rows = original_rows

        if sort_rule and sort_rule.get('key') in original_columns:
            try:
                sort_column_index = original_columns.index(sort_rule['key'])
                is_reverse = sort_rule.get('direction', 'asc').lower() == 'desc'
                
                # lambda fonksiyonu ile belirtilen kolona göre sıralama yap
                sorted_rows = sorted(
                    original_rows, 
                    key=lambda row: _get_sortable_value(row[sort_column_index]), 
                    reverse=is_reverse
                )
            except (ValueError, IndexError) as e:
                logger.warning(f"Rapor (ID: {report_template.id}) için sıralama kuralı uygulanamadı: {e}")
                # Sıralama başarısız olursa, sırasız devam et.
                sorted_rows = original_rows

        # 4. Adım: Kolonları Yapılandırmaya Göre Filtrele ve Yeniden Sırala
        template_columns = config.get('columns', [])
        col_index_map = {col_name: i for i, col_name in enumerate(original_columns)}
        
        final_columns = []
        final_col_indices = []
        
        for col_config in template_columns:
            if col_config.get('visible') and col_config.get('key') in col_index_map:
                final_columns.append(col_config.get('label', col_config.get('key')))
                final_col_indices.append(col_index_map[col_config.get('key')])
        
        # Satırları yeni kolon yapısına göre yeniden oluştur.
        final_rows = []
        for row in sorted_rows: # Artık sıralanmış satırları kullanıyoruz
            new_row = [row[i] for i in final_col_indices]
            final_rows.append(new_row)
        
        return {
            "success": True, 
            "columns": final_columns, 
            "rows": final_rows
        }

    except Exception as e:
        logger.error(f"Rapor şablonu (ID: {report_template.id}) çalıştırılırken hata: {e}")
        return {"success": False, "error": f"Rapor işlenirken bir hata oluştu: {str(e)}"}