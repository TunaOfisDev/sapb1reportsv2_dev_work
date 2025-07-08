# backend/heliosforgev2/core/image_extractor.py

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Optional

import fitz  # PyMuPDF

from heliosforgev2.utils.file_ops import ensure_dir_exists
from heliosforgev2.models import Document, Image


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


def extract_images_from_pdf(
    pdf_path: str,
    output_dir: str,
    doc_id: str,
    document: Optional[Document] = None,
    save_to_db: bool = False
) -> List[Dict]:
    ensure_dir_exists(output_dir)
    images: List[Dict] = []

    pdf = fitz.open(pdf_path)
    for page in pdf:
        page_number = page.number + 1
        page_height = page.rect.height  # 🔴 Kritik satır
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

            try:
                pix = fitz.Pixmap(pdf, xref)
            except Exception as e:
                print(f"[!] Pixmap oluşturulamadı (xref={xref}): {e}")
                continue

            if pix.alpha or pix.colorspace.n >= 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                ext = ".png"
            else:
                ext = ".jpeg"

            for rect in rects:
                # 🔁 Koordinat düzeltmesi
                x0 = rect.x0
                x1 = rect.x1
                y0 = page_height - rect.y1
                y1 = page_height - rect.y0

                file_name = f"{doc_id}-PAGE{page_number:03d}-IMG{img_counter:03d}{ext}"
                out_path = Path(output_dir) / file_name

                try:
                    _save_pixmap(pix, out_path)
                except Exception as e:
                    print(f"[!] Görsel yazılamadı {file_name}: {e}")
                    continue

                bbox = {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
                image_dict = {
                    "file_name": file_name,
                    "file_path": str(out_path.resolve()),
                    "page_number": page_number,
                    "bbox": bbox,
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

            pix = None

    pdf.close()
    return images

    return images
