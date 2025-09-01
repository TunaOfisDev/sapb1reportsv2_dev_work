# path: backend/nexuscore/services/pivot_manager.py

import logging
from typing import Dict, Any

# Diğer servisimize ve modellerimize ihtiyacımız olacak.
from . import connection_manager
from ..models import ReportTemplate, VirtualTable

logger = logging.getLogger(__name__)

def _quote_identifier(name: str) -> str:
    """
    SQL injection'ı önlemek için kolon adlarını güvenli bir şekilde alıntılar.
    Not: Bu basit bir alıntılama. Veritabanı türüne göre (örn: MySQL ``, MSSQL [])
    daha gelişmiş bir mantık kurulabilir. Şimdilik çift tırnak HANA/PostgreSQL için yeterlidir.
    """
    if '"' in name or '`' in name or '[' in name:
        # Zaten alıntılanmışsa veya potansiyel olarak tehlikeliyse dokunma
        raise ValueError(f"Geçersiz kolon adı: {name}")
    return f'"{name}"'

def generate_pivot_data(report_template: ReportTemplate) -> Dict[str, Any]:
    """
    Bir ReportTemplate'in pivot yapılandırmasını alır, dinamik bir GROUP BY sorgusu oluşturur,
    çalıştırır ve özetlenmiş veriyi döndürür.
    """
    try:
        config = report_template.configuration_json
        source_table = report_template.source_virtual_table

        # --- 1. Adım: Pivot Yapılandırmasını Doğrula ---
        pivot_rows = config.get('rows', [])
        pivot_values = config.get('values', [])
        
        if not pivot_rows or not pivot_values:
            return {"success": False, "error": "Pivot tablo oluşturmak için en az bir 'satır' ve bir 'değer' alanı gereklidir."}

        # --- 2. Adım: Dinamik SQL Sorgusunu Oluştur ---
        base_sql = source_table.sql_query.strip()
        if base_sql.endswith(';'):
            base_sql = base_sql[:-1]

        # SELECT bölümünü oluştur
        select_clauses = [_quote_identifier(row_key) for row_key in pivot_rows]
        
        valid_aggregations = {"SUM", "COUNT", "AVG", "MIN", "MAX"}
        for val_config in pivot_values:
            agg_func = val_config.get('agg', 'SUM').upper()
            if agg_func not in valid_aggregations:
                raise ValueError(f"Geçersiz özetleme fonksiyonu: {agg_func}")
            
            column_key = _quote_identifier(val_config['key'])
            alias = _quote_identifier(f"{agg_func}_{val_config['key']}")
            select_clauses.append(f"{agg_func}({column_key}) AS {alias}")

        select_statement = ", ".join(select_clauses)
        
        # GROUP BY bölümünü oluştur
        group_by_statement = ", ".join([_quote_identifier(row_key) for row_key in pivot_rows])

        # Nihai sorguyu birleştir
        final_sql = f"""
            SELECT {select_statement}
            FROM ({base_sql}) AS nexus_base_query
            GROUP BY {group_by_statement}
            ORDER BY {group_by_statement}
        """

        # --- 3. Adım: Yeni Sorguyu Çalıştır ---
        # connection_manager'ı kullanarak, kaynak tablonun bağlantısıyla yeni sorguyu çalıştır.
        # Bunun için geçici bir VirtualTable nesnesi oluşturmak yerine,
        # connection_manager'a bu işi yapacak yeni bir fonksiyon eklemek daha temiz olur.
        # Şimdilik, mantığı burada doğrudan yeniden kullanalım.
        
        temp_virtual_table = VirtualTable(
            connection=source_table.connection,
            sql_query=final_sql
        )
        
        result = connection_manager.execute_virtual_table_query(temp_virtual_table)
        
        return result

    except Exception as e:
        logger.error(f"Pivot raporu (ID: {report_template.id}) oluşturulurken hata: {e}")
        return {"success": False, "error": f"Pivot raporu işlenirken bir hata oluştu: {str(e)}"}