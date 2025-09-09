# path: backend/nexuscore/services/data_app_manager.py

import logging
from typing import Dict, Any, List, Tuple, Set
from ..models import DataApp, VirtualTable, AppRelationship

logger = logging.getLogger(__name__)

def _quote_identifier(name: str) -> str:
    """
    (Pivot Manager'dan kopyalandı - ideal olarak bu utils'a taşınmalı)
    Kolon adlarını güvenli hale getirir. SQL enjeksiyonuna karşı temel kontrol.
    """
    if not isinstance(name, str) or any(c in name for c in '"`[];'):
        raise ValueError(f"Geçersiz veya güvenli olmayan kolon adı saptandı: {name}")
    return f'"{name}"'


def get_data_app_query_components(data_app: DataApp) -> Tuple[str, str]:
    """
    Bir DataApp nesnesini alır ve onu oluşturan iki ana SQL bileşenini döndürür:
    1. CTE (WITH) Cümlesi: Tüm sanal tabloları CTE olarak tanımlar.
    2. FROM/JOIN Cümlesi: İlişkilere dayalı tam JOIN zincirini oluşturur.
    
    Bu iki bileşen, pivot_manager tarafından alınarak nihai sorguyu oluşturmak için kullanılacaktır.
    """
    
    # 1. İlişkili tüm tabloları ve ilişkileri çek
    # .order_by('id') önemlidir, bize tutarlı bir sorgu oluşturma sırası verir.
    tables = data_app.virtual_tables.all().order_by('id')
    relations = data_app.relationships.select_related(
        'left_table', 
        'right_table'
    ).order_by('id')

    if not tables.exists():
        raise ValueError(f"DataApp (ID: {data_app.id}) içinde hiç sanal tablo bulunmuyor.")

    # 2. Alias (Takma Ad) Haritası Oluştur
    # Her VirtualTable'a benzersiz ve tutarlı bir SQL alias'ı atayalım (Örn: "NEXUS_T12")
    alias_map: Dict[int, str] = {
        tbl.id: f"NEXUS_T{tbl.id}" for tbl in tables
    }

    # 3. CTE (WITH) Cümlesini Oluştur
    cte_parts = []
    for tbl in tables:
        alias = alias_map[tbl.id]
        clean_sql = tbl.sql_query.strip().rstrip(';')
        cte_parts.append(f"  {alias} AS (\n    {clean_sql}\n  )")
    
    cte_clause = "WITH \n" + ",\n".join(cte_parts)

    # 4. FROM/JOIN Cümlesini Oluştur
    from_join_clause = ""
    
    if not relations.exists():
        # İlişki yoksa, sadece tek tablo vardır (varsayıyoruz)
        if tables.count() == 1:
            from_join_clause = f"FROM {alias_map[tables.first().id]}"
        else:
            # Birden fazla tablo var ama ilişki yoksa, bu bir Kartezyen Çarpım olur.
            # Buna izin vermeyelim veya uyarı verelim. Şimdilik ilk tabloyu temel alalım.
            logger.warning(f"DataApp (ID: {data_app.id}) ilişkisiz birden fazla tablo içeriyor. Sadece ilk tablo kullanılacak.")
            from_join_clause = f"FROM {alias_map[tables.first().id]}"
    else:
        # İlişki zincirini oluştur
        join_parts = []
        
        # İlk ilişkinin sol tablosu bizim ana FROM tablomuzdur.
        first_rel = relations.first()
        base_from_table_alias = alias_map.get(first_rel.left_table_id)
        if not base_from_table_alias:
            raise ValueError("İlişkide tanımlı sol tablo, uygulama tabloları arasında bulunamadı.")

        from_join_clause = f"FROM {base_from_table_alias}"
        
        # Şimdi TÜM ilişkileri sırayla zincire ekle
        for rel in relations:
            left_alias = alias_map.get(rel.left_table_id)
            right_alias = alias_map.get(rel.right_table_id)
            
            if not left_alias or not right_alias:
                logger.error(f"Eksik ilişki verisi atlanıyor (Rel ID: {rel.id})")
                continue

            left_col = _quote_identifier(rel.left_column)
            right_col = _quote_identifier(rel.right_column)
            join_type = rel.join_type # Modelde "LEFT JOIN" vb. olarak saklanıyor

            join_parts.append(
                f"  {join_type} {right_alias} ON {left_alias}.{left_col} = {right_alias}.{right_col}"
            )
        
        from_join_clause += "\n" + "\n".join(join_parts)

    return cte_clause, from_join_clause