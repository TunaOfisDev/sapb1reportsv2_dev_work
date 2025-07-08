# backend/heliosforgev2/core/chunker.py

from typing import List, Dict, Any
from collections import defaultdict
from heliosforgev2.utils.text_cleaner import clean_text, is_meaningful
import re


def group_runs_by_line(runs: List[Dict[str, Any]], y_tolerance: float = 1.5) -> List[List[Dict]]:
    """
    Aynı yatay satırda yer alan text run’ları grupla (baseLineY’ye göre)
    """
    lines = defaultdict(list)

    for run in runs:
        base_y = run.get("baseLineY")
        key = round(base_y / y_tolerance) * y_tolerance
        lines[key].append(run)

    return [sorted(line, key=lambda r: r["leftX"]) for line in sorted(lines.values(), key=lambda l: l[0]["baseLineY"])]


def detect_section_title(line: list, font_threshold: int = 18) -> bool:
    """
    Font boyutu VEYA başlık örüntüsü (örn: 10.7 Database Authentication) olan satırları tespit eder.
    """
    for r in line:
        text = r.get("text", "").strip()
        font_id = r.get("fontId", "")
        if not text:
            continue

        heading_like = bool(re.match(r"^\d+(\.\d+)*\s+[A-Z]", text))

        try:
            if isinstance(font_id, str) and font_id.isdigit():
                font_val = int(font_id)
            elif isinstance(font_id, (int, float)):
                font_val = font_id
            else:
                font_val = 0
        except:
            font_val = 0

        if heading_like or font_val >= font_threshold:
            return True

    return False


def extract_chunks_from_runs(runs: List[Dict], page_number: int, doc_id: str) -> List[Dict]:
    """
    Tek bir sayfanın 'runs' verisini anlamlı chunk’lara böler.
    """
    chunks = []
    section_title = None
    lines = group_runs_by_line(runs)

    chunk_index = 1
    buffer = []

    bbox = {
        "leftX": None,
        "bottomY": None,
        "rightX": None,
        "topY": None,
    }

    def flush_chunk():
        nonlocal buffer, chunk_index, bbox, section_title
        if not buffer:
            return

        content = clean_text(" ".join(buffer))
        if not is_meaningful(content):
            buffer = []
            return

        chunk_id = f"{doc_id}-PAGE{page_number:03d}-CHUNK{chunk_index:03d}"
        chunks.append({
            "chunk_id": chunk_id,
            "page_number": page_number,
            "section_title": section_title,
            "content": content,
            "bounding_box": bbox.copy()
        })
        chunk_index += 1
        buffer = []
        bbox = {
            "leftX": None,
            "bottomY": None,
            "rightX": None,
            "topY": None,
        }

    for line in lines:
        line_text = " ".join(r["text"] for r in line)
        line_text = clean_text(line_text)

        if detect_section_title(line):
            flush_chunk()
            section_title = line_text
            continue

        if is_meaningful(line_text):
            buffer.append(line_text)

            # Bounding box güncelle
            xs = [r["leftX"] for r in line] + [r["rightX"] for r in line]
            ys = [r["bottomY"] for r in line] + [r["topY"] for r in line]

            bbox["leftX"] = min(xs) if bbox["leftX"] is None else min(bbox["leftX"], min(xs))
            bbox["rightX"] = max(xs) if bbox["rightX"] is None else max(bbox["rightX"], max(xs))
            bbox["bottomY"] = min(ys) if bbox["bottomY"] is None else min(bbox["bottomY"], min(ys))
            bbox["topY"] = max(ys) if bbox["topY"] is None else max(bbox["topY"], max(ys))

    flush_chunk()
    return chunks
