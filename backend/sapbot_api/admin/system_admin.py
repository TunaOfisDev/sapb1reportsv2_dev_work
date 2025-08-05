# backend/sapbot_api/admin/system_admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import Textarea
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import timedelta
import json

from .base_admin import BaseModelAdmin, ReadOnlyMixin
from ..models.system import (
   SystemConfiguration,
   SystemMetrics,
   SystemLog,
   SystemHealth,
   APIQuota,
   SystemNotification,
   MaintenanceWindow
)


class ConfigTypeFilter(SimpleListFilter):
   """Konfigürasyon tipi filtresi"""
   title = 'Konfigürasyon Tipi'
   parameter_name = 'config_type'

   def lookups(self, request, model_admin):
       return SystemConfiguration.CONFIG_TYPE_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(config_type=self.value())
       return queryset


class CategoryFilter(SimpleListFilter):
   """Kategori filtresi"""
   title = 'Kategori'
   parameter_name = 'category'

   def lookups(self, request, model_admin):
       categories = SystemConfiguration.objects.values_list('category', flat=True).distinct()
       return [(cat, cat.title()) for cat in categories if cat]

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(category=self.value())
       return queryset


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(BaseModelAdmin):
   """Sistem Konfigürasyon Admin"""
   
   list_display = [
       'key', 
       'value_preview', 
       'config_type', 
       'category',
       'is_editable_icon',
       'is_sensitive_icon',
       'updated_by',
       'updated_at'
   ]
   
   list_filter = [
       ConfigTypeFilter,
       CategoryFilter,
       'is_editable',
       'is_sensitive',
       'config_type'
   ]
   
   search_fields = [
       'key', 
       'description', 
       'category'
   ]
   
   readonly_fields = [
       'id',
       'created_at',
       'updated_at',
       'typed_value_display'
   ]
   
   fieldsets = (
       ('Temel Bilgiler', {
           'fields': (
               'key',
               'value',
               'config_type',
               'typed_value_display'
           )
       }),
       ('Açıklama ve Kategori', {
           'fields': (
               'description',
               'category',
               'default_value'
           )
       }),
       ('Güvenlik ve Erişim', {
           'fields': (
               'is_sensitive',
               'is_editable',
               'validation_regex'
           )
       }),
       ('İzleme', {
           'fields': (
               'updated_by',
               'created_at',
               'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   formfield_overrides = {
       models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
   }
   
   def value_preview(self, obj):
       """Değer önizleme"""
       if obj.is_sensitive:
           return "*** (Hassas Veri) ***"
       
       value = obj.value
       if len(value) > 50:
           return f"{value[:47]}..."
       return value
   value_preview.short_description = 'Değer'
   
   def typed_value_display(self, obj):
       """Tip dönüştürülmüş değer gösterimi"""
       if obj.is_sensitive:
           return "*** (Hassas Veri) ***"
       
       try:
           typed_value = obj.get_typed_value()
           return format_html(
               '<code style="background: #f8f9fa; padding: 2px 4px; border-radius: 3px;">{}</code>',
               str(typed_value)
           )
       except Exception as e:
           return format_html(
               '<span style="color: red;">Hata: {}</span>',
               str(e)
           )
   typed_value_display.short_description = 'Dönüştürülmüş Değer'
   
   def is_editable_icon(self, obj):
       """Düzenlenebilir ikonu"""
       if obj.is_editable:
           return format_html(
               '<span style="color: green;">✓ Evet</span>'
           )
       return format_html(
           '<span style="color: red;">✗ Hayır</span>'
       )
   is_editable_icon.short_description = 'Düzenlenebilir'
   
   def is_sensitive_icon(self, obj):
       """Hassas veri ikonu"""
       if obj.is_sensitive:
           return format_html(
               '<span style="color: orange;">⚠ Hassas</span>'
           )
       return format_html(
           '<span style="color: green;">✓ Normal</span>'
       )
   is_sensitive_icon.short_description = 'Hassaslık'
   
   def get_readonly_fields(self, request, obj=None):
       """Readonly alanları dinamik belirle"""
       readonly = list(self.readonly_fields)
       
       if obj and not obj.is_editable:
           readonly.extend(['key', 'value', 'config_type'])
       
       if not request.user.is_superuser:
           readonly.extend(['is_sensitive', 'validation_regex'])
       
       return readonly
   
   def save_model(self, request, obj, form, change):
       """Model kaydetme - updated_by alanını otomatik doldur"""
       obj.updated_by = request.user
       super().save_model(request, obj, form, change)
   
   def has_delete_permission(self, request, obj=None):
       """Silme izni kontrolü"""
       if obj and not obj.is_editable:
           return False
       return super().has_delete_permission(request, obj)


class MetricTypeFilter(SimpleListFilter):
   """Metrik tipi filtresi"""
   title = 'Metrik Tipi'
   parameter_name = 'metric_type'

   def lookups(self, request, model_admin):
       return SystemMetrics.METRIC_TYPE_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(metric_type=self.value())
       return queryset


@admin.register(SystemMetrics)
class SystemMetricsAdmin(ReadOnlyMixin, BaseModelAdmin):
   """Sistem Metrik Admin - Sadece Okuma"""
   
   list_display = [
       'metric_name',
       'metric_type',
       'value_formatted',
       'labels_display',
       'timestamp'
   ]
   
   list_filter = [
       MetricTypeFilter,
       'metric_name',
       'timestamp'
   ]
   
   search_fields = [
       'metric_name'
   ]
   
   date_hierarchy = 'timestamp'
   
   ordering = ['-timestamp']
   
   def value_formatted(self, obj):
       """Değeri formatla"""
       if obj.metric_type == 'counter':
           return format_html(
               '<strong style="color: #007cba;">{:,.0f}</strong>',
               obj.value
           )
       elif obj.metric_type == 'gauge':
           color = '#28a745' if obj.value > 0 else '#dc3545'
           return format_html(
               '<span style="color: {};">{:.2f}</span>',
               color, obj.value
           )
       else:
           return f"{obj.value:.2f}"
   value_formatted.short_description = 'Değer'
   
   def labels_display(self, obj):
       """Etiketleri göster"""
       if not obj.labels:
           return "-"
       
       labels = []
       for key, value in obj.labels.items():
           labels.append(f"{key}={value}")
       
       return format_html(
           '<small style="color: #6c757d;">{}</small>',
           ', '.join(labels[:3])  # İlk 3 etiketi göster
       )
   labels_display.short_description = 'Etiketler'


class LogLevelFilter(SimpleListFilter):
   """Log seviye filtresi"""
   title = 'Log Seviyesi'
   parameter_name = 'level'

   def lookups(self, request, model_admin):
       return SystemLog.LOG_LEVEL_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(level=self.value())
       return queryset


class RecentLogsFilter(SimpleListFilter):
   """Son loglar filtresi"""
   title = 'Zaman Aralığı'
   parameter_name = 'recent'

   def lookups(self, request, model_admin):
       return (
           ('1h', 'Son 1 Saat'),
           ('6h', 'Son 6 Saat'),
           ('24h', 'Son 24 Saat'),
           ('7d', 'Son 7 Gün'),
       )

   def queryset(self, request, queryset):
       if self.value():
           now = timezone.now()
           if self.value() == '1h':
               time_threshold = now - timedelta(hours=1)
           elif self.value() == '6h':
               time_threshold = now - timedelta(hours=6)
           elif self.value() == '24h':
               time_threshold = now - timedelta(days=1)
           elif self.value() == '7d':
               time_threshold = now - timedelta(days=7)
           else:
               return queryset
           
           return queryset.filter(created_at__gte=time_threshold)
       return queryset


@admin.register(SystemLog)
class SystemLogAdmin(ReadOnlyMixin, BaseModelAdmin):
   """Sistem Log Admin - Sadece Okuma"""
   
   list_display = [
       'level_colored',
       'message_preview',
       'module',
       'function',
       'user',
       'created_at'
   ]
   
   list_filter = [
       LogLevelFilter,
       RecentLogsFilter,
       'module',
       'level'
   ]
   
   search_fields = [
       'message',
       'module',
       'function',
       'user__email'
   ]
   
   date_hierarchy = 'created_at'
   
   ordering = ['-created_at']
   
   list_per_page = 50
   
   readonly_fields = [
       'level',
       'message',
       'module',
       'function',
       'line_number',
       'user',
       'session_id',
       'ip_address',
       'user_agent',
       'extra_data_formatted',
       'created_at'
   ]
   
   fieldsets = (
       ('Log Bilgileri', {
           'fields': (
               'level',
               'message',
               'module',
               'function',
               'line_number'
           )
       }),
       ('Kullanıcı Bilgileri', {
           'fields': (
               'user',
               'session_id',
               'ip_address',
               'user_agent'
           )
       }),
       ('Ek Veriler', {
           'fields': (
               'extra_data_formatted',
           ),
           'classes': ('collapse',)
       }),
       ('Zaman', {
           'fields': (
               'created_at',
           )
       })
   )
   
   def level_colored(self, obj):
       """Renkli log seviyesi"""
       colors = {
           'DEBUG': '#6c757d',
           'INFO': '#007bff',
           'WARNING': '#ffc107',
           'ERROR': '#dc3545',
           'CRITICAL': '#6f42c1'
       }
       
       color = colors.get(obj.level, '#000000')
       return format_html(
           '<span style="color: {}; font-weight: bold;">{}</span>',
           color, obj.level
       )
   level_colored.short_description = 'Seviye'
   
   def message_preview(self, obj):
       """Mesaj önizleme"""
       message = obj.message
       if len(message) > 100:
           return f"{message[:97]}..."
       return message
   message_preview.short_description = 'Mesaj'
   
   def extra_data_formatted(self, obj):
       """Ek verileri formatla"""
       if not obj.extra_data:
           return "-"
       
       try:
           formatted = json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
           return format_html(
               '<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>',
               formatted
           )
       except Exception:
           return str(obj.extra_data)
   extra_data_formatted.short_description = 'Ek Veriler'


class HealthStatusFilter(SimpleListFilter):
   """Sağlık durumu filtresi"""
   title = 'Sağlık Durumu'
   parameter_name = 'status'

   def lookups(self, request, model_admin):
       return SystemHealth.HEALTH_STATUS_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(status=self.value())
       return queryset


@admin.register(SystemHealth)
class SystemHealthAdmin(ReadOnlyMixin, BaseModelAdmin):
   """Sistem Sağlık Admin - Sadece Okuma"""
   
   list_display = [
       'component',
       'status_colored',
       'response_time_formatted',
       'error_message_preview',
       'created_at'
   ]
   
   list_filter = [
       HealthStatusFilter,
       'component',
       'created_at'
   ]
   
   search_fields = [
       'component',
       'error_message'
   ]
   
   date_hierarchy = 'created_at'
   
   ordering = ['-created_at']
   
   def status_colored(self, obj):
       """Renkli durum gösterimi"""
       colors = {
           'healthy': '#28a745',
           'warning': '#ffc107',
           'critical': '#fd7e14',
           'down': '#dc3545'
       }
       
       icons = {
           'healthy': '✓',
           'warning': '⚠',
           'critical': '⚡',
           'down': '✗'
       }
       
       color = colors.get(obj.status, '#6c757d')
       icon = icons.get(obj.status, '?')
       
       return format_html(
           '<span style="color: {}; font-weight: bold;">{} {}</span>',
           color, icon, obj.get_status_display()
       )
   status_colored.short_description = 'Durum'
   
   def response_time_formatted(self, obj):
       """Yanıt süresini formatla"""
       if obj.response_time is None:
           return "-"
       
       if obj.response_time < 100:
           color = '#28a745'  # Yeşil
       elif obj.response_time < 500:
           color = '#ffc107'  # Sarı
       else:
           color = '#dc3545'  # Kırmızı
       
       return format_html(
           '<span style="color: {};">{:.1f} ms</span>',
           color, obj.response_time
       )
   response_time_formatted.short_description = 'Yanıt Süresi'
   
   def error_message_preview(self, obj):
       """Hata mesajı önizleme"""
       if not obj.error_message:
           return "-"
       
       message = obj.error_message
       if len(message) > 50:
           return f"{message[:47]}..."
       return message
   error_message_preview.short_description = 'Hata Mesajı'


@admin.register(APIQuota)
class APIQuotaAdmin(BaseModelAdmin):
   """API Kota Admin"""
   
   list_display = [
       'endpoint',
       'user',
       'quota_type',
       'usage_progress',
       'reset_at',
       'is_exceeded_icon'
   ]
   
   list_filter = [
       'quota_type',
       'endpoint',
       'reset_at'
   ]
   
   search_fields = [
       'endpoint',
       'user__email',
       'api_key'
   ]
   
   readonly_fields = [
       'id',
       'created_at',
       'updated_at',
       'usage_percentage_display',
       'is_exceeded'
   ]
   
   fieldsets = (
       ('Kota Bilgileri', {
           'fields': (
               'user',
               'api_key',
               'endpoint',
               'quota_type'
           )
       }),
       ('Limitler', {
           'fields': (
               'limit_count',
               'current_count',
               'usage_percentage_display',
               'reset_at'
           )
       }),
       ('İzleme', {
           'fields': (
               'created_at',
               'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   def usage_progress(self, obj):
       """Kullanım ilerlemesi"""
       percentage = obj.usage_percentage
       
       if percentage < 50:
           color = '#28a745'
       elif percentage < 80:
           color = '#ffc107'
       else:
           color = '#dc3545'
       
       return format_html(
           '<div style="width: 100px; background: #e9ecef; border-radius: 10px; overflow: hidden;">'
           '<div style="width: {}%; height: 20px; background: {}; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
           '{}%'
           '</div>'
           '</div>',
           percentage, color, int(percentage)
       )
   usage_progress.short_description = 'Kullanım'
   
   def usage_percentage_display(self, obj):
       """Kullanım yüzdesi gösterimi"""
       return f"{obj.usage_percentage:.1f}%"
   usage_percentage_display.short_description = 'Kullanım Yüzdesi'
   
   def is_exceeded_icon(self, obj):
       """Aşım durumu ikonu"""
       if obj.is_exceeded:
           return format_html(
               '<span style="color: red; font-weight: bold;">⚠ AŞILDI</span>'
           )
       return format_html(
           '<span style="color: green;">✓ Normal</span>'
       )
   is_exceeded_icon.short_description = 'Durum'


class NotificationTypeFilter(SimpleListFilter):
   """Bildirim tipi filtresi"""
   title = 'Bildirim Tipi'
   parameter_name = 'notification_type'

   def lookups(self, request, model_admin):
       return SystemNotification.NOTIFICATION_TYPE_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(notification_type=self.value())
       return queryset


@admin.register(SystemNotification)
class SystemNotificationAdmin(BaseModelAdmin):
   """Sistem Bildirimi Admin"""
   
   list_display = [
       'title',
       'notification_type_colored',
       'priority_stars',
       'is_system_wide_icon',
       'is_read_icon',
       'expires_at',
       'created_at'
   ]
   
   list_filter = [
       NotificationTypeFilter,
       'priority',
       'is_system_wide',
       'is_read',
       'expires_at'
   ]
   
   search_fields = [
       'title',
       'message'
   ]
   
   date_hierarchy = 'created_at'
   
   ordering = ['-priority', '-created_at']
   
   filter_horizontal = ['target_users']
   
   fieldsets = (
       ('Bildirim İçeriği', {
           'fields': (
               'title',
               'message',
               'notification_type',
               'priority'
           )
       }),
       ('Hedefleme', {
           'fields': (
               'is_system_wide',
               'target_users'
           )
       }),
       ('Eylem', {
           'fields': (
               'action_url',
               'action_text'
           )
       }),
       ('Durum', {
           'fields': (
               'is_read',
               'expires_at'
           )
       })
   )
   
   def notification_type_colored(self, obj):
       """Renkli bildirim tipi"""
       colors = {
           'info': '#17a2b8',
           'warning': '#ffc107',
           'error': '#dc3545',
           'success': '#28a745'
       }
       
       color = colors.get(obj.notification_type, '#6c757d')
       return format_html(
           '<span style="color: {}; font-weight: bold;">{}</span>',
           color, obj.get_notification_type_display()
       )
   notification_type_colored.short_description = 'Tip'
   
   def priority_stars(self, obj):
       """Öncelik yıldızları"""
       stars = '★' * obj.priority + '☆' * (4 - obj.priority)
       
       if obj.priority >= 3:
           color = '#dc3545'
       elif obj.priority == 2:
           color = '#ffc107'
       else:
           color = '#6c757d'
       
       return format_html(
           '<span style="color: {};">{}</span>',
           color, stars
       )
   priority_stars.short_description = 'Öncelik'
   
   def is_system_wide_icon(self, obj):
       """Sistem geneli ikonu"""
       if obj.is_system_wide:
           return format_html(
               '<span style="color: blue;">🌐 Sistem Geneli</span>'
           )
       return format_html(
           '<span style="color: gray;">👤 Kullanıcı Özel</span>'
       )
   is_system_wide_icon.short_description = 'Kapsam'
   
   def is_read_icon(self, obj):
       """Okunma durumu ikonu"""
       if obj.is_read:
           return format_html(
               '<span style="color: green;">✓ Okundu</span>'
           )
       return format_html(
           '<span style="color: orange;">● Yeni</span>'
       )
   is_read_icon.short_description = 'Durum'


class MaintenanceStatusFilter(SimpleListFilter):
   """Bakım durumu filtresi"""
   title = 'Bakım Durumu'
   parameter_name = 'status'

   def lookups(self, request, model_admin):
       return MaintenanceWindow.STATUS_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(status=self.value())
       return queryset


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(BaseModelAdmin):
   """Bakım Penceresi Admin"""
   
   list_display = [
       'title',
       'status_colored',
       'maintenance_period',
       'duration_formatted',
       'affects_summary',
       'created_by'
   ]
   
   list_filter = [
       MaintenanceStatusFilter,
       'affects_api',
       'affects_chat',
       'affects_upload',
       'start_time'
   ]
   
   search_fields = [
       'title',
       'description'
   ]
   
   date_hierarchy = 'start_time'
   
   ordering = ['-start_time']
   
   readonly_fields = [
       'id',
       'created_at',
       'updated_at',
       'duration_minutes_display',
       'is_active'
   ]
   
   fieldsets = (
       ('Bakım Bilgileri', {
           'fields': (
               'title',
               'description',
               'status'
           )
       }),
       ('Zaman Planı', {
           'fields': (
               'start_time',
               'end_time',
               'duration_minutes_display'
           )
       }),
       ('Etkilenen Servisler', {
           'fields': (
               'affects_api',
               'affects_chat',
               'affects_upload'
           )
       }),
       ('İzleme', {
           'fields': (
               'created_by',
               'created_at',
               'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   def status_colored(self, obj):
       """Renkli durum gösterimi"""
       colors = {
           'scheduled': '#007bff',
           'in_progress': '#ffc107',
           'completed': '#28a745',
           'cancelled': '#6c757d'
       }
       
       color = colors.get(obj.status, '#000000')
       return format_html(
           '<span style="color: {}; font-weight: bold;">{}</span>',
           color, obj.get_status_display()
       )
   status_colored.short_description = 'Durum'
   
   def maintenance_period(self, obj):
       """Bakım periyodu"""
       start = obj.start_time.strftime('%d.%m.%Y %H:%M')
       end = obj.end_time.strftime('%d.%m.%Y %H:%M')
       
       return format_html(
           '<div><strong>Başlangıç:</strong> {}</div>'
           '<div><strong>Bitiş:</strong> {}</div>',
           start, end
       )
   maintenance_period.short_description = 'Bakım Periyodu'
   
   def duration_formatted(self, obj):
       """Süreyi formatla"""
       duration = obj.duration_minutes
       
       if duration < 60:
           return f"{int(duration)} dakika"
       elif duration < 1440:  # 24 saat
           hours = int(duration // 60)
           minutes = int(duration % 60)
           return f"{hours}s {minutes}d"
       else:
           days = int(duration // 1440)
           hours = int((duration % 1440) // 60)
           return f"{days} gün {hours}s"
   duration_formatted.short_description = 'Süre'
   
   def duration_minutes_display(self, obj):
       """Dakika olarak süre"""
       return f"{obj.duration_minutes:.0f} dakika"
   duration_minutes_display.short_description = 'Süre (Dakika)'
   
   def affects_summary(self, obj):
       """Etkilenen servisler özeti"""
       affected = []
       if obj.affects_api:
           affected.append("API")
       if obj.affects_chat:
           affected.append("Chat")
       if obj.affects_upload:
           affected.append("Upload")
       
       if not affected:
           return format_html('<span style="color: gray;">Hiçbiri</span>')
       
       return format_html(
           '<span style="color: orange;">{}</span>',
           ', '.join(affected)
       )
   affects_summary.short_description = 'Etkilenen Servisler'
   
   def save_model(self, request, obj, form, change):
       """Model kaydetme - created_by alanını otomatik doldur"""
       if not change:  # Yeni kayıt
           obj.created_by = request.user
       super().save_model(request, obj, form, change)


# Admin site customization
admin.site.site_header = "SAPBot API Sistem Yönetimi"
admin.site.site_title = "SAPBot Admin"
admin.site.index_title = "Sistem Yönetim Paneli"
