# backend/mailservice/admin.py
from django.contrib import admin
from .models.models import MailLog  # Import yolunu düzelttik

@admin.register(MailLog)
class MailLogAdmin(admin.ModelAdmin):
    list_display = ('mail_type', 'subject', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'mail_type')  # created_at'i kaldırdık çünkü henüz oluşturulmadı
    search_fields = ('subject',)  # JSONField olan recipients'i kaldırdık
    readonly_fields = ('created_at', 'sent_at')  # Bu alanları readonly yapıyoruz