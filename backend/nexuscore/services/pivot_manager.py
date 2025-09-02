# path: backend/nexuscore/services/pivot_manager.py
import logging
from typing import Dict, Any, List
from decimal import Decimal
from . import connection_manager
from ..models import ReportTemplate, VirtualTable

logger = logging.getLogger(__name__)

def _quote_identifier(name: str) -> str:
    # ... (bu yardımcı fonksiyon aynı kalıyor) ...
    if '"' in name or '`' in name or '[' in name:
        raise ValueError(f"Geçersiz kolon adı: {name}")
    return f'"{name}"'

def _get_sortable_value(value):
    # ... (bu yardımcı fonksiyon aynı kalıyor) ...
    if value is None: return (1, float('inf')) 
    if isinstance(value, (int, float, Decimal)): return (0, value)
    return (1, str(value))

def generate_pivot_data(report_template: ReportTemplate) -> Dict[str, Any]:
    try:
        config = report_template.configuration_json
        source_table = report_template.source_virtual_table
        
        pivot_config = config.get('pivot_config', {})
        pivot_rows = pivot_config.get('rows', [])
        pivot_values = pivot_config.get('values', [])
        
        if not pivot_rows or not pivot_values:
            return {"success": False, "error": "Pivot tablo için en az bir 'satır' ve bir 'değer' alanı gereklidir."}

        base_sql = source_table.sql_query.strip()
        if base_sql.endswith(';'):
            base_sql = base_sql[:-1]

        select_clauses = [_quote_identifier(row_key) for row_key in pivot_rows]
        
        # ### GÜNCELLEME: Dinamik Özetleme Fonksiyonları ###
        valid_aggregations = {"SUM", "COUNT", "AVG", "MIN", "MAX"}
        for val_config in pivot_values:
            agg_func = val_config.get('agg', 'SUM').upper()
            if agg_func not in valid_aggregations:
                raise ValueError(f"Geçersiz özetleme fonksiyonu: {agg_func}")
            
            column_key = _quote_identifier(val_config['key'])
            alias = _quote_identifier(f"{agg_func}_{val_config['key']}")
            select_clauses.append(f"{agg_func}({column_key}) AS {alias}")

        select_statement = ", ".join(select_clauses)
        group_by_statement = ", ".join([_quote_identifier(row_key) for row_key in pivot_rows])

        final_sql = f"SELECT {select_statement} FROM ({base_sql}) AS nexus_base_query GROUP BY {group_by_statement} ORDER BY {group_by_statement}"

        # Geçici bir VirtualTable nesnesi oluşturup connection_manager'ı kullanıyoruz.
        temp_virtual_table = VirtualTable(
            connection=source_table.connection,
            sql_query=final_sql
        )
        result = connection_manager.execute_virtual_table_query(temp_virtual_table)
        return result

    except Exception as e:
        logger.error(f"Pivot raporu (ID: {report_template.id}) oluşturulurken hata: {e}")
        return {"success": False, "error": f"Pivot raporu işlenirken bir hata oluştu: {str(e)}"}