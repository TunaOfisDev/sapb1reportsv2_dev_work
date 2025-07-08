# backend/heliosforgev2/services/image_service.py

import os
from typing import List, Dict, Optional

from heliosforgev2.models.document import Document
from heliosforgev2.models.image import Image
from heliosforgev2.models.chunk import Chunk
from heliosforgev2.utils.file_ops import ensure_dir_exists


# ───────────────────────────── Yardımcı Fonksiyonlar ─────────────────────────────

def safe_float(val: str | float) -> float:
    if isinstance(val, float) or isinstance(val, int):
        return float(val)
    return float(str(val).replace(",", "."))


def normalize_bbox(bbox: Dict[str, float]) -> Dict[str, float]:
    """
    Bounding box koordinatlarını normalize eder (x0 < x1, y0 < y1).
    PyMuPDF ve JSON karışıklıkları için güvenli hale getirir.
    """
    x0 = safe_float(bbox.get("x0", 0))
    y0 = safe_float(bbox.get("y0", 0))
    x1 = safe_float(bbox.get("x1", 0))
    y1 = safe_float(bbox.get("y1", 0))

    return {
        "x0": min(x0, x1),
        "x1": max(x0, x1),
        "bottomY": min(y0, y1),
        "topY": max(y0, y1),
    }


def is_overlap(image_box: Dict[str, float], chunk_box: Dict[str, float], threshold: float = 0.85) -> bool:
    """
    Görsel alanının ne kadarının chunk tarafından kapsandığını ölçer (%85 ve üzeri eşleşme kabul edilir).
    """
    x_overlap = max(0, min(image_box["x1"], chunk_box["x1"]) - max(image_box["x0"], chunk_box["x0"]))
    y_overlap = max(0, min(image_box["topY"], chunk_box["topY"]) - max(image_box["bottomY"], chunk_box["bottomY"]))
    overlap_area = x_overlap * y_overlap

    image_area = (image_box["x1"] - image_box["x0"]) * (image_box["topY"] - image_box["bottomY"])
    if image_area == 0:
        return False

    return (overlap_area / image_area) >= threshold


# ───────────────────────────── Chunk Eşlemesi ve Kayıt ─────────────────────────────

def find_best_chunk(document: Document, image_info: Dict) -> Optional[Chunk]:
    """
    Görselin bulunduğu sayfada en iyi eşleşen chunk’ı bulur.
    %85 ve üzeri overlap aranır. Bulunamazsa None döner.
    """
    if not image_info.get("bbox"):
        return None

    bbox = normalize_bbox(image_info["bbox"])

    image_box = {
        "x0": bbox["x0"],
        "x1": bbox["x1"],
        "bottomY": bbox["bottomY"],
        "topY": bbox["topY"],
    }

    chunks = Chunk.objects.filter(
        document=document,
        page_number=image_info["page_number"]
    ).exclude(
        left_x=None, right_x=None, bottom_y=None, top_y=None
    )

    for chunk in chunks:
        chunk_box = {
            "x0": chunk.left_x,
            "x1": chunk.right_x,
            "bottomY": chunk.bottom_y,
            "topY": chunk.top_y,
        }

        if is_overlap(image_box, chunk_box, threshold=0.85):
            return chunk

    return None


def save_image_metadata(
    document: Document,
    page_number: int,
    file_path: str,
    chunk: Optional[Chunk],
    bbox: Dict[str, float],
) -> Image:
    """Tek bir Image kaydı oluşturur."""
    ensure_dir_exists(os.path.dirname(file_path))
    bbox = normalize_bbox(bbox)

    return Image.objects.create(
        document=document,
        chunk=chunk,
        file_name=os.path.basename(file_path),
        file_path=file_path,
        page_number=page_number,
        left_x=bbox["x0"],
        bottom_y=bbox["bottomY"],
        right_x=bbox["x1"],
        top_y=bbox["topY"],
    )


def bulk_register_images(document: Document, image_infos: List[Dict]) -> None:
    """
    Her görselin koordinatları veritabanına kaydedilir.
    Chunk eşleşmesi sadece %85+ kapsama varsa yapılır.
    """
    for img in image_infos:
        bbox = img.get("bbox")
        if not bbox:
            continue

        chunk = find_best_chunk(document, img)

        save_image_metadata(
            document=document,
            page_number=img["page_number"],
            file_path=img["file_path"],
            chunk=chunk,
            bbox=bbox
        )
