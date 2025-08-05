# backend/sapbot_api/admin/chat_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .base_admin import BaseModelAdmin
from ..models import (
   ChatConversation, 
   ChatMessage, 
   MessageFeedback,
   ConversationSummary
)

@admin.register(ChatConversation)
class ChatConversationAdmin(BaseModelAdmin):
   """Chat konuşması admin"""
   
   list_display = [
       'session_short_id', 'user_email', 'user_type', 'message_count_display',
       'duration_display', 'last_activity', 'is_archived', 'created_at'
   ]
   
   list_filter = [
       'user_type', 'is_archived', 'created_at', 'last_activity',
       ('user', admin.RelatedFieldListFilter)
   ]
   
   search_fields = [
       'session_id', 'user__email', 'user__first_name', 'user__last_name'
   ]
   
   readonly_fields = [
       'id', 'session_id', 'created_at', 'updated_at', 'last_activity',
       'message_count_display', 'duration_display', 'conversation_preview'
   ]
   
   fieldsets = (
       ('Temel Bilgiler', {
           'fields': (
               'id', 'session_id', 'user', 'user_type'
           )
       }),
       ('Teknik Bilgiler', {
           'fields': (
               'user_agent', 'ip_address', 'metadata'
           ),
           'classes': ('collapse',)
       }),
       ('İstatistikler', {
           'fields': (
               'message_count_display', 'duration_display', 
               'conversation_preview'
           )
       }),
       ('Durum', {
           'fields': (
               'is_active', 'is_archived', 'created_at', 
               'updated_at', 'last_activity'
           )
       })
   )
   
   actions = ['archive_conversations', 'unarchive_conversations']
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'user'
       ).annotate(
           msg_count=Count('messages')
       )
   
   def session_short_id(self, obj):
       """Kısa session ID"""
       return f"{obj.session_id[:12]}..."
   session_short_id.short_description = "Session ID"
   
   def user_email(self, obj):
       """Kullanıcı email"""
       if obj.user:
           url = reverse('admin:auth_user_change', args=[obj.user.pk])
           return format_html(
               '<a href="{}">{}</a>', 
               url, obj.user.email
           )
       return "Anonim"
   user_email.short_description = "Kullanıcı"
   
   def message_count_display(self, obj):
       """Mesaj sayısı"""
       count = getattr(obj, 'msg_count', obj.message_count)
       if count > 50:
           return format_html(
               '<span style="color: #e74c3c; font-weight: bold;">{}</span>',
               count
           )
       elif count > 20:
           return format_html(
               '<span style="color: #f39c12; font-weight: bold;">{}</span>',
               count
           )
       return str(count)
   message_count_display.short_description = "Mesaj Sayısı"
   
   def duration_display(self, obj):
       """Konuşma süresi"""
       duration = obj.duration_minutes
       if duration > 60:
           hours = int(duration // 60)
           minutes = int(duration % 60)
           return f"{hours}s {minutes}dk"
       elif duration > 0:
           return f"{int(duration)}dk"
       return "< 1dk"
   duration_display.short_description = "Süre"
   
   def conversation_preview(self, obj):
       """Konuşma önizlemesi"""
       if not obj.pk:
           return "-"
       
       messages = obj.messages.order_by('created_at')[:3]
       preview_html = []
       
       for msg in messages:
           content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
           icon = "👤" if msg.message_type == "user" else "🤖"
           preview_html.append(f"{icon} {content}")
       
       if messages.count() > 3:
           preview_html.append("...")
       
       return format_html("<br>".join(preview_html))
   conversation_preview.short_description = "Konuşma Önizlemesi"
   
   def archive_conversations(self, request, queryset):
       """Konuşmaları arşivle"""
       updated = queryset.update(is_archived=True)
       self.message_user(
           request, 
           f"{updated} konuşma arşivlendi."
       )
   archive_conversations.short_description = "Seçili konuşmaları arşivle"
   
   def unarchive_conversations(self, request, queryset):
       """Konuşmaları arşivden çıkar"""
       updated = queryset.update(is_archived=False)
       self.message_user(
           request, 
           f"{updated} konuşma arşivden çıkarıldı."
       )
   unarchive_conversations.short_description = "Seçili konuşmaları arşivden çıkar"


class MessageSourcesInline(admin.TabularInline):
   """Mesaj kaynakları inline"""
   model = ChatMessage.sources_used.through
   extra = 0
   readonly_fields = ['knowledgechunk']
   verbose_name = "Kullanılan Kaynak"
   verbose_name_plural = "Kullanılan Kaynaklar"


@admin.register(ChatMessage)
class ChatMessageAdmin(BaseModelAdmin):
   """Chat mesajı admin"""
   
   list_display = [
       'conversation_link', 'message_type', 'content_preview',
       'intent_detected', 'confidence_score', 'response_time',
       'source_count_display', 'created_at'
   ]
   
   list_filter = [
       'message_type', 'intent_detected', 'created_at',
       ('conversation__user', admin.RelatedFieldListFilter),
       'conversation__user_type'
   ]
   
   search_fields = [
       'content', 'conversation__session_id', 
       'conversation__user__email', 'intent_detected'
   ]
   
   readonly_fields = [
       'id', 'content_hash', 'created_at', 'updated_at',
       'source_count_display', 'conversation_info'
   ]
   
   fieldsets = (
       ('Mesaj Bilgileri', {
           'fields': (
               'conversation', 'message_type', 'content'
           )
       }),
       ('AI Analizi', {
           'fields': (
               'intent_detected', 'confidence_score', 'model_used'
           )
       }),
       ('Performans', {
           'fields': (
               'response_time', 'token_count', 'source_count_display'
           )
       }),
       ('Teknik', {
           'fields': (
               'id', 'content_hash', 'metadata', 'created_at', 'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   inlines = [MessageSourcesInline]
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'conversation',
           'conversation__user'
       ).prefetch_related('sources_used')
   
   def conversation_link(self, obj):
       """Konuşma linki"""
       url = reverse('admin:sapbot_api_chatconversation_change', 
                    args=[obj.conversation.pk])
       return format_html(
           '<a href="{}">{}</a>',
           url, f"{obj.conversation.session_id[:12]}..."
       )
   conversation_link.short_description = "Konuşma"
   
   def content_preview(self, obj):
       """İçerik önizlemesi"""
       content = obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
       
       if obj.message_type == 'user':
           return format_html(
               '<span style="color: #3498db;">👤 {}</span>',
               content
           )
       elif obj.message_type == 'assistant':
           return format_html(
               '<span style="color: #27ae60;">🤖 {}</span>',
               content
           )
       elif obj.message_type == 'error':
           return format_html(
               '<span style="color: #e74c3c;">❌ {}</span>',
               content
           )
       return content
   content_preview.short_description = "İçerik"
   
   def source_count_display(self, obj):
       """Kaynak sayısı"""
       count = obj.source_count
       if count > 5:
           return format_html(
               '<span style="color: #e74c3c; font-weight: bold;">{}</span>',
               count
           )
       elif count > 0:
           return format_html(
               '<span style="color: #27ae60;">{}</span>',
               count
           )
       return "0"
   source_count_display.short_description = "Kaynak"
   
   def conversation_info(self, obj):
       """Konuşma bilgisi"""
       conv = obj.conversation
       return format_html(
           "Session: {}<br>Kullanıcı: {}<br>Tip: {}",
           conv.session_id,
           conv.user.email if conv.user else "Anonim",
           conv.get_user_type_display()
       )
   conversation_info.short_description = "Konuşma Bilgisi"


@admin.register(MessageFeedback)
class MessageFeedbackAdmin(BaseModelAdmin):
   """Mesaj geri bildirim admin"""
   
   list_display = [
       'message_link', 'rating_display', 'is_helpful',
       'has_comment', 'created_at'
   ]
   
   list_filter = [
       'rating', 'is_helpful', 'created_at',
       ('message__conversation__user', admin.RelatedFieldListFilter)
   ]
   
   search_fields = [
       'comment', 'message__content', 
       'message__conversation__session_id'
   ]
   
   readonly_fields = [
       'id', 'created_at', 'updated_at', 'message_info'
   ]
   
   fieldsets = (
       ('Geri Bildirim', {
           'fields': (
               'message', 'rating', 'is_helpful', 'comment'
           )
       }),
       ('Sistem', {
           'fields': (
               'user_ip', 'id', 'created_at', 'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'message',
           'message__conversation',
           'message__conversation__user'
       )
   
   def message_link(self, obj):
       """Mesaj linki"""
       url = reverse('admin:sapbot_api_chatmessage_change', 
                    args=[obj.message.pk])
       return format_html(
           '<a href="{}">{}</a>',
           url, f"Mesaj #{obj.message.pk}"
       )
   message_link.short_description = "Mesaj"
   
   def rating_display(self, obj):
       """Rating görüntüleme"""
       stars = "⭐" * obj.rating
       
       if obj.rating >= 4:
           color = "#27ae60"
       elif obj.rating >= 3:
           color = "#f39c12"
       else:
           color = "#e74c3c"
       
       return format_html(
           '<span style="color: {};">{} ({})</span>',
           color, stars, obj.rating
       )
   rating_display.short_description = "Puan"
   
   def has_comment(self, obj):
       """Yorum var mı?"""
       if obj.comment:
           return format_html(
               '<span style="color: #27ae60;">✓</span>'
           )
       return format_html(
           '<span style="color: #e74c3c;">✗</span>'
       )
   has_comment.short_description = "Yorum"
   has_comment.boolean = True
   
   def message_info(self, obj):
       """Mesaj bilgisi"""
       msg = obj.message
       content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
       return format_html(
           "Tip: {}<br>İçerik: {}<br>Session: {}",
           msg.get_message_type_display(),
           content,
           msg.conversation.session_id[:12] + "..."
       )
   message_info.short_description = "Mesaj Bilgisi"


@admin.register(ConversationSummary)
class ConversationSummaryAdmin(BaseModelAdmin):
   """Konuşma özeti admin"""
   
   list_display = [
       'conversation_link', 'title', 'resolution_status',
       'auto_generated', 'sap_modules_display', 'created_at'
   ]
   
   list_filter = [
       'resolution_status', 'auto_generated', 'created_at',
       ('conversation__user', admin.RelatedFieldListFilter)
   ]
   
   search_fields = [
       'title', 'summary', 'conversation__session_id',
       'main_topics', 'sap_modules_discussed'
   ]
   
   readonly_fields = [
       'id', 'created_at', 'updated_at', 'conversation_info'
   ]
   
   fieldsets = (
       ('Özet Bilgileri', {
           'fields': (
               'conversation', 'title', 'summary'
           )
       }),
       ('Analiz', {
           'fields': (
               'main_topics', 'sap_modules_discussed', 'resolution_status'
           )
       }),
       ('Sistem', {
           'fields': (
               'auto_generated', 'id', 'created_at', 'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'conversation',
           'conversation__user'
       )
   
   def conversation_link(self, obj):
       """Konuşma linki"""
       url = reverse('admin:sapbot_api_chatconversation_change', 
                    args=[obj.conversation.pk])
       return format_html(
           '<a href="{}">{}</a>',
           url, f"{obj.conversation.session_id[:12]}..."
       )
   conversation_link.short_description = "Konuşma"
   
   def sap_modules_display(self, obj):
       """SAP modülleri görüntüleme"""
       if obj.sap_modules_discussed:
           modules = obj.sap_modules_discussed[:3]  # İlk 3 modül
           display = ", ".join(modules)
           if len(obj.sap_modules_discussed) > 3:
               display += f" (+{len(obj.sap_modules_discussed) - 3})"
           return display
       return "-"
   sap_modules_display.short_description = "SAP Modülleri"
   
   def conversation_info(self, obj):
       """Konuşma bilgisi"""
       conv = obj.conversation
       return format_html(
           "Kullanıcı: {}<br>Mesaj Sayısı: {}<br>Süre: {} dk",
           conv.user.email if conv.user else "Anonim",
           conv.message_count,
           int(conv.duration_minutes)
       )
   conversation_info.short_description = "Konuşma Bilgisi"


# Admin site customization
admin.site.register_view('sapbot_api/chat_analytics/', 
                       view=lambda request: None, 
                       name='Chat Analytics')
