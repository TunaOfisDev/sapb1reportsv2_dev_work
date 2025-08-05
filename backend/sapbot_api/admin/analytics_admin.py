# backend/sapbot_api/admin/analytics_admin.py
from django.contrib import admin
from django.db.models import Count, Avg, Sum
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .base_admin import (
    BaseModelAdmin, 
    ExportMixin, 
    DateRangeFilter as BaseDateRangeFilter,
    BulkActionsMixin
)
from ..models.analytics import (
    QueryAnalytics, UserFeedback, UsageStatistics, 
    PerformanceMetrics, ErrorLog
)
from ..utils.helpers import format_response_time, format_percentage


class AnalyticsDateRangeFilter(BaseDateRangeFilter):
    """Analytics özelinde tarih filtresi"""
    def get_default_lookups(self):
        return super().get_default_lookups() + [
            ('quarter', 'Bu Çeyrek'),
            ('half_year', '6 Ay'),
        ]


class SAPModuleFilter(SimpleListFilter):
    """SAP modül filtresi"""
    title = 'SAP Modülü'
    parameter_name = 'sap_module'

    def lookups(self, request, model_admin):
        return (
            ('FI', 'Mali Muhasebe'),
            ('MM', 'Malzeme Yönetimi'),
            ('SD', 'Satış ve Dağıtım'),
            ('CRM', 'Müşteri İlişkileri'),
            ('PROD', 'Üretim'),
            ('HR', 'İnsan Kaynakları'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sap_module_detected=self.value())
        return queryset


class AnalyticsExportMixin(ExportMixin):
    """Analytics özelinde export işlemleri"""
    
    def get_export_filename(self, format_type='csv'):
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        return f"sapbot_analytics_{timestamp}.{format_type}"
    
    def get_export_fields(self):
        return [
            'created_at', 'query', 'user_type', 'sap_module_detected',
            'intent_detected', 'confidence_score', 'response_time',
            'tokens_used', 'cost_estimate'
        ]


@admin.register(QueryAnalytics)
class QueryAnalyticsAdmin(BaseModelAdmin, AnalyticsExportMixin, BulkActionsMixin):
    list_display = [
        'query_preview', 'user_display', 'user_type', 'sap_module_detected',
        'intent_detected', 'confidence_badge', 'response_time_display',
        'success_status', 'created_at_short'
    ]
    
    list_filter = [
        AnalyticsDateRangeFilter, 'user_type', 'sap_module_detected', 
        'intent_detected', 'response_generated', 'error_occurred', SAPModuleFilter
    ]
    
    search_fields = ['query', 'user__email', 'session_id']
    
    readonly_fields = BaseModelAdmin.readonly_fields = (
        'query_hash',
        'query_length',
        'metadata_display',
        'performance_summary',
    )
    
    fieldsets = (
        ('Sorgu Bilgileri', {
            'fields': ('query', 'query_hash', 'query_length', 'language_detected')
        }),
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'session_id', 'user_type', 'ip_address', 'user_agent')
        }),
        ('AI Analizi', {
            'fields': ('sap_module_detected', 'intent_detected', 'confidence_score')
        }),
        ('Performans', {
            'fields': ('response_generated', 'response_time', 'tokens_used', 'cost_estimate')
        }),
        ('Hata Bilgileri', {
            'fields': ('error_occurred', 'error_type'),
            'classes': ('collapse',)
        }),
    ) + BaseModelAdmin.base_fieldsets
    
    # Base admin'den gelen standart action'lar + özel action'lar
    actions = BaseModelAdmin.actions + [
        'export_detailed_analytics', 'recalculate_metrics'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def query_preview(self, obj):
        """Sorgu önizlemesi"""
        return self.truncate_text(obj.query, 80)
    query_preview.short_description = 'Sorgu'
    
    def user_display(self, obj):
        """Kullanıcı gösterimi"""
        if obj.user:
            return self.link_to_object(obj.user, obj.user.email)
        return self.format_empty('Anonim')
    user_display.short_description = 'Kullanıcı'
    
    def confidence_badge(self, obj):
        """Güven skoru badge"""
        if obj.confidence_score is None:
            return '-'
        
        confidence = obj.confidence_score
        return self.format_badge(
            f"{confidence:.2f}",
            'success' if confidence >= 0.8 else 'warning' if confidence >= 0.6 else 'danger'
        )
    confidence_badge.short_description = 'Güven'
    
    def response_time_display(self, obj):
        """Yanıt süresi gösterimi"""
        if obj.response_time:
            return format_response_time(obj.response_time)
        return '-'
    response_time_display.short_description = 'Yanıt Süresi'
    
    def success_status(self, obj):
        """Başarı durumu"""
        if obj.error_occurred:
            return self.format_status('Hata', 'error')
        elif obj.response_generated:
            return self.format_status('Başarılı', 'success')
        else:
            return self.format_status('İşleniyor', 'warning')
    success_status.short_description = 'Durum'
    
    def metadata_display(self, obj):
        """Metadata görüntüleme"""
        return self.format_json(obj.metadata)
    metadata_display.short_description = 'Metadata'
    
    def performance_summary(self, obj):
        """Performans özeti"""
        summary = []
        
        if obj.response_time:
            summary.append(f"Yanıt: {format_response_time(obj.response_time)}")
        
        if obj.tokens_used:
            summary.append(f"Token: {obj.tokens_used:,}")
        
        if obj.cost_estimate:
            summary.append(f"Maliyet: ${obj.cost_estimate:.4f}")
        
        if obj.sources_used_count:
            summary.append(f"Kaynak: {obj.sources_used_count}")
        
        return mark_safe('<br>'.join(summary)) if summary else '-'
    performance_summary.short_description = 'Performans Özeti'
    
    def export_detailed_analytics(self, request, queryset):
        """Detaylı analytics export"""
        return self.export_to_excel(request, queryset, 'detailed_analytics')
    export_detailed_analytics.short_description = "Detaylı analytics export et"
    
    def recalculate_metrics(self, request, queryset):
        """Metrikleri yeniden hesapla"""
        count = 0
        for obj in queryset:
            # Metrik hesaplama logic'i burada olacak
            count += 1
        
        self.success_message(request, f"{count} kayıt için metrikler yeniden hesaplandı.")
    recalculate_metrics.short_description = "Metrikleri yeniden hesapla"


@admin.register(UserFeedback)
class UserFeedbackAdmin(BaseModelAdmin, AnalyticsExportMixin):
    list_display = [
        'feedback_preview', 'user_display', 'rating_stars', 'feedback_type',
        'is_helpful_display', 'is_processed', 'created_at_short'
    ]
    
    list_filter = [
        AnalyticsDateRangeFilter, 'feedback_type', 'rating', 'is_helpful', 
        'is_processed', 'satisfaction'
    ]
    
    search_fields = ['comment', 'user__email', 'improvement_suggestions']
    
    fieldsets = (
        ('Geri Bildirim', {
            'fields': ('user', 'message', 'feedback_type', 'rating', 'satisfaction')
        }),
        ('Detaylar', {
            'fields': ('comment', 'is_helpful', 'improvement_suggestions')
        }),
        ('İletişim', {
            'fields': ('contact_email', 'response_sent')
        }),
        ('İşleme', {
            'fields': ('is_processed', 'processed_at')
        }),
    ) + BaseModelAdmin.base_fieldsets
    
    actions = BaseModelAdmin.actions + ['mark_as_processed', 'send_response']
    
    def feedback_preview(self, obj):
        """Geri bildirim önizlemesi"""
        if obj.comment:
            return self.truncate_text(obj.comment, 60)
        return f"{obj.get_feedback_type_display()}"
    feedback_preview.short_description = 'Geri Bildirim'
    
    def user_display(self, obj):
        """Kullanıcı gösterimi"""
        if obj.user:
            return self.link_to_object(obj.user, obj.user.email)
        elif obj.contact_email:
            return obj.contact_email
        return self.format_empty('Anonim')
    user_display.short_description = 'Kullanıcı'
    
    def rating_stars(self, obj):
        """Yıldız puanı"""
        if obj.rating:
            return self.format_rating(obj.rating, 5)
        return '-'
    rating_stars.short_description = 'Puan'
    
    def is_helpful_display(self, obj):
        """Faydalı mı gösterimi"""
        if obj.is_helpful is True:
            return self.format_status('Evet', 'success')
        elif obj.is_helpful is False:
            return self.format_status('Hayır', 'error')
        return '-'
    is_helpful_display.short_description = 'Faydalı mı?'
    
    def mark_as_processed(self, request, queryset):
        """İşlendi olarak işaretle"""
        count = queryset.filter(is_processed=False).update(
            is_processed=True,
            processed_at=timezone.now()
        )
        self.success_message(request, f"{count} geri bildirim işlendi olarak işaretlendi.")
    mark_as_processed.short_description = "İşlendi olarak işaretle"


@admin.register(UsageStatistics)
class UsageStatisticsAdmin(BaseModelAdmin, AnalyticsExportMixin):
    list_display = [
        'date', 'metric_type', 'queries_summary', 'users_summary',
        'success_rate_display', 'avg_response_time_display'
    ]
    
    list_filter = ['metric_type', 'date']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('date', 'metric_type')
        }),
        ('Sorgu İstatistikleri', {
            'fields': ('total_queries', 'successful_queries', 'failed_queries')
        }),
        ('Kullanıcı İstatistikleri', {
            'fields': ('unique_users', 'unique_sessions')
        }),
        ('Performans', {
            'fields': ('avg_response_time', 'avg_satisfaction')
        }),
        ('Maliyet', {
            'fields': ('total_tokens_used', 'total_cost')
        }),
        ('Döküman İşleme', {
            'fields': ('documents_processed', 'chunks_created')
        }),
    ) + BaseModelAdmin.base_fieldsets
    
    def queries_summary(self, obj):
        """Sorgu özeti"""
        return format_html(
            'Toplam: <strong>{:,}</strong><br>'
            'Başarılı: <span style="color: green;">{:,}</span><br>'
            'Başarısız: <span style="color: red;">{:,}</span>',
            obj.total_queries,
            obj.successful_queries,
            obj.failed_queries
        )
    queries_summary.short_description = 'Sorgular'
    
    def success_rate_display(self, obj):
        """Başarı oranı gösterimi"""
        rate = obj.success_rate
        badge_type = 'success' if rate >= 90 else 'warning' if rate >= 70 else 'danger'
        return self.format_badge(f"{rate:.1f}%", badge_type)
    success_rate_display.short_description = 'Başarı Oranı'
    
    def avg_response_time_display(self, obj):
        """Ortalama yanıt süresi"""
        return format_response_time(obj.avg_response_time)
    avg_response_time_display.short_description = 'Ort. Yanıt Süresi'


@admin.register(ErrorLog)
class ErrorLogAdmin(BaseModelAdmin, AnalyticsExportMixin):
    list_display = [
        'error_summary', 'user_display', 'error_level_badge', 
        'component', 'is_resolved', 'created_at_short'
    ]
    
    list_filter = [
        AnalyticsDateRangeFilter, 'error_type', 'error_level', 'component', 'is_resolved'
    ]
    
    search_fields = ['error_message', 'component', 'function_name', 'user__email']
    
    fieldsets = (
        ('Hata Bilgileri', {
            'fields': ('error_type', 'error_level', 'error_message')
        }),
        ('Konum', {
            'fields': ('component', 'function_name', 'line_number')
        }),
        ('Kullanıcı', {
            'fields': ('user', 'session_id', 'ip_address', 'user_agent')
        }),
        ('Çözüm', {
            'fields': ('is_resolved', 'resolved_at', 'resolution_notes')
        }),
        ('Teknik Detaylar', {
            'fields': ('stack_trace_display', 'request_data', 'context_display'),
            'classes': ('collapse',)
        }),
    ) + BaseModelAdmin.base_fieldsets
    
    actions = BaseModelAdmin.actions + ['mark_as_resolved']
    
    def error_summary(self, obj):
        """Hata özeti"""
        return self.truncate_text(obj.error_message, 80)
    error_summary.short_description = 'Hata'
    
    def error_level_badge(self, obj):
        """Hata seviyesi badge"""
        level_mapping = {
            'low': 'info',
            'medium': 'warning', 
            'high': 'danger',
            'critical': 'danger'
        }
        badge_type = level_mapping.get(obj.error_level, 'secondary')
        return self.format_badge(obj.get_error_level_display(), badge_type)
    error_level_badge.short_description = 'Seviye'
    
    def stack_trace_display(self, obj):
        """Stack trace görüntüleme"""
        return self.format_code_block(obj.stack_trace, max_height='300px')
    stack_trace_display.short_description = 'Stack Trace'
    
    def context_display(self, obj):
        """Context görüntüleme"""
        return self.format_json(obj.context)
    context_display.short_description = 'Context'