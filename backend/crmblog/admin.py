# backend/crmblog/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models.models import Post
from authcentral.models import CustomUser

class PostResource(resources.ModelResource):
    author_id = fields.Field(attribute='author_id', column_name='author_id')
    
    class Meta:
        model = Post
        fields = ('id', 'task_title', 'project_name', 'deadline', 'task_description', 'status', 'author_id', 'author__email', 'created_at', 'updated_at')

    def before_import_row(self, row, **kwargs):
        email = row.get('author__email')
        try:
            author = CustomUser.objects.get(email=email)
            row['author_id'] = author.id
        except CustomUser.DoesNotExist:
            row['author_id'] = None  # Yazar bulunamazsa None değerini atayabiliriz
        return super().before_import_row(row, **kwargs)

class PostAdmin(ImportExportModelAdmin):
    resource_class = PostResource
    list_display = ('id','task_title', 'project_name', 'deadline', 'status', 'author', 'created_at', 'updated_at')
    list_filter = ('status', 'author', 'created_at')
    search_fields = ('task_title', 'project_name', 'task_description', 'author__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('task_title', 'project_name', 'deadline', 'task_description', 'status', 'author')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.register(Post, PostAdmin)

