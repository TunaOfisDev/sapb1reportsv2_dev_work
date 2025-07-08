# backend/heliosforgev2/api/views.py
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from heliosforgev2.models.document import Document
from heliosforgev2.models.chunk import Chunk
from heliosforgev2.models.image import Image

from heliosforgev2.api.serializers import (
    DocumentSerializer,
    DocumentDetailSerializer,
    ChunkSerializer,
    ImageSerializer
)

from heliosforgev2.services.document_service import create_document_record, update_document_status
from heliosforgev2.services.chunk_service import create_chunks_from_json
from heliosforgev2.services.image_service import bulk_register_images
from heliosforgev2.core.pdf_parser import parse_pdf_to_json
from heliosforgev2.core.chunker import extract_chunks_from_runs
from heliosforgev2.core.image_extractor import extract_images_from_pdf

import json


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all().order_by("-uploaded_at")

    def get_serializer_class(self):
        return DocumentDetailSerializer if self.action == "retrieve" else DocumentSerializer


class ChunkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chunk.objects.all()
    serializer_class = ChunkSerializer


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer




class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file uploaded."}, status=400)

        document = create_document_record(uploaded_file)
        local_pdf_path = document.file.path
        doc_id = f"DOC{document.id:03d}"

        try:
            # 1. PDF → JSON
            json_path = parse_pdf_to_json(
                pdf_path=local_pdf_path,
                output_dir=settings.HELIOS_STORAGE["JSON"],
                doc_id=doc_id
            )

            with open(json_path, "r", encoding="utf-8") as jf:
                pages_data = json.load(jf)

            # 2. Chunk üretimi
            for page in pages_data:
                chunks = extract_chunks_from_runs(
                    runs=page["txtRns"],
                    page_number=page["page_number"],
                    doc_id=doc_id
                )
                create_chunks_from_json(document, page["page_number"], chunks)

            # 3. Görsel çıkarımı ve kesin chunk eşlemesi
            image_infos = extract_images_from_pdf(
                pdf_path=local_pdf_path,
                output_dir=settings.HELIOS_STORAGE["IMAGES"],
                doc_id=doc_id
            )
            bulk_register_images(document, image_infos)

            # 4. Başarıyla tamamlandı
            update_document_status(document, "parsed")

        except Exception as e:
            update_document_status(document, "error")
            return Response({"error": str(e)}, status=500)

        return Response(DocumentDetailSerializer(document).data, status=201)
