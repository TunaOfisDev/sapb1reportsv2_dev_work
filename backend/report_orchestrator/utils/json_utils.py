# backend/report_orchestrator/utils/json_utils.py

import json
import os
from datetime import datetime
from django.conf import settings


def save_json_to_disk(data: dict, filename: str, folder: str = "logs/debug_json") -> str:
    """
    Verilen JSON datasını belirtilen klasöre `.json` dosyası olarak kaydeder.
    - filename: uzantısız dosya adı (örn: "balance_top10_20250417")
    - folder: klasör yolu (varsayılan: logs/debug_json/)
    """
    base_path = os.path.join(settings.BASE_DIR, folder)
    os.makedirs(base_path, exist_ok=True)

    full_path = os.path.join(base_path, f"{filename}.json")

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return full_path


def load_json_from_file(path: str) -> dict:
    """
    Diskteki bir JSON dosyasını açar ve içeriklerini döndürür.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_json_preview(data: dict, max_chars: int = 300) -> str:
    """
    JSON içeriğini sade bir şekilde loglamak için kısa özet string üretir.
    """
    try:
        raw = json.dumps(data, ensure_ascii=False, indent=2)
        return raw[:max_chars] + ("..." if len(raw) > max_chars else "")
    except Exception as e:
        return f"[format_json_preview hata]: {str(e)}"


def generate_timestamped_filename(base_name: str) -> str:
    """
    'bakiye_ozeti_20250417_0900' gibi zaman damgalı bir dosya adı üretir.
    """
    now = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{base_name}_{now}"
