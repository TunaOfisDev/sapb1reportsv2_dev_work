# backend/docarchivev2/admin.py
from django.contrib import admin
from .models.models import Department, Document, DocumentFile

class DocumentFileInline(admin.TabularInline):
    model = DocumentFile
    extra = 1  # Specifies the number of extra forms the formset should display.
    fields = ['file']

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'department', 'created_at')
    list_filter = ('created_at', 'department')
    search_fields = ('name', 'owner_name', 'comments')
    inlines = [DocumentFileInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'owner_name', 'comments', 'department')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('created_at',),
        }),
    )
    readonly_fields = ('created_at',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentFile)  # This can be left simple as the detailed interactions are through Document


