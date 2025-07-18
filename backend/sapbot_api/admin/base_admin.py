# backend/sapbot_api/admin/base_admin.py
"""
SAPBot API Base Admin Classes

Bu modül Django admin için temel sınıfları ve mixin'leri içerir.
Tüm admin sınıfları bu temel sınıflardan türetilmelidir.
"""
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import json
import json as _json
import csv
from django.http import HttpResponse
import logging
from ..utils.helpers import format_file_size, time_ago
from ..utils.security import SecurityAuditor

logger = logging.getLogger(__name__)


class BaseModelAdmin(admin.ModelAdmin):
   """Tüm admin sınıfları için temel admin sınıfı"""
   
   # Genel ayarlar
   list_per_page = 25
   list_max_show_all = 100
   save_on_top = True
   save_as = True
   preserve_filters = True
   
   # Varsayılan sütunlar
   readonly_fields = ('id', 'created_at', 'updated_at')
   list_display = ('__str__', 'is_active', 'created_at')
   list_filter = ('is_active', 'created_at')
   search_fields = ('id',)
   ordering = ('-created_at',)
   
   # Fieldsets
   fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("created_at", "updated_at")
        }),
       ('Sistem Bilgileri', {
           'fields': ('id', 'created_at', 'updated_at'),
           'classes': ('collapse',)
       }),
   )
   
   def get_readonly_fields(self, request, obj=None):
       """Readonly field'ları dinamik olarak belirle"""
       readonly = list(self.readonly_fields)
       
       # Yeni kayıt değilse ID'yi readonly yap
       if obj:
           if 'id' not in readonly:
               readonly.append('id')
       
       return readonly
   
   def get_list_display(self, request):
       """List display'i dinamik olarak belirle"""
       display_fields = list(self.list_display)
       
       # Süper kullanıcılara ekstra bilgiler göster
       if request.user.is_superuser:
           if 'id' not in display_fields:
               display_fields.insert(-1, 'id')
       
       return display_fields
   
   def save_model(self, request, obj, form, change):
       """Model kaydetme işlemini özelleştir"""
       # Audit log için
       action_type = 'UPDATE' if change else 'CREATE'
       
       try:
           super().save_model(request, obj, form, change)
           
           # Başarılı işlemi logla
           SecurityAuditor.log_security_event(
               event_type=f'ADMIN_{action_type}',
               user=request.user,
               request=request,
               details={
                   'model': obj.__class__.__name__,
                   'object_id': str(obj.pk),
                   'changes': form.changed_data if hasattr(form, 'changed_data') else []
               },
               severity='INFO'
           )
           
       except Exception as e:
           logger.error(f"Admin model save hatası: {e}")
           SecurityAuditor.log_security_event(
               event_type=f'ADMIN_{action_type}_FAILED',
               user=request.user,
               request=request,
               details={
                   'model': obj.__class__.__name__,
                   'error': str(e)
               },
               severity='ERROR'
           )
           raise
   
   def delete_model(self, request, obj):
       """Model silme işlemini özelleştir"""
       try:
           model_name = obj.__class__.__name__
           object_id = str(obj.pk)
           
           super().delete_model(request, obj)
           
           # Silme işlemini logla
           SecurityAuditor.log_security_event(
               event_type='ADMIN_DELETE',
               user=request.user,
               request=request,
               details={
                   'model': model_name,
                   'object_id': object_id
               },
               severity='WARNING'
           )
           
       except Exception as e:
           logger.error(f"Admin model delete hatası: {e}")
           raise
   
   def get_queryset(self, request):
       """Queryset'i optimize et"""
       qs = super().get_queryset(request)
       
       # Select related ile N+1 problemini önle
       if hasattr(self.model, '_meta'):
           # Foreign key field'ları otomatik select_related
           fk_fields = [
               field.name for field in self.model._meta.fields
               if isinstance(field, models.ForeignKey)
           ]
           if fk_fields:
               qs = qs.select_related(*fk_fields[:3])  # Max 3 tane
       
       return qs
   
   def changelist_view(self, request, extra_context=None):
       """Changelist view'ını özelleştir"""
       extra_context = extra_context or {}
       
       # Model istatistikleri ekle
       try:
           total_count = self.model.objects.count()
           active_count = self.model.objects.filter(is_active=True).count() if hasattr(self.model, 'is_active') else total_count
           
           extra_context.update({
               'total_count': total_count,
               'active_count': active_count,
               'inactive_count': total_count - active_count,
           })
       except Exception as e:
           logger.warning(f"Admin changelist stats hatası: {e}")
       
       return super().changelist_view(request, extra_context)


class TimestampedModelAdmin(BaseModelAdmin):
   """Timestamp'li modeller için admin"""
   
   readonly_fields = ('created_at', 'updated_at')
   list_display = ('__str__', 'created_at', 'updated_at')
   list_filter = ('created_at', 'updated_at')
   
   fieldsets = (
       ('Zaman Bilgileri', {
           'fields': ('created_at', 'updated_at'),
           'classes': ('collapse',)
       }),
   )


class SoftDeleteModelAdmin(BaseModelAdmin):
   """Soft delete destekli modeller için admin"""
   
   def get_queryset(self, request):
       """Silinmiş kayıtları da göster"""
       return self.model.all_objects.get_queryset()
   
   def delete_queryset(self, request, queryset):
       """Toplu silme işlemi"""
       for obj in queryset:
           obj.delete()  # Soft delete
   
   actions = ['restore_selected', 'hard_delete_selected']
   
   def restore_selected(self, request, queryset):
       """Seçili kayıtları geri yükle"""
       count = 0
       for obj in queryset:
           if hasattr(obj, 'restore'):
               obj.restore()
               count += 1
       
       self.message_user(
           request,
           f"{count} kayıt başarıyla geri yüklendi.",
           messages.SUCCESS
       )
   restore_selected.short_description = "Seçili kayıtları geri yükle"
   
   def hard_delete_selected(self, request, queryset):
       """Seçili kayıtları kalıcı olarak sil"""
       if not request.user.is_superuser:
           raise PermissionDenied("Bu işlem için süper kullanıcı yetkisi gerekli")
       
       count = 0
       for obj in queryset:
           if hasattr(obj, 'hard_delete'):
               obj.hard_delete()
               count += 1
       
       self.message_user(
           request,
           f"{count} kayıt kalıcı olarak silindi.",
           messages.WARNING
       )
   hard_delete_selected.short_description = "Seçili kayıtları kalıcı olarak sil"


class ReadOnlyModelAdmin(BaseModelAdmin):
   """Sadece okunabilir modeller için admin"""
   
   def has_add_permission(self, request):
       return False
   
   def has_change_permission(self, request, obj=None):
       return False
   
   def has_delete_permission(self, request, obj=None):
       return False


class ExportableModelAdmin(BaseModelAdmin):
   """Export işlevi olan admin"""
   
   actions = ['export_as_json', 'export_as_csv']
   
   def export_as_json(self, request, queryset):
       """JSON olarak export et"""
       from django.core.serializers import serialize
       from django.http import HttpResponse
       
       response = HttpResponse(
           serialize('json', queryset, indent=2),
           content_type='application/json'
       )
       response['Content-Disposition'] = f'attachment; filename="{self.model.__name__.lower()}_export.json"'
       return response
   export_as_json.short_description = "JSON olarak export et"
   
   def export_as_csv(self, request, queryset):
       """CSV olarak export et"""
       import csv
       from django.http import HttpResponse
       
       response = HttpResponse(content_type='text/csv')
       response['Content-Disposition'] = f'attachment; filename="{self.model.__name__.lower()}_export.csv"'
       
       writer = csv.writer(response)
       
       # Header yaz
       field_names = [field.name for field in self.model._meta.fields]
       writer.writerow(field_names)
       
       # Data yaz
       for obj in queryset:
           row = []
           for field in field_names:
               value = getattr(obj, field, '')
               row.append(str(value) if value else '')
           writer.writerow(row)
       
       return response
   export_as_csv.short_description = "CSV olarak export et"


class BulkActionModelAdmin(BaseModelAdmin):
   """Toplu işlemler için admin"""
   
   actions = ['bulk_activate', 'bulk_deactivate']
   
   def bulk_activate(self, request, queryset):
       """Toplu aktifleştir"""
       if hasattr(self.model, 'is_active'):
           updated = queryset.update(is_active=True)
           self.message_user(
               request,
               f"{updated} kayıt aktifleştirildi.",
               messages.SUCCESS
           )
   bulk_activate.short_description = "Seçili kayıtları aktifleştir"
   
   def bulk_deactivate(self, request, queryset):
       """Toplu pasifleştir"""
       if hasattr(self.model, 'is_active'):
           updated = queryset.update(is_active=False)
           self.message_user(
               request,
               f"{updated} kayıt pasifleştirildi.",
               messages.WARNING
           )
   bulk_deactivate.short_description = "Seçili kayıtları pasifleştir"


# Custom List Filters
class DateRangeFilter(SimpleListFilter):
   """Tarih aralığı filtresi"""
   title = 'Tarih Aralığı'
   parameter_name = 'date_range'
   
   def lookups(self, request, model_admin):
       return [
           ('today', 'Bugün'),
           ('yesterday', 'Dün'),
           ('week', 'Bu Hafta'),
           ('month', 'Bu Ay'),
           ('year', 'Bu Yıl'),
       ]
   
   def queryset(self, request, queryset):
       now = timezone.now()
       
       if self.value() == 'today':
           return queryset.filter(created_at__date=now.date())
       elif self.value() == 'yesterday':
           yesterday = now.date() - timezone.timedelta(days=1)
           return queryset.filter(created_at__date=yesterday)
       elif self.value() == 'week':
           week_start = now - timezone.timedelta(days=now.weekday())
           return queryset.filter(created_at__gte=week_start)
       elif self.value() == 'month':
           month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
           return queryset.filter(created_at__gte=month_start)
       elif self.value() == 'year':
           year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
           return queryset.filter(created_at__gte=year_start)
       
       return queryset


class BooleanFilter(SimpleListFilter):
   """Boolean field için özelleştirilmiş filtre"""
   
   def __init__(self, request, params, model, model_admin, field_name, title=None):
       self.field_name = field_name
       if title:
           self.title = title
       super().__init__(request, params, model, model_admin)
   
   def lookups(self, request, model_admin):
       return [
           ('1', 'Evet'),
           ('0', 'Hayır'),
       ]
   
   def queryset(self, request, queryset):
       if self.value() == '1':
           return queryset.filter(**{self.field_name: True})
       elif self.value() == '0':
           return queryset.filter(**{self.field_name: False})
       return queryset


# Custom Field Displays
class ColoredBooleanMixin:
   """Boolean field'ları renkli göstermek için mixin"""
   
   def colored_boolean(self, obj, field_name):
       """Boolean field'ı renkli göster"""
       value = getattr(obj, field_name, None)
       if value is True:
           return format_html(
               '<span style="color: green; font-weight: bold;">✓ Evet</span>'
           )
       elif value is False:
           return format_html(
               '<span style="color: red; font-weight: bold;">✗ Hayır</span>'
           )
       return format_html('<span style="color: gray;">-</span>')


class FileSizeMixin:
   """Dosya boyutu göstermek için mixin"""
   
   def formatted_file_size(self, obj):
       """Dosya boyutunu formatla"""
       if hasattr(obj, 'file_size') and obj.file_size:
           return format_file_size(obj.file_size)
       return '-'
   formatted_file_size.short_description = 'Dosya Boyutu'


class TimestampMixin:
   """Zaman damgalarını formatlamak için mixin"""
   
   def formatted_created_at(self, obj):
       """Oluşturulma tarihini formatla"""
       if obj.created_at:
           return format_html(
               '<span title="{}">{}</span>',
               obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
               time_ago(obj.created_at)
           )
       return '-'
   formatted_created_at.short_description = 'Oluşturulma'
   
   def formatted_updated_at(self, obj):
       """Güncellenme tarihini formatla"""
       if obj.updated_at:
           return format_html(
               '<span title="{}">{}</span>',
               obj.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
               time_ago(obj.updated_at)
           )
       return '-'
   formatted_updated_at.short_description = 'Güncellenme'


class StatusMixin:
   """Status field'larını renkli göstermek için mixin"""
   
   def colored_status(self, obj, field_name, color_map=None):
       """Status'u renkli göster"""
       if not color_map:
           color_map = {
               'active': 'green',
               'inactive': 'red',
               'pending': 'orange',
               'processing': 'blue',
               'completed': 'green',
               'failed': 'red',
           }
       
       value = getattr(obj, field_name, None)
       if value:
           color = color_map.get(value.lower(), 'gray')
           display_value = value.replace('_', ' ').title()
           return format_html(
               '<span style="color: {}; font-weight: bold;">{}</span>',
               color,
               display_value
           )
       return '-'


class LinkMixin:
   """Link'ler için mixin"""
   
   def admin_link(self, obj, field_name, link_text=None):
       """Admin link oluştur"""
       related_obj = getattr(obj, field_name, None)
       if related_obj:
           link_text = link_text or str(related_obj)
           url = reverse(
               f'admin:{related_obj._meta.app_label}_{related_obj._meta.model_name}_change',
               args=[related_obj.pk]
           )
           return format_html('<a href="{}">{}</a>', url, link_text)
       return '-'
   
   def external_link(self, obj, field_name, link_text=None):
       """Harici link oluştur"""
       url = getattr(obj, field_name, None)
       if url:
           link_text = link_text or 'Link'
           return format_html(
               '<a href="{}" target="_blank" rel="noopener">{} ↗</a>',
               url,
               link_text
           )
       return '-'


class JSONFieldMixin:
   """JSON field'ları göstermek için mixin"""
   
   def formatted_json(self, obj, field_name):
       """JSON field'ı formatla"""
       data = getattr(obj, field_name, None)
       if data:
           try:
               formatted = json.dumps(data, indent=2, ensure_ascii=False)
               return format_html('<pre style="max-height: 200px; overflow: auto;">{}</pre>', formatted)
           except (TypeError, ValueError):
               return str(data)
       return '-'


# Utility Functions
def admin_action_required_permission(permission):
   """Admin action için permission kontrolü"""
   def decorator(func):
       def wrapper(self, request, queryset):
           if not request.user.has_perm(permission):
               raise PermissionDenied(f"Bu işlem için '{permission}' iznine ihtiyacınız var")
           return func(self, request, queryset)
       wrapper.__name__ = func.__name__
       wrapper.__doc__ = func.__doc__
       wrapper.short_description = getattr(func, 'short_description', func.__name__)
       return wrapper
   return decorator


def admin_ajax_response(success=True, message='', data=None):
   """Admin AJAX response helper"""
   return JsonResponse({
       'success': success,
       'message': message,
       'data': data or {}
   })


# Custom Widget Helper
class AdminRichTextWidget:
   """Rich text widget için helper"""
   
   class Media:
       css = {
           'all': ('sapbot_api/admin/css/rich-text.css',)
       }
       js = (
           'sapbot_api/admin/js/rich-text.js',
       )


# Admin Site Customization
def customize_admin_site():
   """Admin site'ı özelleştir"""
   admin.site.site_header = 'SAPBot API Yönetim Paneli'
   admin.site.site_title = 'SAPBot Admin'
   admin.site.index_title = 'SAPBot API Yönetimi'
   admin.site.site_url = '/api/sapbot/'
   admin.site.enable_nav_sidebar = True


# Health Check Mixin
class HealthCheckMixin:
   """Sistem sağlığı kontrolü için mixin"""
   
   def system_health_status(self, obj):
       """Sistem sağlık durumunu göster"""
       # Bu method'u model'e göre özelleştir
       try:
           if hasattr(obj, 'last_activity'):
               # Son aktiviteye göre durum belirleme
               last_activity = obj.last_activity
               if last_activity:
                   diff = timezone.now() - last_activity
                   if diff.total_seconds() < 300:  # 5 dakika
                       return format_html('<span style="color: green;">● Aktif</span>')
                   elif diff.total_seconds() < 3600:  # 1 saat
                       return format_html('<span style="color: orange;">● Uyarı</span>')
                   else:
                       return format_html('<span style="color: red;">● Pasif</span>')
           
           return format_html('<span style="color: gray;">● Bilinmiyor</span>')
       except Exception:
           return format_html('<span style="color: red;">● Hata</span>')
   
   system_health_status.short_description = 'Durum'


# Performance Optimization Mixin
class OptimizedQuerysetMixin:
   """Queryset optimizasyonu için mixin"""
   
   def get_queryset(self, request):
       """Optimize edilmiş queryset"""
       qs = super().get_queryset(request)
       
       # Prefetch related for Many-to-Many and reverse FK
       if hasattr(self, 'prefetch_related_fields'):
           qs = qs.prefetch_related(*self.prefetch_related_fields)
       
       # Select related for FK
       if hasattr(self, 'select_related_fields'):
           qs = qs.select_related(*self.select_related_fields)
       
       # Only select needed fields
       if hasattr(self, 'only_fields'):
           qs = qs.only(*self.only_fields)
       
       return qs


# Statistics Mixin
class StatisticsMixin:
   """İstatistik gösterimi için mixin"""
   
   def get_statistics(self, obj):
       """Model istatistiklerini al"""
       stats = {}
       
       # Bu method'u her model için özelleştir
       try:
           if hasattr(obj, 'usage_count'):
               stats['Kullanım'] = obj.usage_count
           
           if hasattr(obj, 'last_used') and obj.last_used:
               stats['Son Kullanım'] = time_ago(obj.last_used)
           
           return stats
       except Exception as e:
           logger.warning(f"Statistics hesaplama hatası: {e}")
           return {}
       

# ---------------------------------------------------------------------------
# Ek Yardımcı Mix-in’ler – analytics_admin ve diğer modüller için
# ---------------------------------------------------------------------------




class ExportMixin:
    """
    Temel CSV/“Excel” dışa-aktarımı sağlar.
    analytics_admin içindeki AnalyticsExportMixin bu sınıfı genişletir.
    """

    def export_to_excel(self, request, queryset, filename_prefix="export"):
        """
        Basit CSV çıktısı üretir (Excel ile açılabilir).
        """
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        field_names = [f.name for f in queryset.model._meta.fields]
        writer = csv.writer(response)
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response


class BulkActionsMixin:
    """
    Ortak yardımcı metotlar:
    • admin’e başarı/uyarı mesajı basma
    • badge, json, code-block biçimleme
    • link ve kısa metin yardımcıları
    """

    # --- Mesaj
    def success_message(self, request, message):
        self.message_user(request, message, messages.SUCCESS)

    # --- Görsel yardımcılar
    def format_badge(self, text, badge_type="secondary"):
        palette = {
            "success": "#27ae60",
            "warning": "#f39c12",
            "danger":  "#e74c3c",
            "info":    "#3498db",
            "secondary": "#7f8c8d",
        }
        color = palette.get(badge_type, "#7f8c8d")
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 6px; '
            'border-radius:4px; font-size:12px;">{}</span>',
            color,
            text,
        )

    def format_status(self, text, badge_type="secondary"):
        return self.format_badge(text, badge_type)

    def format_json(self, data):
        try:
            formatted = _json.dumps(data, indent=2, ensure_ascii=False)
        except TypeError:
            formatted = str(data)
        return format_html(
            '<pre style="max-height:200px; overflow:auto;">{}</pre>', formatted
        )

    def format_code_block(self, code, max_height="400px"):
        if not code:
            return "-"
        return format_html(
            '<pre style="max-height:{}; overflow:auto;">{}</pre>', max_height, code
        )

    # --- Kısa yardımcılar
    def truncate_text(self, text, max_len=60, ellipsis="…"):
        if not text:
            return "-"
        return text if len(text) <= max_len else text[:max_len] + ellipsis

    def link_to_object(self, obj, display_text=None):
        if not obj:
            return "-"
        display_text = display_text or str(obj)
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.pk],
        )
        return format_html('<a href="{}">{}</a>', url, display_text)

    def format_rating(self, rating, max_stars=5):
        filled = "⭐" * int(rating)
        empty = "☆" * (max_stars - int(rating))
        return format_html('<span style="color:#f1c40f;">{}{}</span>', filled, empty)

    def format_empty(self, placeholder="-"):
        return placeholder
