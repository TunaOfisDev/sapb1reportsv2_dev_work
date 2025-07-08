# backend/report_orchestrator/utils/time_utils.py

from datetime import datetime, date, time
from dateutil import parser
from zoneinfo import ZoneInfo


# Sistem zamanı için timezone ayarı
IST_TIMEZONE = ZoneInfo("Europe/Istanbul")


def now_tr():
    """
    Türkiye saatine göre şimdiki zamanı döndür.
    """
    return datetime.now(IST_TIMEZONE)


def is_today(dt: datetime) -> bool:
    """
    Verilen datetime objesi bugün mü?
    """
    return dt.date() == now_tr().date()


def is_after_time(dt: datetime, target_hour: int, target_minute: int = 0) -> bool:
    """
    Verilen datetime, örneğin saat 09:00'dan sonra mı?
    """
    limit = time(hour=target_hour, minute=target_minute)
    return dt.time() >= limit


def parse_datetime_safe(value: str) -> datetime:
    """
    ISO string veya HANA formatlı string tarihleri datetime'a dönüştür.
    """
    try:
        return parser.isoparse(value).astimezone(IST_TIMEZONE)
    except Exception:
        raise ValueError(f"Geçersiz datetime formatı: {value}")


def validate_data_timestamp(data: list, created_at_field: str, after_hour: int = 9) -> bool:
    """
    Verideki tüm satırların istenen saatten sonra ve bugüne ait olduğunu kontrol eder.
    """
    for item in data:
        if created_at_field not in item:
            return False

        dt = parse_datetime_safe(item[created_at_field])
        if not is_today(dt) or not is_after_time(dt, after_hour):
            return False

    return True
