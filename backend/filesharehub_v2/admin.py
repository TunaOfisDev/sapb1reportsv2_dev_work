# backend/filesharehub_v2/admin.py
from django.contrib import admin
from filesharehub_v2.models.filerecord import FileRecord

@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "is_dir", "size", "modified", "is_image")
    list_filter = ("is_dir", "is_image")
    search_fields = ("name", "path")
    ordering = ("path", "name")
