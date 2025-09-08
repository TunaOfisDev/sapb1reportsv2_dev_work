# path: backend/nexuscore/services/pivot_manager.py
import logging
from typing import Dict, Any, List
from decimal import Decimal
from . import connection_manager
from ..models import ReportTemplate, VirtualTable

logger = logging.getLogger(__name__)

def _quote_identifier(name: str) -> str:
    """
    Kolon adlarını veritabanı motorları için güvenli hale getirir (örn: "Satici").
    SQL enjeksiyonunu önlemek için temel bir kontrol yapar.
    """
    if not isinstance(name, str) or '"' in name or '`' in name or '[' in name or ']' in name or ';' in name:
        raise ValueError(f"Geçersiz veya güvenli olmayan kolon adı saptandı: {name}")
    return f'"{name}"'

def _get_sortable_value(value):
    """ (Bu yardımcı fonksiyon aynı kalıyor, sıralama için) """
    if value is None: return (1, float('inf')) 
    if isinstance(value, (int, float, Decimal)): return (0, value)
    return (1, str(value))

def generate_pivot_data(report_template: ReportTemplate) -> Dict[str, Any]:
    """
    Bir Rapor Şablonu alır, pivot yapılandırmasını okur ve dinamik olarak 
    bir GROUP BY SQL sorgusu oluşturup bunu connection_manager aracılığıyla çalıştırır.
    """
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

        # --- DÜZELTME BURADA (1/2) ---
        # pivot_rows bir [{...}, {...}] listesidir. Sadece 'key' değerine ihtiyacımız var.
        # Hatalı kod: [_quote_identifier(row_key) for row_key in pivot_rows]
        select_clauses = [_quote_identifier(row_config['key']) for row_config in pivot_rows]
        # -----------------------------
        
        valid_aggregations = {"SUM", "COUNT", "AVG", "MIN", "MAX"}
        for val_config in pivot_values:
            # Bu döngü zaten doğruydu (val_config['key'] kullanıyordu)
            agg_func = val_config.get('agg', 'SUM').upper()
            if agg_func not in valid_aggregations:
                raise ValueError(f"Geçersiz özetleme fonksiyonu: {agg_func}")
            
            column_key = _quote_identifier(val_config['key'])
            alias = _quote_identifier(f"{agg_func.upper()}_{val_config['key']}")
            select_clauses.append(f"{agg_func}({column_key}) AS {alias}")

        select_statement = ", ".join(select_clauses)
        
        # --- DÜZELTME BURADA (2/2) ---
        # Aynı düzeltmeyi GROUP BY ifadesi için de yapıyoruz.
        # Hatalı kod: ", ".join([_quote_identifier(row_key) for row_key in pivot_rows])
        group_by_statement = ", ".join([_quote_identifier(row_config['key']) for row_config in pivot_rows])
        # -----------------------------

        # Bu dinamik SQL üretimi artık doğru kolon adlarını kullanacaktır.
        # Örn: SELECT "Satici", SUM("Bakiye") ... GROUP BY "Satici" ORDER BY "Satici"
        final_sql = f"SELECT {select_statement} FROM ({base_sql}) AS nexus_base_query GROUP BY {group_by_statement} ORDER BY {group_by_statement}"

        # Sorguyu çalıştırması için connection_manager'a gönderiyoruz.
        # connection_manager sql_query parametresine güvendiği için parametreli sorgu kullanmaz,
        # ancak biz burada kolon adlarını _quote_identifier ile zaten güvenli hale getirdik.
        temp_virtual_table = VirtualTable(
            connection=source_table.connection,
            sql_query=final_sql
        )
        result = connection_manager.execute_virtual_table_query(temp_virtual_table)
        return result

    except Exception as e:
        logger.error(f"Pivot raporu (ID: {report_template.id}) oluşturulurken hata: {e}")
        # API ViewSet bu hatayı yakalayıp 400 Bad Request olarak döndürecek.
        return {"success": False, "error": f"Pivot raporu işlenirken bir hata oluştu: {str(e)}"}