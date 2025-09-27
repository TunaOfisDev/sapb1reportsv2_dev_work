# File: backend/report_orchestrator/rules/rule_engine.py

from typing import List, Dict, Any
from collections import defaultdict
import re

def apply_rules(data: List[Dict[str, Any]], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    rule_json'a göre veri kümesini işler:
    - filtre uygular
    - sıralar
    - limit/top uygular
    - alan seçimi yapar
    - sayısal alanlar için ara toplam ve kümülatif toplam döner
    - retry_attempts ve retry_interval gibi operational configleri doğrular (işlemez)
    """
    original_data = data.copy()
    filters = rules.get("filters", {})
    sort_by = rules.get("sort_field") or rules.get("sort_by")  
    sort_order = rules.get("sort_order", "asc")
    limit = rules.get("top") or rules.get("limit")
    selected_fields = rules.get("fields")

    # Operational config validation
    retry_attempts = rules.get("retry_attempts")
    retry_interval = rules.get("retry_interval")
    if retry_attempts is not None and not isinstance(retry_attempts, int):
        raise ValueError("retry_attempts must be an integer")
    if retry_interval is not None and not isinstance(retry_interval, int):
        raise ValueError("retry_interval must be an integer")

    # 1. Filtreleme
    for field, condition in filters.items():
        if isinstance(condition, dict):
            for operator, value in condition.items():
                if operator == "gt":
                    data = [item for item in data if _to_float(item.get(field, 0)) > value]
                elif operator == "lt":
                    data = [item for item in data if _to_float(item.get(field, 0)) < value]
                elif operator == "eq":
                    data = [item for item in data if item.get(field) == value]
        else:
            data = [item for item in data if item.get(field) == condition]

    # 2. Sıralama
    if sort_by:
        data.sort(key=lambda x: _to_float(x.get(sort_by, 0)), reverse=(sort_order == "desc"))

    # 3. Limit (Top)
    if limit and isinstance(limit, int):
        data = data[:limit]

    # 4. Alan seçimi (fields)
    if selected_fields:
        data = [
            {field: item.get(field) for field in selected_fields}
            for item in data
        ]

    # 5. Sayısal alanları belirle
    def get_numeric_fields(sample: List[Dict[str, Any]]) -> List[str]:
        if not sample:
            return []
        ignore_fields = {"MuhatapKod", "VergiNo", "IBAN", "Telefon", "Satici", "Grup", "MuhatapAd"}
        return [
            key for key, val in sample[0].items()
            if key not in ignore_fields and _is_numeric(val)
        ]

    numeric_fields = get_numeric_fields(data)

    # 6. Toplamları hesapla
    subtotal = defaultdict(float)
    cumulative_total = defaultdict(float)

    for item in data:
        for field in numeric_fields:
            subtotal[field] += _to_float(item.get(field, 0))

    for item in original_data:
        for field in numeric_fields:
            cumulative_total[field] += _to_float(item.get(field, 0))

    return {
        "filtered_data": data,
        "totals": {
            "subtotal": dict(subtotal),
            "cumulative": dict(cumulative_total)
        }
    }

def _is_numeric(val: Any) -> bool:
    try:
        float(str(val).replace('.', '').replace(',', '.'))
        return True
    except:
        return False

def _to_float(val: Any) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    try:
        val_str = str(val)
        val_str = re.sub(r"[^\d,.-]", "", val_str)
        if ',' in val_str and val_str.count(',') == 1 and '.' not in val_str:
            val_str = val_str.replace(',', '.')
        elif val_str.count('.') > 1:
            val_str = val_str.replace('.', '')
        return float(val_str)
    except:
        return 0.0
