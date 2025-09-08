# path: backend/nexuscore/services/pivot_manager.py

import logging
from typing import Dict, Any, List
from decimal import Decimal

# Yeni servisimize ve güncellenmiş modellerimize ihtiyacımız var
from . import connection_manager, data_app_manager
from ..models import ReportTemplate, VirtualTable # VirtualTable hala lazım (execute için)

logger = logging.getLogger(__name__)

# _quote_identifier fonksiyonu artık data_app_manager içinde (veya idealde utils'da)
# Burada DRY (Don't Repeat Yourself) ilkesi için ona güvendiğimizi varsayıyoruz 
# veya buradan data_app_manager._quote_identifier olarak import edebiliriz.
# Şimdilik data_app_manager'daki kopyayı kullanalım.
from .data_app_manager import _quote_identifier 


def _get_sortable_value(value):
    """ (Bu yardımcı fonksiyon aynı kalıyor) """
    if value is None: return (1, float('inf')) 
    if isinstance(value, (int, float, Decimal)): return (0, value)
    return (1, str(value))


def generate_pivot_data(report_template: ReportTemplate) -> Dict[str, Any]:
    """
    BİR RAPOR ŞABLONUNU ALIR (YENİ SİSTEM).
    Raporun bağlı olduğu DataApp'i okur, data_app_manager'ı kullanarak 
    base SQL sorgusunu (CTE'ler ve JOIN'ler dahil) oluşturur.
    SONRA, bu base SQL'in üzerine pivot yapılandırmasını (GROUP BY) uygular.
    """
    try:
        config = report_template.configuration_json
        
        # ### DEĞİŞİKLİK BAŞLANGICI ###
        # Artık tek bir VirtualTable kaynağımız yok, bir DataApp kaynağımız var.
        source_app = report_template.source_data_app
        if not source_app:
            return {"success": False, "error": "Bu rapor şablonu geçerli bir Veri Uygulamasına bağlı değil."}
        
        # Ana bağlantı, artık uygulama üzerinden geliyor.
        source_connection = source_app.connection

        # 1. Beyin'i (data_app_manager) çağır ve base SQL parçalarını al
        try:
            cte_clause, from_join_clause = data_app_manager.get_data_app_query_components(source_app)
        except ValueError as e:
            logger.warning(f"DataApp sorgusu oluşturulamadı (App ID: {source_app.id}): {e}")
            return {"success": False, "error": f"Veri modeli sorgusu oluşturulamadı: {str(e)}"}

        # Artık base_sql dediğimiz şey, tek bir sorgu değil, bir JOIN zinciridir.
        # Pivot sorgumuzun FROM kısmı, bu alt sorgu olmalı.
        base_sql = f"SELECT * FROM (\n  {from_join_clause}\n) AS nexus_data_app_base"
        
        # CTE'leri de sorgunun başına eklememiz gerekiyor!
        base_query_with_cte = f"{cte_clause}\n{base_sql}"
        
        # ### DEĞİŞİKLİK SONU ###

        pivot_config = config.get('pivot_config', {})
        pivot_rows = pivot_config.get('rows', [])
        pivot_values = pivot_config.get('values', [])
        pivot_columns = pivot_config.get('columns', []) 
        
        all_dimensions = pivot_rows + pivot_columns 
        
        if not all_dimensions or not pivot_values:
            return {"success": False, "error": "Pivot tablo için en az bir 'boyut' (satır/sütun) ve bir 'değer' alanı gereklidir."}

        # Kalan mantık (GROUP BY ve SELECT cümlelerinin oluşturulması) aynı kalır,
        # çünkü base_sql'imiz (base_query_with_cte) zaten birleşik bir tablo gibi davranır.

        select_clauses = [_quote_identifier(dim_config['key']) for dim_config in all_dimensions]
        
        valid_aggregations = {"SUM", "COUNT", "AVG", "MIN", "MAX"}
        for val_config in pivot_values:
            agg_func = val_config.get('agg', 'SUM').upper()
            if agg_func not in valid_aggregations:
                raise ValueError(f"Geçersiz özetleme fonksiyonu: {agg_func}")
            
            column_key = _quote_identifier(val_config['key'])
            alias = _quote_identifier(f"{agg_func.upper()}_{val_config['key']}")
            select_clauses.append(f"{agg_func}({column_key}) AS {alias}")

        select_statement = ", ".join(select_clauses)
        
        group_by_statement = ", ".join([_quote_identifier(dim_config['key']) for dim_config in all_dimensions])
        order_by_statement = group_by_statement or "1" 

        # Nihai SQL sorgusunu, CTE'leri de içerecek şekilde oluştur
        final_sql = f"{cte_clause}\nSELECT {select_statement} FROM ({from_join_clause}) AS nexus_base_query GROUP BY {group_by_statement} ORDER BY {order_by_statement}"
        
        # Sorguyu çalıştır
        # Geçici Sanal Tablo oluşturup doğru bağlantıyı (App'in bağlantısı) kullanıyoruz.
        temp_virtual_table = VirtualTable(
            connection=source_connection, # <-- Doğru bağlantıyı kullandığımızdan emin olalım
            sql_query=final_sql
        )
        result = connection_manager.execute_virtual_table_query(temp_virtual_table)
        return result

    except Exception as e:
        logger.error(f"Pivot raporu (ID: {report_template.id}) oluşturulurken hata: {e}")
        return {"success": False, "error": f"Pivot raporu işlenirken bir hata oluştu: {str(e)}"}