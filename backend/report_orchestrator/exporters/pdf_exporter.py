# backend/report_orchestrator/exporters/pdf_exporter.py

import os
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings

EXPORT_DIR = os.path.join(settings.BASE_DIR, "data/exports/pdf")



def generate_pdf_from_result(api_name: str, result_json: dict) -> str:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    """
    result_json içeriğine göre PDF dosyası üretir.
    """

    report_title = result_json.get("report_title", api_name)
    report_date = result_json.get("report_date", datetime.today().strftime("%Y-%m-%d"))
    columns = result_json.get("columns") or list(result_json.get("data", [{}])[0].keys())
    data = result_json.get("data", [])
    ara_toplam = result_json.get("ara_toplam")
    kumulatif_toplam = result_json.get("kumulatif_toplam")

    html_content = render_to_string("report_orchestrator/pdf_template.html", {
        "report_title": report_title,
        "report_date": report_date,
        "columns": columns,
        "data": data,
        "ara_toplam": ara_toplam,
        "kumulatif_toplam": kumulatif_toplam,
    })

    filename = f"{api_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    HTML(string=html_content).write_pdf(filepath)
    return filepath
