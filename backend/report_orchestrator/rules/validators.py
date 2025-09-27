# backend/report_orchestrator/rules/validators.py

from typing import List, Dict, Any
from report_orchestrator.utils.time_utils import parse_datetime_safe, is_today, is_after_time


def validate_data_freshness(data: List[Dict[str, Any]], rules: Dict[str, Any]) -> bool:
    """
    Gelen özet verinin güncelliğini kontrol eder:
    - created_at alanı bugünün tarihi mi?
    - belirtilen saatten sonra mı oluşturulmuş?
    """

    validation = rules.get("validation", {})
    created_at_field = validation.get("created_at_field", "createdAt")
    must_be_today = validation.get("date_must_be", "today") == "today"
    hour_after = validation.get("hour_must_be_after", "09:00")

    try:
        hour_parts = [int(x) for x in hour_after.split(":")]
        required_hour = hour_parts[0]
        required_minute = hour_parts[1] if len(hour_parts) > 1 else 0
    except Exception:
        required_hour = 9
        required_minute = 0

    for item in data:
        raw = item.get(created_at_field)
        if not raw:
            return False

        try:
            dt = parse_datetime_safe(raw)
        except Exception:
            return False

        if must_be_today and not is_today(dt):
            return False

        if not is_after_time(dt, required_hour, required_minute):
            return False

    return True
