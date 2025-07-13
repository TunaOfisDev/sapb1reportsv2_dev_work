# backend/heliosforgev2/core/image_extractor.py
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Optional

import fitz  # PyMuPDF

from django.conf import settings
from heliosforgev2.utils.file_ops import ensure_dir_exists
from heliosforgev2.models import Document, Image

# ─────────────────────────── Filtre Varsayılanları ────────────────────────────
DEFAULT_FILTER: Dict[str, int] = {
    "min_width": 100,      # px
    "min_height": 100,     # px
    "min_area": 10_000,    # px²   (≈100×100)
}

# settings.py içinden ezme şansı
DEFAULT_FILTER.update(getattr(settings, "HELIOS_IMAGE_FILTER", {}))


# ───────────────────────────── Yardımcı Fonksiyon ─────────────────────────────
def _save_pixmap(pix: fitz.Pixmap, out_path: Path) -> None:
    """
    PyMuPDF 1.23+ : Pixmap.save(path)
    1.18 – 1.22   : Pixmap.writePNG / writeImage
    """
    try:
        pix.save(out_path)
    except TypeError:
        if out_path.suffix.lower() == ".png":
            pix.writePNG(out_path)
        else:
            pix.writeImage(out_path)


# ───────────────────────────── Ana Fonksiyon ──────────────────────────────────
def extract_images_from_pdf(
    pdf_path: str,
    output_dir: str,
    doc_id: str,
    *,
    document: Optional[Document] = None,
    save_to_db: bool = False,
    filter_rules: Optional[Dict[str, int]] = None,
) -> List[Dict]:
    """
    PDF’ten görselleri çıkarır.

    • `filter_rules` ile min_width / min_height / min_area eşikleri geçilebilir.
    • Küçük ikon/simgeler eşik altındaysa **kaydedilmez**.
    • `save_to_db=True` ise Image modeli anında oluşturulur.
    """
    ensure_dir_exists(output_dir)
    images: List[Dict] = []

    filt = {**DEFAULT_FILTER, **(filter_rules or {})}

    pdf = fitz.open(pdf_path)
    for page in pdf:
        page_number = page.number + 1
        page_height = page.rect.height
        img_counter = 1

        for img in page.get_images(full=True):
            xref = img[0]
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                name = img[7] if len(img) >= 8 else None
                rects = [page.get_image_bbox(name)] if name else []

            if not rects:
                continue

            # ───────── Pixmap oluştur ─────────
            try:
                pix = fitz.Pixmap(pdf, xref)
            except Exception as e:  # noqa: BLE001
                print(f"[!] Pixmap oluşturulamadı (xref={xref}): {e}")
                continue

            # Boyut filtresi
            img_w, img_h = pix.width, pix.height
            if (
                img_w < filt["min_width"]
                or img_h < filt["min_height"]
                or (img_w * img_h) < filt["min_area"]
            ):
                pix = None
                continue

            # Renk → RGB / uzantı
            if pix.alpha or pix.colorspace.n >= 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                ext = ".png"
            else:
                ext = ".jpeg"

            # ───────── Her rect için kayıt ─────────
            for rect in rects:
                x0, x1 = rect.x0, rect.x1
                y0, y1 = page_height - rect.y1, page_height - rect.y0  # alt-sol

                file_name = f"{doc_id}-PAGE{page_number:03d}-IMG{img_counter:03d}{ext}"
                out_path = Path(output_dir) / file_name

                try:
                    _save_pixmap(pix, out_path)
                except Exception as e:  # noqa: BLE001
                    print(f"[!] Görsel yazılamadı {file_name}: {e}")
                    continue

                bbox = {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
                image_dict = {
                    "file_name": file_name,
                    "file_path": str(out_path.resolve()),
                    "page_number": page_number,
                    "bbox": bbox,
                    "page_width": page.rect.width,
                    "page_height": page_height,
                }

                images.append(image_dict)

                if save_to_db and document:
                    Image.objects.create(
                        document=document,
                        chunk=None,
                        file_name=file_name,
                        file_path=str(out_path.resolve()),
                        page_number=page_number,
                        left_x=bbox["x0"],
                        bottom_y=bbox["y0"],
                        right_x=bbox["x1"],
                        top_y=bbox["y1"],
                    )

                img_counter += 1

            pix = None  # bellek temizliği

    pdf.close()
    return images
