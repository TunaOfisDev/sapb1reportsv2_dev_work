# backend/heliosforgev2/core/schemas.py

from typing import Optional, List
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    leftX: float = Field(..., description="Sol koordinat (X)")
    bottomY: float = Field(..., description="Alt koordinat (Y)")
    rightX: float = Field(..., description="Sağ koordinat (X)")
    topY: float = Field(..., description="Üst koordinat (Y)")


class ChunkSchema(BaseModel):
    chunk_id: str
    page_number: int
    section_title: Optional[str] = None
    content: str
    bounding_box: BoundingBox
    related_image: Optional[str] = None  # Dosya adı (örn: DOC001-PAGE003-IMG001.png)


class ImageSchema(BaseModel):
    file_name: str
    file_path: str
    page_number: int
    coordinates: Optional[BoundingBox] = None
    related_chunk_id: Optional[str] = None


class DocumentSchema(BaseModel):
    file_name: str
    file_path: str
    page_count: int
    parsed_at: Optional[str] = None
    status: str = "pending"
    chunks: Optional[List[ChunkSchema]] = None
    images: Optional[List[ImageSchema]] = None
