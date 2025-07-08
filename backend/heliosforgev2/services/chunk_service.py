# backend/heliosforgev2/services/chunk_service.py

from typing import List, Dict
from heliosforgev2.models.chunk import Chunk
from heliosforgev2.models.document import Document

def create_chunks_from_json(document: Document, page_number: int, chunk_data: List[Dict]) -> List[Chunk]:
    Chunk.objects.filter(document=document, page_number=page_number).delete()
    saved_chunks = []

    for i, data in enumerate(chunk_data, start=1):
        chunk_id = f"{document.id:04d}-PAGE{page_number:03d}-CHUNK{i:03d}"
        bbox = data.get("bounding_box", {})

        chunk = Chunk(
            chunk_id=chunk_id,
            document=document,
            page_number=page_number,
            section_title=data.get("section_title"),
            content=data.get("content"),
            left_x=bbox.get("leftX", 0.0),
            bottom_y=bbox.get("bottomY", 0.0),
            right_x=bbox.get("rightX", 0.0),
            top_y=bbox.get("topY", 0.0),
        )
        saved_chunks.append(chunk)

    # topluca yaz
    Chunk.objects.bulk_create(saved_chunks)
    return saved_chunks

