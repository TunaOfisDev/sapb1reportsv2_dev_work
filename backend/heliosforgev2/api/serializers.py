
from rest_framework import serializers
from heliosforgev2.models.document import Document
from heliosforgev2.models.chunk import Chunk
from heliosforgev2.models.image import Image


class ChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chunk
        fields = [
            "id",
            "chunk_id",
            "document",
            "page_number",
            "section_title",
            "content",
            "left_x", "bottom_y", "right_x", "top_y",
            "created_at",
        ]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            "id",
            "document",
            "chunk",
            "file_name",
            "file_path",
            "page_number",
            "left_x", "bottom_y", "right_x", "top_y",
            "created_at",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "file",           # FileField
            "page_count",
            "uploaded_at",
            "parsed_at",
            "status",
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    chunks = ChunkSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "file",
            "page_count",
            "uploaded_at",
            "parsed_at",
            "status",
            "chunks",
            "images",
        ]
