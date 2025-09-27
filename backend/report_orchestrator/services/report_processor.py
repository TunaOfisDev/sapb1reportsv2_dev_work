# backend/report_orchestrator/services/report_processor.py


from report_orchestrator.rules.rule_engine import apply_rules
from report_orchestrator.utils.time_utils import now_tr
from report_orchestrator.models.api_report_model import APIReportModel

def process_report_data(api_name: str, raw_data: list, rule_json: dict) -> dict:
    """
    Pasif modda veya işlenmemiş ham veriyi alan modlarda:
    - Veriyi rule_engine'e sokar
    - Sıralar, filtreler, toplar
    - Final JSON yapısını hazırlar (result_json)
    """
    processed = apply_rules(raw_data, rule_json)

    # APIReportModel'den `extra_headers` alınıyor
    try:
        report = APIReportModel.objects.get(api_name=api_name)
        extra_headers = report.extra_headers  # Yeni alan alındı
    except APIReportModel.DoesNotExist:
        extra_headers = {}

    return {
        "report_date": now_tr().strftime("%Y-%m-%d"),
        "api_name": api_name,
        "data": processed["filtered_data"],
        "subtotal": processed["subtotal"],
        "cumulative_total": processed["cumulative_total"],
        "extra_headers": extra_headers  # İşlenmiş veriye `extra_headers` eklendi
    }
