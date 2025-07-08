# backend/eduvideo/admin.py
from django.contrib import admin
from .models.models import EduVideo

class EduVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'thumbnail_url' ,'published_at', 'created_at', 'updated_at')  # Listede gösterilecek alanlar
    search_fields = ('title', 'description')  # Arama yapılacak alanlar
    list_filter = ('published_at', 'created_at')  # Filtreleme yapılacak alanlar
    readonly_fields = ('created_at', 'updated_at')  # Sadece okunabilir alanlar

    def save_model(self, request, obj, form, change):
        # Özel kaydetme davranışı test
        super().save_model(request, obj, form, change)

admin.site.register(EduVideo, EduVideoAdmin)
