# backend/systemnotebook/admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from systemnotebook.models.system_note_model import SystemNote
from import_export import resources


class SystemNoteResource(resources.ModelResource):
    class Meta:
        model = SystemNote
        fields = (
            'id',
            'title',
            'content',
            'source',
            'created_by__email',  # <-- username yerine email
            'created_at',
        )
        export_order = (
            'id',
            'title',
            'source',
            'created_by__email',  # <-- burada da aynı şekilde
            'created_at',
            'content',
        )


@admin.register(SystemNote)
class SystemNoteAdmin(ImportExportModelAdmin):
    list_display = ('title', 'source', 'created_by', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('title', 'content', 'created_by__email')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    resource_class = SystemNoteResource
