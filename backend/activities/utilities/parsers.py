# backend/activities/utilities/parsers.py
from datetime import datetime, date, time

def parse_date(raw):
    if not raw or raw in {"-", ""}:     # None, boş veya '-' ise
        return None
    return datetime.strptime(raw, "%d.%m.%Y").date()

def parse_time(raw):
    if not raw or raw in {"-", ""}:
        return None
    return datetime.strptime(raw, "%H:%M").time()

def parse_datetime(raw):
    if not raw or raw in {"-", ""}:
        return None
    return datetime.strptime(raw, "%d.%m.%Y %H:%M")   # DD.MM.YYYY HH:MM
