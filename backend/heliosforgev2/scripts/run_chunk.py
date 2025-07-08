# backend/heliosforgev2/scripts/run_chunk.py

import os
import sys
import json

# PYTHONPATH ayarı
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sapreports.settings")

import django
django.setup()

from django.conf import settings
from heliosforgev2.models import Document
from heliosforgev2.core.pdf_parser import parse_pdf_to_json
from heliosforgev2.core.chunker import extract_chunks_from_runs
from heliosforgev2.core.image_extractor import extract_images_from_pdf
from heliosforgev2.services.chunk_service import create_chunks_from_json
from heliosforgev2.services.document_service import update_document_status


def run(document_id: int):
    doc = Document.objects.get(id=document_id)
    doc_id = f"DOC{doc.id:03d}"

    print(f"[✓] Başladı: {doc_id} ({doc.file.name})")

    # 1. PDF → JSON
    json_path = parse_pdf_to_json(
        pdf_path=doc.file.path,
        output_dir=settings.HELIOS_STORAGE["JSON"],
        doc_id=doc_id
    )

    with open(json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    # 2. Chunk üretimi
    total_chunks = 0
    for page in pages:
        chunks = extract_chunks_from_runs(
            runs=page["txtRns"],
            page_number=page["page_number"],
            doc_id=doc_id
        )
        create_chunks_from_json(doc, page["page_number"], chunks)
        total_chunks += len(chunks)

    print(f"[✓] Chunk üretimi tamamlandı: {total_chunks} adet")

    # 3. Görsel çıkarımı ve Image modeline kaydet
    image_infos = extract_images_from_pdf(
        pdf_path=doc.file.path,
        output_dir=settings.HELIOS_STORAGE["IMAGES"],
        doc_id=doc_id,
        document=doc,              # resim kaydı için gerekli
        save_to_db=True            # doğrudan DB’ye kaydetsin
    )

    print(f"[✓] Görsel kaydı tamamlandı: {len(image_infos)} adet")

    # 4. Belge durumu güncelle
    update_document_status(doc, "parsed")
    print(f"[✓] Tamamlandı: {doc_id}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python run_chunk.py <document_id>")
        sys.exit(1)

    run(int(sys.argv[1]))
