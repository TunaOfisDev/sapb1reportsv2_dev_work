# path: backend/nexuscore/services/pivot_manager.py

import logging
from typing import Dict, Any
from decimal import Decimal

from . import connection_manager, data_app_manager
from ..models import ReportTemplate, VirtualTable

logger = logging.getLogger(__name__)

# data_app_manager'dan _quote_identifier fonksiyonunu import ediyoruz.
# Bu, kod tekrarını (DRY ilkesi) önler.
from .data_app_manager import _quote_identifier

def generate_pivot_data(report_template: ReportTemplate) -> Dict[str, Any]:
    """
    Bir Rapor Şablonunu alır, ilişkili DataApp'i analiz eder,
    pivot yapılandırmasını uygular ve hem nihai veriyi hem de
    bu veriye ait meta veriyi döndürür.
    """
    try:
        config = report_template.configuration_json
        source_app = report_template.source_data_app
        if not source_app:
            return {"success": False, "error": "Rapor geçerli bir Veri Uygulamasına bağlı değil."}
        
        source_connection = source_app.connection

        # İYİLEŞTİRME: DataApp'ten sorgu bileşenlerini alırken oluşabilecek
        # hataları daha spesifik bir şekilde yakalıyoruz.
        try:
            cte_clause, from_join_clause = data_app_manager.get_data_app_query_components(source_app)
        except ValueError as e:
            logger.warning(f"DataApp sorgusu oluşturulamadı (App ID: {source_app.id}): {e}")
            return {"success": False, "error": f"Veri modeli sorgusu oluşturulamadı: {str(e)}"}

        pivot_config = config.get('pivot_config', {})
        pivot_rows = pivot_config.get('rows', [])
        pivot_values = pivot_config.get('values', [])
        pivot_columns = pivot_config.get('columns', []) 
        all_dimensions = pivot_rows + pivot_columns
        
        select_statement: str
        group_by_clause = "" # Varsayılan olarak GROUP BY yok

        if not all_dimensions or not pivot_values:
            # Durum 1: Pivot ayarı yok (Detay Raporu)
            # Tüm kolonları seçiyoruz.
            select_statement = "SELECT *"
        else:
            # Durum 2: Pivot Raporu
            # Boyutları (dimensions) ve hesaplamaları (aggregations) oluştur.
            select_clauses = [_quote_identifier(dim_config['key']) for dim_config in all_dimensions]
            
            valid_aggregations = {"SUM", "COUNT", "AVG", "MIN", "MAX"}
            for val_config in pivot_values:
                agg_func = val_config.get('agg', 'SUM').upper()
                if agg_func not in valid_aggregations: 
                    raise ValueError(f"Geçersiz özetleme fonksiyonu: {agg_func}")
                
                column_key = _quote_identifier(val_config['key'])
                alias = _quote_identifier(f"{agg_func}_{val_config['key']}")
                select_clauses.append(f"{agg_func}({column_key}) AS {alias}")
            
            select_statement = "SELECT " + ", ".join(select_clauses)
            group_by_clause = "GROUP BY " + ", ".join([_quote_identifier(dim_config['key']) for dim_config in all_dimensions])

        # DÜZELTME: Nihai SQL sorgusunu hatasız bir şekilde birleştiriyoruz.
        # Artık gereksiz alt sorgu veya çift 'FROM' ifadesi yok.
        final_sql = f"{cte_clause}\n{select_statement}\n{from_join_clause}\n{group_by_clause}"

        # --- Meta Veriyi Nihai Sorgudan Üretme ---
        metadata_result = connection_manager.generate_metadata_for_query(source_connection, final_sql)
        
        if not metadata_result.get('success'):
            logger.warning(f"Rapor (ID: {report_template.id}) için meta veri üretilemedi: {metadata_result.get('error')}")
            final_metadata = {}
        else:
            final_metadata = metadata_result.get('metadata', {})
        
        # --- Veriyi Çekme ---
        # Sorguyu çalıştırmak için geçici bir VirtualTable nesnesi kullanıyoruz.
        temp_virtual_table = VirtualTable(connection=source_connection, sql_query=final_sql)
        result = connection_manager.execute_virtual_table_query(temp_virtual_table)
        
        # --- Sonucu Birleştirme ---
        # Veri başarıyla çekildiyse, meta veriyi de yanıta ekliyoruz.
        if result.get('success'):
            result['metadata'] = final_metadata
            
        return result

    except Exception as e:
        # Beklenmedik tüm hataları loglayıp kullanıcıya genel bir mesaj dönüyoruz.
        logger.error(f"Pivot raporu (ID: {report_template.id}) oluşturulurken kritik hata: {e}", exc_info=True)
        return {"success": False, "error": f"Rapor işlenirken sunucuda beklenmedik bir hata oluştu."}