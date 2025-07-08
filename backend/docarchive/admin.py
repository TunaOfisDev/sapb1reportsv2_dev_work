# backend/docarchive/admin.py
from django.contrib import admin
from .models.models import Document, Department, DocumentFile

class DocumentFileInline(admin.TabularInline):
    model = DocumentFile
    extra = 1  # Varsayılan olarak bir dosya yükleme alanı ekler

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_at', 'owner_name', 'comments', 'department')
    list_filter = ('created_at', 'owner_name', 'department')
    search_fields = ('name', 'owner_name', 'comments', 'department__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    inlines = [DocumentFileInline]  # Document ile ilişkili dosyaları yönetmek için inline ekleniyor

    fieldsets = (
        (None, {
            'fields': ('name', 'owner_name', 'comments', 'department')
        }),
        ('Date Information', {'fields': ('created_at',)}),
    )
    ordering = ('-created_at',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Document, DocumentAdmin)
admin.site.register(Department, DepartmentAdmin)

