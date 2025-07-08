# backend/productconfig_simulator/admin/simulation_error_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from ..models.simulation_error import SimulationError
from ..admin.filters import (
    ErrorTypeFilter,
    ErrorSeverityFilter,
    ResolutionStatusFilter,
    ModelRelatedFilter,
    QuestionRelatedFilter
)


class SimulationErrorAdmin(admin.ModelAdmin):
    """
    Simülasyon hatalarını yönetmek için admin arayüzü
    """
    list_display = (
        'id', 'error_type_display', 'severity_display', 'message_display',
        'product_model_display', 'question_display', 'resolution_status_display',
        'created_at'
    )
    list_filter = (
        'simulation',
        ErrorTypeFilter,
        ErrorSeverityFilter,
        ResolutionStatusFilter,
        ModelRelatedFilter,
        QuestionRelatedFilter,
    )
    search_fields = ('message', 'product_model__name', 'question__name', 'option__name')
    readonly_fields = (
        'simulation', 'error_type', 'severity', 'message',
        'product_model', 'question', 'option',
        'created_at', 'updated_at'
    )
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('simulation', 'error_type', 'severity', 'message')
        }),
        ('İlişkili Veriler', {
            'fields': ('product_model', 'question', 'option')
        }),
        ('Çözüm', {
            'fields': ('resolution_status', 'resolution_notes', 'resolved_by', 'resolved_at')
        }),
    )
    actions = ['mark_as_resolved', 'mark_as_unresolved']

    def error_type_display(self, obj):
        """Hata türünü renkli göster"""
        error_type_colors = {
            SimulationError.ErrorType.MISSING_OPTIONS: 'blue',
            SimulationError.ErrorType.DEPENDENT_RULE: 'orange',
            SimulationError.ErrorType.CONDITIONAL_OPTION: 'purple',
            SimulationError.ErrorType.PRICE_MULTIPLIER: 'teal',
            SimulationError.ErrorType.PROCESSING: 'red',
            SimulationError.ErrorType.OTHER: 'gray',
        }
        color = error_type_colors.get(obj.error_type, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_error_type_display()
        )
    error_type_display.short_description = 'Hata Türü'

    def severity_display(self, obj):
        """Önem derecesini renkli göster"""
        severity_colors = {
            SimulationError.Severity.INFO: 'blue',
            SimulationError.Severity.WARNING: 'orange',
            SimulationError.Severity.ERROR: 'red',
            SimulationError.Severity.CRITICAL: 'darkred',
        }
        color = severity_colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_display.short_description = 'Önem'

    def message_display(self, obj):
        """Hatanın başlangıcını göster"""
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_display.short_description = 'Mesaj'

    def product_model_display(self, obj):
        """Ürün modelini göster"""
        if obj.product_model:
            return obj.product_model.name
        return '-'
    product_model_display.short_description = 'Ürün Modeli'

    def question_display(self, obj):
        """Soruyu göster"""
        if obj.question:
            return obj.question.name
        return '-'
    question_display.short_description = 'Soru'

    def resolution_status_display(self, obj):
        """Çözüm durumunu göster"""
        if obj.resolution_status:
            return format_html(
                '<span style="color: white; background-color: green; padding: 3px 8px; border-radius: 3px;">Çözüldü</span>'
            )
        return format_html(
            '<span style="color: white; background-color: red; padding: 3px 8px; border-radius: 3px;">Çözülmedi</span>'
        )
    resolution_status_display.short_description = 'Durum'

    def mark_as_resolved(self, request, queryset):
        """Seçili hataları çözüldü olarak işaretle"""
        queryset.filter(resolution_status=False).update(
            resolution_status=True,
            resolved_by=request.user,
            resolved_at=timezone.now(),
            resolution_notes=f"Toplu işlem ile çözüldü olarak işaretlendi. (Kullanıcı: {request.user.username})"
        )
        self.message_user(request, f"{queryset.filter(resolution_status=True).count()} hata çözüldü olarak işaretlendi.")
    mark_as_resolved.short_description = "Seçili hataları çözüldü olarak işaretle"

    def mark_as_unresolved(self, request, queryset):
        """Seçili hataları çözülmedi olarak işaretle"""
        queryset.filter(resolution_status=True).update(
            resolution_status=False,
            resolved_by=None,
            resolved_at=None,
            resolution_notes=f"Toplu işlem ile çözülmedi olarak işaretlendi. (Kullanıcı: {request.user.username})"
        )
        self.message_user(request, f"{queryset.filter(resolution_status=False).count()} hata çözülmedi olarak işaretlendi.")
    mark_as_unresolved.short_description = "Seçili hataları çözülmedi olarak işaretle"