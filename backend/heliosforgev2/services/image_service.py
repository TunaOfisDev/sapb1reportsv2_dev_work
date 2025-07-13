# backend/heliosforgev2/services/image_service.py
import os
from typing import List, Dict, Optional, Union
from math import hypot
from heliosforgev2.models.document import Document
from heliosforgev2.models.image import Image
from heliosforgev2.models.chunk import Chunk
from heliosforgev2.utils.file_ops import ensure_dir_exists


# ───────────────────────────── Yardımcı Fonksiyonlar ─────────────────────────────

Number = Union[int, float, str]


def safe_float(val: Number, default: float = 0.0) -> float:
    """
    Virgül veya dize içerebilecek sayıyı güvenle float’a çevirir.
    """
    try:
        if isinstance(val, (int, float)):
            return float(val)
        return float(str(val).replace(",", "."))
    except Exception:
        return default


def normalize_bbox(bbox: Dict[str, Number]) -> Dict[str, float]:
    """
    Bounding-box koordinatlarını standardize eder:

    * x0 < x1  |  y0 < y1 (alt-sol köken)
    * Hem `y0/y1` anahtarlarını hem de `bottomY/topY` varyasyonlarını tolere eder.
    """
    # Anahtarları esnek yakala
    x0_raw = bbox.get("x0") or bbox.get("leftX")
    x1_raw = bbox.get("x1") or bbox.get("rightX")

    # Öncelikle y0/y1 varsa kullan, yoksa bottomY/topY
    y0_raw = bbox.get("y0") or bbox.get("bottomY")
    y1_raw = bbox.get("y1") or bbox.get("topY")

    # Güvenli dönüştürme
    x0, x1 = sorted([safe_float(x0_raw), safe_float(x1_raw)])
    y0, y1 = sorted([safe_float(y0_raw), safe_float(y1_raw)])

    return {
        "x0": x0,
        "x1": x1,
        "bottomY": y0,
        "topY": y1,
    }


def is_overlap(img: dict, chk: dict) -> float:
    """İki kutunun örtüşen ALAN oranını verir (0‒1). Küçük alanı payda yapar."""
    x_ov = max(0, min(img["x1"], chk["x1"]) - max(img["x0"], chk["x0"]))
    y_ov = max(0, min(img["topY"], chk["topY"]) - max(img["bottomY"], chk["bottomY"]))
    overlap = x_ov * y_ov
    if overlap == 0:
        return 0.0
    smaller = min(
        (img["x1"] - img["x0"]) * (img["topY"] - img["bottomY"]),
        (chk["x1"] - chk["x0"]) * (chk["topY"] - chk["bottomY"]),
    )
    return overlap / smaller



# ─────────────────────── Chunk Eşlemesi ve Kayıt Mantığı ────────────────────────

# -------------------- normalize_bbox() aynı kalsın ---------------------------

def overlap_ratio(img: dict, chk: dict) -> float:
    """
    img & chk: {'x0','x1','bottomY','topY'}
    Dönüş: küçük kutuya göre kaplama oranı (0–1).
    """
    x_ov = max(0, min(img["x1"], chk["x1"]) - max(img["x0"], chk["x0"]))
    y_ov = max(0, min(img["topY"], chk["topY"]) - max(img["bottomY"], chk["bottomY"]))
    overlap = x_ov * y_ov
    if overlap == 0:
        return 0.0
    img_area = (img["x1"] - img["x0"]) * (img["topY"] - img["bottomY"])
    chk_area = (chk["x1"] - chk["x0"]) * (chk["topY"] - chk["bottomY"])
    return overlap / min(img_area, chk_area)




def center(box):
    return ((box["x0"] + box["x1"]) / 2, (box["bottomY"] + box["topY"]) / 2)

def center_distance(a, b):
    ax, ay = center(a)
    bx, by = center(b)
    return hypot(ax - bx, ay - by)


def find_best_chunk(document, image_info, *, threshold=0.70):
    img_box = normalize_bbox(image_info["bbox"])
    page_chunks = Chunk.objects.filter(
        document=document, page_number=image_info["page_number"]
    ).exclude(left_x=None)

    # --- Kademe 1: overlap ---
    best, best_score = None, 0.0
    for ch in page_chunks:
        score = overlap_ratio(img_box, ch.box_dict)
        if score > best_score:
            best, best_score = ch, score
    if best_score >= threshold:
        return best

    # --- Kademe 2: dikey / merkez mesafesi ---
    nearest = min(
        page_chunks,
        key=lambda ch: center_distance(img_box, ch.box_dict),
        default=None,
    )
    if nearest:
        return nearest

    # --- Kademe 3: pseudo-chunk ---
    caption_chunk, _ = Chunk.objects.get_or_create(
        document=document,
        page_number=image_info["page_number"],
        chunk_id=f"{document.code}-PAGE{image_info['page_number']:03d}-CHUNK_CAPTION",
        defaults={
            "content": "",
            "left_x": 0,
            "bottom_y": 0,
            "right_x": image_info["page_width"],
            "top_y": image_info["page_height"],
        },
    )
    return caption_chunk




def save_image_metadata(
    document: Document,
    page_number: int,
    file_path: str,
    chunk: Optional[Chunk],
    bbox: Dict[str, Number],
) -> Image:
    """
    Tek bir Image kaydı oluşturur (normalize edilmiş bbox ile).
    """
    ensure_dir_exists(os.path.dirname(file_path))
    nb = normalize_bbox(bbox)

    return Image.objects.create(
        document=document,
        chunk=chunk,
        file_name=os.path.basename(file_path),
        file_path=file_path,
        page_number=page_number,
        left_x=nb["x0"],
        bottom_y=nb["bottomY"],
        right_x=nb["x1"],
        top_y=nb["topY"],
    )


# ───────────────────────────── Toplu Görsel Kaydı ──────────────────────────────
def bulk_register_images(document, image_infos, match_threshold=0.70):
    for img in image_infos:
        bbox = img.get("bbox")
        if not bbox:
            continue
        chunk = find_best_chunk(document, img, threshold=match_threshold)
        save_image_metadata(document, img["page_number"], img["file_path"], chunk, bbox)

