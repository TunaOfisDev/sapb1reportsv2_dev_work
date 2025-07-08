# backend/heliosforgev2/admin.py

from django.contrib import admin
from import_export.admin import ExportMixin
from heliosforgev2.models.document import Document
from heliosforgev2.models.chunk import Chunk
from heliosforgev2.models.image import Image


@admin.register(Document)
class DocumentAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "get_file_name", "page_count", "status", "uploaded_at", "parsed_at")
    search_fields = ("file__icontains",)
    list_filter = ("status", "uploaded_at")
    ordering = ("-uploaded_at",)

    def get_file_name(self, obj):
        return obj.file.name.split("/")[-1] if obj.file else "-"
    get_file_name.short_description = "Dosya Adı"


@admin.register(Chunk)
class ChunkAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("chunk_id", "document", "page_number", "section_title")
    search_fields = ("chunk_id", "section_title", "content")
    list_filter = ("page_number",)
    ordering = ("document", "page_number", "chunk_id")


@admin.register(Image)
class ImageAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("file_name", "document", "page_number", "chunk")
    search_fields = ("file_name",)
    list_filter = ("page_number", "document")
    ordering = ("document", "page_number", "file_name")
