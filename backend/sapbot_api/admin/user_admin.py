# backend/sapbot_api/admin/user_admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
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
from ..models.user import (
   UserProfile,
   UserPreferences,
   UserSession,
   UserActivity,
   UserApiKey
)

User = get_user_model()


class UserTypeFilter(SimpleListFilter):
   """Kullanıcı tipi filtresi"""
   title = 'Kullanıcı Tipi'
   parameter_name = 'user_type'

   def lookups(self, request, model_admin):
       return UserProfile.USER_TYPE_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(sapbot_profile__user_type=self.value())
       return queryset


class BetaUserFilter(SimpleListFilter):
   """Beta kullanıcı filtresi"""
   title = 'Beta Kullanıcısı'
   parameter_name = 'is_beta'

   def lookups(self, request, model_admin):
       return (
           ('yes', 'Beta Kullanıcısı'),
           ('no', 'Normal Kullanıcı'),
       )

   def queryset(self, request, queryset):
       if self.value() == 'yes':
           return queryset.filter(sapbot_profile__is_beta_user=True)
       elif self.value() == 'no':
           return queryset.filter(sapbot_profile__is_beta_user=False)
       return queryset


class LastActivityFilter(SimpleListFilter):
   """Son aktivite filtresi"""
   title = 'Son Aktivite'
   parameter_name = 'last_activity'

   def lookups(self, request, model_admin):
       return (
           ('1d', 'Son 1 Gün'),
           ('7d', 'Son 7 Gün'),
           ('30d', 'Son 30 Gün'),
           ('inactive', '30 Günden Eski'),
       )

   def queryset(self, request, queryset):
       if self.value():
           now = timezone.now()
           if self.value() == '1d':
               time_threshold = now - timedelta(days=1)
               return queryset.filter(sapbot_profile__last_activity__gte=time_threshold)
           elif self.value() == '7d':
               time_threshold = now - timedelta(days=7)
               return queryset.filter(sapbot_profile__last_activity__gte=time_threshold)
           elif self.value() == '30d':
               time_threshold = now - timedelta(days=30)
               return queryset.filter(sapbot_profile__last_activity__gte=time_threshold)
           elif self.value() == 'inactive':
               time_threshold = now - timedelta(days=30)
               return queryset.filter(sapbot_profile__last_activity__lt=time_threshold)
       return queryset


class SAPBotUserAdmin(BaseUserAdmin):
   """Gelişmiş User Admin - SAPBot özelleştirmeli"""
   
   list_display = [
       'email',
       'full_name_display',
       'user_type_badge',
       'is_beta_icon',
       'last_activity_display',
       'is_active_icon',
       'date_joined'
   ]
   
   list_filter = [
       UserTypeFilter,
       BetaUserFilter,
       LastActivityFilter,
       'is_active',
       'is_staff',
       'date_joined'
   ]
   
   search_fields = [
       'email',
       'first_name',
       'last_name',
       'sapbot_profile__display_name'
   ]
   
   ordering = ['-date_joined']
   
   fieldsets = BaseUserAdmin.fieldsets + (
       ('SAPBot Bilgileri', {
           'fields': ('sapbot_profile_link',),
           'classes': ('collapse',)
       }),
   )
   
   readonly_fields = BaseUserAdmin.readonly_fields + ('sapbot_profile_link',)
   
   def full_name_display(self, obj):
       """Tam ad gösterimi"""
       if hasattr(obj, 'sapbot_profile') and obj.sapbot_profile.display_name:
           return obj.sapbot_profile.display_name
       elif obj.first_name or obj.last_name:
           return f"{obj.first_name} {obj.last_name}".strip()
       else:
           return obj.email.split('@')[0]
   full_name_display.short_description = 'Ad Soyad'
   
   def user_type_badge(self, obj):
       """Kullanıcı tipi rozeti"""
       try:
           profile = obj.sapbot_profile
           colors = {
               'user': '#6c757d',
               'technical': '#17a2b8',
               'admin': '#fd7e14',
               'super_admin': '#dc3545'
           }
           
           color = colors.get(profile.user_type, '#6c757d')
           return format_html(
               '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px;">{}</span>',
               color, profile.get_user_type_display()
           )
       except:
           return format_html(
               '<span style="color: #6c757d;">-</span>'
           )
   user_type_badge.short_description = 'Tip'
   
   def is_beta_icon(self, obj):
       """Beta kullanıcı ikonu"""
       try:
           if obj.sapbot_profile.is_beta_user:
               return format_html(
                   '<span style="color: #007bff; font-weight: bold;">β Beta</span>'
               )
           return format_html('<span style="color: #6c757d;">-</span>')
       except:
           return format_html('<span style="color: #6c757d;">-</span>')
   is_beta_icon.short_description = 'Beta'
   
   def last_activity_display(self, obj):
       """Son aktivite gösterimi"""
       try:
           if obj.sapbot_profile.last_activity:
               now = timezone.now()
               diff = now - obj.sapbot_profile.last_activity
               
               if diff.days == 0:
                   if diff.seconds < 3600:
                       return format_html('<span style="color: #28a745;">Az önce</span>')
                   else:
                       hours = diff.seconds // 3600
                       return format_html('<span style="color: #28a745;">{} saat önce</span>', hours)
               elif diff.days < 7:
                   return format_html('<span style="color: #ffc107;">{} gün önce</span>', diff.days)
               else:
                   return format_html('<span style="color: #dc3545;">{} gün önce</span>', diff.days)
           return format_html('<span style="color: #6c757d;">Hiç</span>')
       except:
           return format_html('<span style="color: #6c757d;">-</span>')
   last_activity_display.short_description = 'Son Aktivite'
   
   def is_active_icon(self, obj):
       """Aktif durumu ikonu"""
       if obj.is_active:
           return format_html(
               '<span style="color: #28a745;">✓ Aktif</span>'
           )
       return format_html(
           '<span style="color: #dc3545;">✗ Pasif</span>'
       )
   is_active_icon.short_description = 'Durum'
   
   def sapbot_profile_link(self, obj):
       """SAPBot profil linki"""
       try:
           profile = obj.sapbot_profile
           url = reverse('admin:sapbot_api_userprofile_change', args=[profile.pk])
           return format_html(
               '<a href="{}" target="_blank">📋 Profili Görüntüle</a>',
               url
           )
       except:
           return format_html('<span style="color: #6c757d;">Profil yok</span>')
   sapbot_profile_link.short_description = 'SAPBot Profili'
   
   def get_queryset(self, request):
       """Optimize edilmiş queryset"""
       return super().get_queryset(request).select_related('sapbot_profile')


# User admin'i değiştir
admin.site.unregister(User)
admin.site.register(User, SAPBotUserAdmin)


class SAPModuleFilter(SimpleListFilter):
   """SAP modül filtresi"""
   title = 'SAP Modülleri'
   parameter_name = 'sap_modules'

   def lookups(self, request, model_admin):
       return [
           ('FI', 'Mali Muhasebe'),
           ('MM', 'Malzeme Yönetimi'),
           ('SD', 'Satış ve Dağıtım'),
           ('CRM', 'Müşteri İlişkileri'),
           ('HR', 'İnsan Kaynakları'),
       ]

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(sap_modules__contains=[self.value()])
       return queryset


@admin.register(UserProfile)
class UserProfileAdmin(BaseModelAdmin):
   """Kullanıcı Profil Admin"""
   
   list_display = [
       'user_email',
       'display_name',
       'user_type_colored',
       'preferred_language',
       'sap_modules_display',
       'last_activity_time',
       'is_beta_user_icon'
   ]
   
   list_filter = [
       'user_type',
       'preferred_language',
       SAPModuleFilter,
       'is_beta_user',
       'email_notifications',
       'last_activity'
   ]
   
   search_fields = [
       'user__email',
       'display_name',
       'bio'
   ]
   
   raw_id_fields = ['user']
   
   readonly_fields = [
       'id',
       'created_at',
       'updated_at',
       'full_name',
       'last_login_display'
   ]
   
   fieldsets = (
       ('Kullanıcı Bilgileri', {
           'fields': (
               'user',
               'display_name',
               'full_name',
               'user_type',
               'bio'
           )
       }),
       ('Tercihler', {
           'fields': (
               'preferred_language',
               'sap_modules',
               'chat_settings'
           )
       }),
       ('Bildirimler', {
           'fields': (
               'email_notifications',
               'push_notifications'
           )
       }),
       ('Güvenlik ve Limitler', {
           'fields': (
               'session_timeout',
               'max_daily_requests',
               'is_beta_user'
           )
       }),
       ('Medya', {
           'fields': (
               'avatar',
           ),
           'classes': ('collapse',)
       }),
       ('Aktivite İzleme', {
           'fields': (
               'last_login_ip',
               'last_activity',
               'last_login_display'
           ),
           'classes': ('collapse',)
       }),
       ('Sistem', {
           'fields': (
               'created_at',
               'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   formfield_overrides = {
       models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
   }
   
   def user_email(self, obj):
       """Kullanıcı email"""
       return obj.user.email
   user_email.short_description = 'Email'
   user_email.admin_order_field = 'user__email'
   
   def user_type_colored(self, obj):
       """Renkli kullanıcı tipi"""
       colors = {
           'user': '#6c757d',
           'technical': '#17a2b8',
           'admin': '#fd7e14',
           'super_admin': '#dc3545'
       }
       
       color = colors.get(obj.user_type, '#6c757d')
       return format_html(
           '<span style="color: {}; font-weight: bold;">{}</span>',
           color, obj.get_user_type_display()
       )
   user_type_colored.short_description = 'Kullanıcı Tipi'
   
   def sap_modules_display(self, obj):
       """SAP modülleri gösterimi"""
       if not obj.sap_modules:
           return format_html('<span style="color: #6c757d;">-</span>')
       
       modules = obj.sap_modules[:3]  # İlk 3 modül
       more_count = len(obj.sap_modules) - 3
       
       display = ', '.join(modules)
       if more_count > 0:
           display += f' (+{more_count})'
       
       return format_html(
           '<span style="font-family: monospace; background: #f8f9fa; padding: 2px 4px; border-radius: 3px;">{}</span>',
           display
       )
   sap_modules_display.short_description = 'SAP Modülleri'
   
   def last_activity_time(self, obj):
       """Son aktivite zamanı"""
       if not obj.last_activity:
           return format_html('<span style="color: #6c757d;">Hiç</span>')
       
       now = timezone.now()
       diff = now - obj.last_activity
       
       if diff.days == 0:
           if diff.seconds < 3600:
               return format_html('<span style="color: #28a745;">Az önce</span>')
           else:
               hours = diff.seconds // 3600
               return format_html('<span style="color: #28a745;">{} saat önce</span>', hours)
       elif diff.days < 7:
           return format_html('<span style="color: #ffc107;">{} gün önce</span>', diff.days)
       else:
           return format_html('<span style="color: #dc3545;">{} gün önce</span>', diff.days)
   last_activity_time.short_description = 'Son Aktivite'
   
   def is_beta_user_icon(self, obj):
       """Beta kullanıcı ikonu"""
       if obj.is_beta_user:
           return format_html(
               '<span style="color: #007bff; font-weight: bold;">β Beta</span>'
           )
       return format_html('<span style="color: #6c757d;">-</span>')
   is_beta_user_icon.short_description = 'Beta'
   
   def last_login_display(self, obj):
       """Son giriş gösterimi"""
       if obj.user.last_login:
           return obj.user.last_login.strftime('%d.%m.%Y %H:%M')
       return "Hiç giriş yapmamış"
   last_login_display.short_description = 'Son Giriş'


class ThemeFilter(SimpleListFilter):
   """Tema filtresi"""
   title = 'Tema'
   parameter_name = 'theme'

   def lookups(self, request, model_admin):
       return UserPreferences.THEME_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(theme=self.value())
       return queryset


@admin.register(UserPreferences)
class UserPreferencesAdmin(BaseModelAdmin):
   """Kullanıcı Tercihleri Admin"""
   
   list_display = [
       'user_email',
       'theme_colored',
       'font_size',
       'features_summary',
       'updated_at'
   ]
   
   list_filter = [
       ThemeFilter,
       'font_size',
       'sound_enabled',
       'keyboard_shortcuts',
       'compact_mode'
   ]
   
   search_fields = [
       'user__email'
   ]
   
   raw_id_fields = ['user']
   
   readonly_fields = [
       'id',
       'created_at',
       'updated_at'
   ]
   
   fieldsets = (
       ('Görünüm', {
           'fields': (
               'user',
               'theme',
               'font_size',
               'compact_mode'
           )
       }),
       ('Etkileşim', {
           'fields': (
               'show_typing_indicator',
               'sound_enabled',
               'keyboard_shortcuts',
               'show_source_preview'
           )
       }),
       ('Veri Yönetimi', {
           'fields': (
               'auto_save_conversations',
               'dashboard_widgets'
           )
       }),
       ('Gelişmiş', {
           'fields': (
               'custom_css',
           ),
           'classes': ('collapse',)
       }),
       ('Sistem', {
           'fields': (
               'created_at',
               'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   def user_email(self, obj):
       """Kullanıcı email"""
       return obj.user.email
   user_email.short_description = 'Kullanıcı'
   user_email.admin_order_field = 'user__email'
   
   def theme_colored(self, obj):
       """Renkli tema gösterimi"""
       colors = {
           'light': '#ffc107',
           'dark': '#6c757d',
           'auto': '#17a2b8'
       }
       
       icons = {
           'light': '☀️',
           'dark': '🌙',
           'auto': '⚡'
       }
       
       color = colors.get(obj.theme, '#000000')
       icon = icons.get(obj.theme, '?')
       
       return format_html(
           '<span style="color: {};">{} {}</span>',
           color, icon, obj.get_theme_display()
       )
   theme_colored.short_description = 'Tema'
   
   def features_summary(self, obj):
       """Özellik özeti"""
       features = []
       if obj.sound_enabled:
           features.append("🔊")
       if obj.keyboard_shortcuts:
           features.append("⌨️")
       if obj.show_typing_indicator:
           features.append("✍️")
       if obj.auto_save_conversations:
           features.append("💾")
       
       if not features:
           return format_html('<span style="color: #6c757d;">Varsayılan</span>')
       
       return format_html(' '.join(features))
   features_summary.short_description = 'Özellikler'


class SessionStatusFilter(SimpleListFilter):
   """Oturum durumu filtresi"""
   title = 'Oturum Durumu'
   parameter_name = 'status'

   def lookups(self, request, model_admin):
       return (
           ('active', 'Aktif'),
           ('expired', 'Süresi Dolmuş'),
       )

   def queryset(self, request, queryset):
       if self.value() == 'active':
           return queryset.filter(
               is_active=True,
               expires_at__gt=timezone.now()
           )
       elif self.value() == 'expired':
           return queryset.filter(
               models.Q(is_active=False) | 
               models.Q(expires_at__lte=timezone.now())
           )
       return queryset


@admin.register(UserSession)
class UserSessionAdmin(ReadOnlyMixin, BaseModelAdmin):
   """Kullanıcı Oturum Admin - Sadece Okuma"""
   
   list_display = [
       'user_email',
       'session_preview',
       'location',
       'status_indicator',
       'device_info_summary',
       'last_activity',
       'expires_at'
   ]
   
   list_filter = [
       SessionStatusFilter,
       'is_active',
       'created_at',
       'expires_at'
   ]
   
   search_fields = [
       'user__email',
       'session_key',
       'ip_address',
       'location'
   ]
   
   date_hierarchy = 'created_at'
   
   ordering = ['-last_activity']
   
   readonly_fields = [
       'user',
       'session_key',
       'ip_address',
       'user_agent',
       'location',
       'device_info_formatted',
       'is_expired',
       'created_at',
       'last_activity',
       'expires_at'
   ]
   
   fieldsets = (
       ('Oturum Bilgileri', {
           'fields': (
               'user',
               'session_key',
               'is_active',
               'is_expired'
           )
       }),
       ('Konum ve Cihaz', {
           'fields': (
               'ip_address',
               'location',
               'user_agent',
               'device_info_formatted'
           )
       }),
       ('Zaman Bilgileri', {
           'fields': (
               'created_at',
               'last_activity',
               'expires_at'
           )
       })
   )
   
   def user_email(self, obj):
       """Kullanıcı email"""
       return obj.user.email
   user_email.short_description = 'Kullanıcı'
   user_email.admin_order_field = 'user__email'
   
   def session_preview(self, obj):
       """Oturum önizleme"""
       return format_html(
           '<code style="font-size: 11px;">{}</code>',
           obj.session_key[:16] + '...'
       )
   session_preview.short_description = 'Oturum'
   
   def status_indicator(self, obj):
       """Durum göstergesi"""
       if obj.is_expired:
           return format_html(
               '<span style="color: #dc3545;">⏰ Süresi Dolmuş</span>'
           )
       elif obj.is_active:
           return format_html(
               '<span style="color: #28a745;">✓ Aktif</span>'
           )
       else:
           return format_html(
               '<span style="color: #6c757d;">⏸ Pasif</span>'
           )
   status_indicator.short_description = 'Durum'
   
   def device_info_summary(self, obj):
       """Cihaz bilgisi özeti"""
       if not obj.device_info:
           return format_html('<span style="color: #6c757d;">-</span>')
       
       device_type = obj.device_info.get('type', 'Bilinmeyen')
       browser = obj.device_info.get('browser', 'Bilinmeyen')
       
       return format_html(
           '<span style="font-size: 11px;">{} / {}</span>',
           device_type, browser
       )
   device_info_summary.short_description = 'Cihaz'
   
   def device_info_formatted(self, obj):
       """Formatlanmış cihaz bilgisi"""
       if not obj.device_info:
           return "-"
       
       try:
           formatted = json.dumps(obj.device_info, indent=2, ensure_ascii=False)
           return format_html(
               '<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 12px;">{}</pre>',
               formatted
           )
       except Exception:
           return str(obj.device_info)
   device_info_formatted.short_description = 'Detaylı Cihaz Bilgisi'


class ActivityTypeFilter(SimpleListFilter):
   """Aktivite tipi filtresi"""
   title = 'Aktivite Tipi'
   parameter_name = 'activity_type'

   def lookups(self, request, model_admin):
       return UserActivity.ACTIVITY_TYPE_CHOICES

   def queryset(self, request, queryset):
       if self.value():
           return queryset.filter(activity_type=self.value())
       return queryset


@admin.register(UserActivity)
class UserActivityAdmin(ReadOnlyMixin, BaseModelAdmin):
   """Kullanıcı Aktivite Admin - Sadece Okuma"""
   
   list_display = [
       'user_email',
       'activity_type_colored',
       'description_preview',
       'ip_address',
       'created_at'
   ]
   
   list_filter = [
       ActivityTypeFilter,
       'created_at'
   ]
   
   search_fields = [
       'user__email',
       'description',
       'ip_address'
   ]
   
   date_hierarchy = 'created_at'
   
   ordering = ['-created_at']
   
   list_per_page = 100
   
   def user_email(self, obj):
       """Kullanıcı email"""
       return obj.user.email
   user_email.short_description = 'Kullanıcı'
   user_email.admin_order_field = 'user__email'
   
   def activity_type_colored(self, obj):
       """Renkli aktivite tipi"""
       colors = {
           'login': '#28a745',
           'logout': '#6c757d',
           'chat': '#007bff',
           'upload': '#17a2b8',
           'search': '#ffc107',
           'download': '#fd7e14',
           'settings': '#6f42c1',
           'api_call': '#20c997'
       }
       
       color = colors.get(obj.activity_type, '#000000')
       return format_html(
           '<span style="color: {}; font-weight: bold;">{}</span>',
           color, obj.get_activity_type_display()
       )
   activity_type_colored.short_description = 'Aktivite'
   
   def description_preview(self, obj):
       """Açıklama önizleme"""
       if not obj.description:
           return format_html('<span style="color: #6c757d;">-</span>')
       
       desc = obj.description
       if len(desc) > 60:
           return f"{desc[:57]}..."
       return desc
   description_preview.short_description = 'Açıklama'


@admin.register(UserApiKey)
class UserApiKeyAdmin(BaseModelAdmin):
   """Kullanıcı API Key Admin"""
   
   list_display = [
       'name',
       'user_email',
       'key_preview',
       'permissions_display',
       'rate_limit',
       'usage_info',
       'is_active_icon',
       'expires_at'
   ]
   
   list_filter = [
       'is_active',
       'created_at',
       'expires_at',
       'rate_limit'
   ]
   
   search_fields = [
       'name',
       'user__email',
       'key'
   ]
   
   raw_id_fields = ['user']
   
   readonly_fields = [
       'id',
       'key',
       'created_at',
       'updated_at',
       'last_used',
       'usage_count',
       'is_expired'
   ]
   
   fieldsets = (
       ('API Key Bilgileri', {
           'fields': (
               'user',
               'name',
               'key',
               'is_active'
           )
       }),
       ('İzinler ve Limitler', {
           'fields': (
               'permissions',
               'rate_limit'
           )
       }),
       ('Süre', {
           'fields': (
               'expires_at',
               'is_expired'
           )
       }),
       ('Kullanım İstatistikleri', {
           'fields': (
               'last_used',
               'usage_count'
           ),
           'classes': ('collapse',)
       }),
       ('Sistem', {
           'fields': (
               'created_at',
               'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   def user_email(self, obj):
       """Kullanıcı email"""
       return obj.user.email
   user_email.short_description = 'Kullanıcı'
   user_email.admin_order_field = 'user__email'
   
   def key_preview(self, obj):
       """Key önizleme"""
       return format_html(
           '<code style="font-size: 11px; background: #f8f9fa; padding: 2px 4px;">{}...</code>',
           obj.key[:20]
       )
   key_preview.short_description = 'API Key'
   
   def permissions_display(self, obj):
       """İzinler gösterimi"""
       if not obj.permissions:
           return format_html('<span style="color: #6c757d;">Hiçbiri</span>')
       
       perms = obj.permissions[:3]  # İlk 3 izin
       more_count = len(obj.permissions) - 3
       
       display = ', '.join(perms)
       if more_count > 0:
           display += f' (+{more_count})'
       
       return format_html(
           '<span style="font-family: monospace; font-size: 11px;">{}</span>',
           display
       )
   permissions_display.short_description = 'İzinler'
   
   def usage_info(self, obj):
       """Kullanım bilgisi"""
       if obj.usage_count == 0:
           return format_html('<span style="color: #6c757d;">Hiç kullanılmamış</span>')
       
       return format_html(
           '<div style="font-size: 11px;">'
           '<div><strong>{}</strong> kez kullanıldı</div>'
           '<div style="color: #6c757d;">{}</div>'
           '</div>',
           obj.usage_count,
           f"Son: {obj.last_used.strftime('%d.%m.%Y %H:%M')}" if obj.last_used else "Hiç"
       )
   usage_info.short_description = 'Kullanım'
   
   def is_active_icon(self, obj):
       """Aktif durumu ikonu"""
       if obj.is_expired:
           return format_html(
               '<span style="color: #dc3545;">⏰ Süresi Dolmuş</span>'
           )
       elif obj.is_active:
           return format_html(
               '<span style="color: #28a745;">✓ Aktif</span>'
           )
       else:
           return format_html(
               '<span style="color: #6c757d;">✗ Pasif</span>'
           )
   is_active_icon.short_description = 'Durum'
   
   def save_model(self, request, obj, form, change):
       """Model kaydetme - key otomatik oluştur"""
       if not change:  # Yeni kayıt
           obj.generate_key()
       super().save_model(request, obj, form, change)
   
   def get_readonly_fields(self, request, obj=None):
       """Readonly alanları dinamik belirle"""
       readonly = list(self.readonly_fields)
       
       if obj:  # Mevcut kayıt
           readonly.append('user')  # Kullanıcı değiştirilemez
       
       return readonly


# Inline admin'ler
class UserProfileInline(admin.StackedInline):
   """User Profile Inline"""
   model = UserProfile
   can_delete = False
   verbose_name = 'SAPBot Profili'
   verbose_name_plural = 'SAPBot Profili'
   
   fields = (
       'display_name',
       'user_type',
       'preferred_language',
       'sap_modules',
       'is_beta_user'
   )
   
   extra = 0


class UserPreferencesInline(admin.StackedInline):
   """User Preferences Inline"""
   model = UserPreferences
   can_delete = False
   verbose_name = 'Kullanıcı Tercihleri'
   verbose_name_plural = 'Kullanıcı Tercihleri'
   
   fields = (
       'theme',
       'font_size',
       'sound_enabled',
       'keyboard_shortcuts'
   )
   
   extra = 0


class UserApiKeyInline(admin.TabularInline):
   """User API Key Inline"""
   model = UserApiKey
   verbose_name = 'API Anahtarı'
   verbose_name_plural = 'API Anahtarları'
   
   fields = (
       'name',
       'key_preview',
       'is_active',
       'rate_limit',
       'expires_at'
   )
   
   readonly_fields = ('key_preview',)
   extra = 0
   
   def key_preview(self, obj):
       """Key önizleme"""
       if obj.key:
           return format_html(
               '<code style="font-size: 10px;">{}</code>',
               obj.key[:16] + '...'
           )
       return "-"
   key_preview.short_description = 'API Key'


# User admin'e inline'ları ekle
SAPBotUserAdmin.inlines = [
   UserProfileInline,
   UserPreferencesInline,
   UserApiKeyInline
]


# Custom actions
@admin.action(description='Seçili kullanıcıları beta programına ekle')
def add_to_beta_program(modeladmin, request, queryset):
   """Kullanıcıları beta programına ekle"""
   updated = 0
   for profile in queryset:
       if not profile.is_beta_user:
           profile.is_beta_user = True
           profile.save()
           updated += 1
   
   modeladmin.message_user(
       request,
       f'{updated} kullanıcı beta programına eklendi.',
       level='success'
   )


@admin.action(description='Seçili kullanıcıları beta programından çıkar')
def remove_from_beta_program(modeladmin, request, queryset):
   """Kullanıcıları beta programından çıkar"""
   updated = 0
   for profile in queryset:
       if profile.is_beta_user:
           profile.is_beta_user = False
           profile.save()
           updated += 1
   
   modeladmin.message_user(
       request,
       f'{updated} kullanıcı beta programından çıkarıldı.',
       level='success'
   )


@admin.action(description='Son aktiviteyi güncelle')
def update_last_activity(modeladmin, request, queryset):
   """Son aktiviteyi güncelle"""
   from django.utils import timezone
   
   updated = queryset.update(last_activity=timezone.now())
   
   modeladmin.message_user(
       request,
       f'{updated} kullanıcının son aktivite zamanı güncellendi.',
       level='success'
   )


@admin.action(description='Süresi dolmuş API keylerini pasif yap')
def deactivate_expired_keys(modeladmin, request, queryset):
   """Süresi dolmuş API keylerini pasif yap"""
   from django.utils import timezone
   
   expired_keys = queryset.filter(
       expires_at__lt=timezone.now(),
       is_active=True
   )
   
   updated = expired_keys.update(is_active=False)
   
   modeladmin.message_user(
       request,
       f'{updated} süresi dolmuş API key pasif yapıldı.',
       level='success'
   )


@admin.action(description='Seçili oturumları sonlandır')
def terminate_sessions(modeladmin, request, queryset):
   """Seçili oturumları sonlandır"""
   updated = queryset.update(is_active=False)
   
   modeladmin.message_user(
       request,
       f'{updated} oturum sonlandırıldı.',
       level='warning'
   )


# Action'ları admin'lere ekle
UserProfileAdmin.actions = [
   add_to_beta_program,
   remove_from_beta_program,
   update_last_activity
]

UserApiKeyAdmin.actions = [
   deactivate_expired_keys
]

UserSessionAdmin.actions = [
   terminate_sessions
]


# Dashboard widget için custom view
class UserStatsWidget:
   """Kullanıcı istatistikleri widget"""
   
   @staticmethod
   def get_stats():
       """Kullanıcı istatistiklerini al"""
       from django.db.models import Count, Q
       from django.utils import timezone
       from datetime import timedelta
       
       now = timezone.now()
       week_ago = now - timedelta(days=7)
       month_ago = now - timedelta(days=30)
       
       stats = {
           'total_users': User.objects.count(),
           'active_users': User.objects.filter(is_active=True).count(),
           'beta_users': UserProfile.objects.filter(is_beta_user=True).count(),
           'recent_activity': UserProfile.objects.filter(
               last_activity__gte=week_ago
           ).count(),
           'user_types': UserProfile.objects.values('user_type').annotate(
               count=Count('user_type')
           ),
           'api_keys_active': UserApiKey.objects.filter(
               is_active=True,
               expires_at__gt=now
           ).count(),
           'sessions_active': UserSession.objects.filter(
               is_active=True,
               expires_at__gt=now
           ).count()
       }
       
       return stats


# Admin site customization
admin.site.site_header = "SAPBot API Kullanıcı Yönetimi"
admin.site.site_title = "SAPBot Kullanıcı Admin"
admin.site.index_title = "Kullanıcı Yönetim Paneli"

# Custom admin index template için context processor
def admin_context_processor(request):
   """Admin context processor"""
   if request.path.startswith('/admin/'):
       return {
           'user_stats': UserStatsWidget.get_stats()
       }
   return {}



