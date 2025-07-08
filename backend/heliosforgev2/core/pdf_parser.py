# backend/heliosforgev2/core/pdf_parser.py

import fitz  
import os
from typing import List, Dict
from heliosforgev2.utils.file_ops import ensure_dir_exists, save_text_to_file
from heliosforgev2.utils.text_cleaner import clean_text


def extract_text_runs_from_pdf(pdf_path: str) -> List[Dict]:
    """
    PDF dosyasını analiz eder ve her sayfa için text run'larını çıkarır.

    Args:
        pdf_path: Girdi PDF dosyasının tam yolu

    Returns:
        [
            {
                "page_number": 1,
                "txtRns": [ {run}, {run}, ... ]
            },
            ...
        ]
    """
    results = []
    doc = fitz.open(pdf_path)

    for page_index in range(len(doc)):
        page = doc[page_index]
        words = page.get_text("dict")["blocks"]

        text_runs = []

        for block in words:
            if block["type"] != 0:  # sadece text block
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    cleaned_text = clean_text(span["text"])
                    if not cleaned_text:
                        continue

                    text_runs.append({
                        "leftX": span["bbox"][0],
                        "bottomY": span["bbox"][3],
                        "rightX": span["bbox"][2],
                        "topY": span["bbox"][1],
                        "baseLineY": line.get("baseline", span["bbox"][3] - 2),
                        "fontId": span.get("font", 0),
                        "text": cleaned_text
                    })

        results.append({
            "page_number": page_index + 1,
            "txtRns": text_runs
        })

    doc.close()
    return results


def parse_pdf_to_json(pdf_path: str, output_dir: str, doc_id: str) -> str:
    """
    PDF'i parse eder ve çıktı JSON’unu verilen klasöre kaydeder.

    Args:
        pdf_path: PDF dosyasının tam yolu
        output_dir: Çıktının yazılacağı klasör
        doc_id: Dosya adlandırması için benzersiz kimlik (örn: DOC001)

    Returns:
        Yazılan JSON dosyasının path’i
    """
    ensure_dir_exists(output_dir)

    all_pages_data = extract_text_runs_from_pdf(pdf_path)

    json_file_path = os.path.join(output_dir, f"{doc_id}_parsed.json")

    import json
    save_text_to_file(json.dumps(all_pages_data, indent=2), json_file_path)

    return json_file_path
