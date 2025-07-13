# backend/heliosforgev2/core/chunker.py
from typing import List, Dict, Any
from collections import defaultdict
from heliosforgev2.utils.text_cleaner import clean_text, is_meaningful
import re


# ---------------------------------------------------------------------------
# Satır gruplayıcı (değişmedi)
# ---------------------------------------------------------------------------
def group_runs_by_line(runs: List[Dict[str, Any]], y_tolerance: float = 1.5) -> List[List[Dict]]:  # noqa: D401
    """Aynı yatay satırda yer alan text-run’ları grupla (baseLineY’ye göre)."""
    lines = defaultdict(list)

    for run in runs:
        base_y = run.get("baseLineY")
        key = round(base_y / y_tolerance) * y_tolerance
        lines[key].append(run)

    # soldan sağa, yukarıdan aşağıya
    return [sorted(line, key=lambda r: r["leftX"])
            for line in sorted(lines.values(), key=lambda l: l[0]["baseLineY"])]


# ---------------------------------------------------------------------------
# Başlık (section title) sezgisi (değişmedi)
# ---------------------------------------------------------------------------
def detect_section_title(line: list, font_threshold: int = 18) -> bool:
    """Başlık olabilecek satırı tespit et (font boyutu veya 1.2.3 ... örüntüsü)."""
    for r in line:
        text = r.get("text", "").strip()
        font_id = r.get("fontId", "")
        if not text:
            continue

        heading_like = bool(re.match(r"^\d+(\.\d+)*\s+[A-Z]", text))

        try:
            font_val = int(font_id) if isinstance(font_id, str) and font_id.isdigit() else float(font_id)
        except Exception:
            font_val = 0

        if heading_like or font_val >= font_threshold:
            return True
    return False


# ---------------------------------------------------------------------------
# Ana chunker - Y ekseni düzeltildi
# ---------------------------------------------------------------------------
def extract_chunks_from_runs(                 # noqa: D401
    runs: List[Dict[str, Any]],
    page_number: int,
    doc_id: str,
    page_height: float,
) -> List[Dict[str, Any]]:
    """
    Tek bir sayfanın 'runs' verisini anlamlı chunk’lara böler
    ve bounding-box’ları alt-sol kökenine çevirir.
    """
    chunks: List[Dict[str, Any]] = []
    section_title: str | None = None
    lines = group_runs_by_line(runs)

    chunk_index = 1
    buffer: list[str] = []

    # PyMuPDF üst-sol kökene göre ham bbox tut
    bbox_raw = {
        "x0": None,   # sol
        "x1": None,   # sağ
        "y_min": None,  # en yukarı (küçük değer)
        "y_max": None,  # en aşağı (büyük değer)
    }

    # ------------- iç yardımcı ------------------------------------------------
    def flush_chunk() -> None:
        nonlocal buffer, chunk_index, section_title, bbox_raw

        if not buffer:
            return

        content = clean_text(" ".join(buffer))
        if not is_meaningful(content):
            buffer.clear()
            return

        # Ham bbox → alt-sol normalize
        if bbox_raw["y_min"] is not None:
            bottomY = page_height - bbox_raw["y_max"]
            topY    = page_height - bbox_raw["y_min"]
        else:
            bottomY = topY = None

        bbox_norm = {
            "leftX":  bbox_raw["x0"],
            "rightX": bbox_raw["x1"],
            "bottomY": bottomY,
            "topY":    topY,
        }

        chunk_id = f"{doc_id}-PAGE{page_number:03d}-CHUNK{chunk_index:03d}"
        chunks.append({
            "chunk_id":      chunk_id,
            "page_number":   page_number,
            "section_title": section_title,
            "content":       content,
            "bounding_box":  bbox_norm,
        })
        chunk_index += 1

        # reset
        buffer.clear()
        bbox_raw = {"x0": None, "x1": None, "y_min": None, "y_max": None}

    # ------------- ana döngü --------------------------------------------------
    for line in lines:
        line_text = clean_text(" ".join(r["text"] for r in line))

        if detect_section_title(line):
            flush_chunk()
            section_title = line_text
            continue

        if is_meaningful(line_text):
            buffer.append(line_text)

            xs = [r["leftX"] for r in line] + [r["rightX"] for r in line]
            ys = [r["topY"]  for r in line] + [r["bottomY"] for r in line]

            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)

            # ham bbox güncelle
            bbox_raw["x0"]   = x_min if bbox_raw["x0"]   is None else min(bbox_raw["x0"], x_min)
            bbox_raw["x1"]   = x_max if bbox_raw["x1"]   is None else max(bbox_raw["x1"], x_max)
            bbox_raw["y_min"] = y_min if bbox_raw["y_min"] is None else min(bbox_raw["y_min"], y_min)
            bbox_raw["y_max"] = y_max if bbox_raw["y_max"] is None else max(bbox_raw["y_max"], y_max)

    flush_chunk()
    return chunks
