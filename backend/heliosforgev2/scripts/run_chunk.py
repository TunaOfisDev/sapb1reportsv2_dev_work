#!/usr/bin/env python3
# backend/heliosforgev2/scripts/run_chunk.py
"""
Tek komutla:
    python backend/heliosforgev2/scripts/run_chunk.py <document_id>

⤷ 1)  PDF → JSON
⤷ 2)  JSON → Chunk (bbox alt-sol köken)
⤷ 3)  Görsel çıkarımı (henüz DB’ye yazmadan)
⤷ 4)  Görsel ↔ Chunk eşlemesi + Image kayıt
⤷ 5)  Document.status = "parsed"
"""

import os
import sys
import json

# ─────────────────────────── PYTHONPATH / Django ──────────────────────────────
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sapreports.settings")

import django  # noqa: E402
django.setup()

# ───────────────────────────────── 3rd-party ──────────────────────────────────
import fitz  # PyMuPDF

# ──────────────────────────────── App Imports ─────────────────────────────────
from django.conf import settings
from heliosforgev2.models import Document
from heliosforgev2.core.pdf_parser import parse_pdf_to_json
from heliosforgev2.core.chunker import extract_chunks_from_runs
from heliosforgev2.core.image_extractor import extract_images_from_pdf
from heliosforgev2.services.chunk_service import create_chunks_from_json
from heliosforgev2.services.document_service import update_document_status
from heliosforgev2.services.image_service import bulk_register_images
from heliosforgev2.utils.text_cleaner import remove_header_footer, clean_text, is_meaningful

# ────────────────────────────────── Main Flow ─────────────────────────────────
def run(document_id: int) -> None:
    doc: Document = Document.objects.get(id=document_id)
    doc_code = f"DOC{doc.id:03d}"
    print(f"[✓] Başladı: {doc_code} ({doc.file.name})")

    # 1. PDF → JSON -------------------------------------------------------------
    json_path = parse_pdf_to_json(
        pdf_path=doc.file.path,
        output_dir=settings.HELIOS_STORAGE["JSON"],
        doc_id=doc_code,
    )
    with open(json_path, "r", encoding="utf-8") as fh:
        pages = json.load(fh)

    # 2. Chunk üretimi ----------------------------------------------------------
    pdf_doc = fitz.open(doc.file.path)          # tek sefer aç
    total_chunks = 0
    for idx, page in enumerate(pages):
        page_height = pdf_doc[idx].rect.height   # pt cinsinden

        # [🧹] Run içindeki metinleri önceden temizle
        cleaned_runs = []
        for run in page["txtRns"]:
            original_text = run.get("text", "")
            cleaned_text = clean_text(remove_header_footer(original_text))
            if is_meaningful(cleaned_text):
                run["text"] = cleaned_text
                cleaned_runs.append(run)

        # [📦] Chunk üretimi
        chunks = extract_chunks_from_runs(
            runs=cleaned_runs,
            page_number=idx + 1,
            doc_id=doc_code,
            page_height=page_height,
        )
        create_chunks_from_json(doc, idx + 1, chunks)
        total_chunks += len(chunks)

    # 3. Görsel çıkarımı (DB’ye yazmadan) ---------------------------------------
    image_infos = extract_images_from_pdf(
        pdf_path=doc.file.path,
        output_dir=settings.HELIOS_STORAGE["IMAGES"],
        doc_id=doc_code,
        save_to_db=False,           # önce liste; DB kaydı sonraki adımda
    )

    # 4. Görsel ↔ Chunk eşlemesi + Image kayıt ----------------------------------
    bulk_register_images(
        document=doc,
        image_infos=image_infos,
        match_threshold=0.70,       # küçük kutuya göre %70+
    )
    print(f"[✓] Görsel kaydı (chunk eşleşmeli) tamamlandı: {len(image_infos)} adet")

    # 5. Belge durumu güncelle ---------------------------------------------------
    update_document_status(doc, "parsed")
    print(f"[✓] Tamamlandı: {doc_code}")

# ─────────────────────────────────── CLI ──────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python run_chunk.py <document_id>")
        sys.exit(1)

    try:
        run(int(sys.argv[1]))
    except Exception as exc:  # pragma: no cover
        print(f"[✗] Hata: {exc}")
        raise
