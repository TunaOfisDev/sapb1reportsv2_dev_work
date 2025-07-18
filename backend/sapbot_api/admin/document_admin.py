# backend/sapbot_api/admin/document_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.http import HttpResponse
import json

from .base_admin import BaseModelAdmin, ReadOnlyTabularInline
from ..models import (
   DocumentSource, 
   KnowledgeChunk, 
   DocumentTag,
   DocumentChunkRelation
)


class KnowledgeChunkInline(ReadOnlyTabularInline):
   """Knowledge chunk inline"""
   model = KnowledgeChunk
   fields = [
       'content_preview', 'sap_module', 'technical_level', 
       'usage_count', 'relevance_score', 'is_verified'
   ]
   readonly_fields = ['content_preview']
   extra = 0
   max_num = 10
   
   def content_preview(self, obj):
       """İçerik önizlemesi"""
       if obj.content:
           preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
           return preview
       return "-"
   content_preview.short_description = "İçerik Önizleme"


@admin.register(DocumentSource)
class DocumentSourceAdmin(BaseModelAdmin):
   """Döküman kaynağı admin"""
   
   list_display = [
       'title_link', 'document_type', 'language', 'processing_status_display',
       'file_size_display', 'chunk_count_display', 'priority_display',
       'uploaded_by', 'processed_at', 'is_active'
   ]
   
   list_filter = [
       'document_type', 'language', 'processing_status', 'priority',
       'is_public', 'is_active', 'created_at', 'processed_at',
       ('uploaded_by', admin.RelatedFieldListFilter)
   ]
   
   search_fields = [
       'title', 'description', 'file_path', 'source_url',
       'uploaded_by__email', 'tags'
   ]
   
   readonly_fields = [
       'id', 'file_hash', 'file_size_mb', 'chunk_count_display',
       'processing_progress', 'created_at', 'updated_at', 'processed_at',
       'file_info_display', 'processing_stats'
   ]
   
   fieldsets = (
       ('Temel Bilgiler', {
           'fields': (
               'title', 'description', 'document_type', 'language'
           )
       }),
       ('Dosya Bilgileri', {
           'fields': (
               'file_path', 'source_url', 'version', 'file_hash',
               'file_size_mb', 'file_info_display'
           )
       }),
       ('İşleme Durumu', {
           'fields': (
               'processing_status', 'processing_progress', 'processed_at',
               'processing_error', 'processing_stats'
           )
       }),
       ('Kategorizasyon', {
           'fields': (
               'tags', 'priority', 'is_public', 'uploaded_by'
           )
       }),
       ('Chunk Analizi', {
           'fields': (
               'chunk_count_display',
           )
       }),
       ('Sistem', {
           'fields': (
               'id', 'is_active', 'created_at', 'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   actions = [
       'reprocess_documents', 'activate_documents', 'deactivate_documents',
       'mark_high_priority', 'export_document_stats'
   ]
   
   inlines = [KnowledgeChunkInline]
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'uploaded_by'
       ).annotate(
           chunks_count=Count('chunks'),
           avg_chunk_usage=Avg('chunks__usage_count'),
           total_usage=Sum('chunks__usage_count')
       )
   
   def title_link(self, obj):
       """Başlık linki"""
       return format_html(
           '<a href="{}" style="font-weight: bold;">{}</a>',
           reverse('admin:sapbot_api_documentsource_change', args=[obj.pk]),
           obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
       )
   title_link.short_description = "Başlık"
   
   def processing_status_display(self, obj):
       """İşleme durumu görüntüleme"""
       status_colors = {
           'pending': '#f39c12',
           'processing': '#3498db',
           'completed': '#27ae60',
           'failed': '#e74c3c',
           'cancelled': '#95a5a6'
       }
       
       color = status_colors.get(obj.processing_status, '#333')
       icon_map = {
           'pending': '⏳',
           'processing': '⚙️',
           'completed': '✅',
           'failed': '❌',
           'cancelled': '⏹️'
       }
       
       icon = icon_map.get(obj.processing_status, '❓')
       
       return format_html(
           '<span style="color: {}; font-weight: bold;">{} {}</span>',
           color, icon, obj.get_processing_status_display()
       )
   processing_status_display.short_description = "Durum"
   
   def file_size_display(self, obj):
       """Dosya boyutu görüntüleme"""
       if not obj.file_size:
           return "-"
       
       size_mb = obj.file_size_mb
       if size_mb > 100:
           return format_html(
               '<span style="color: #e74c3c; font-weight: bold;">{:.1f} MB</span>',
               size_mb
           )
       elif size_mb > 50:
           return format_html(
               '<span style="color: #f39c12;">{:.1f} MB</span>',
               size_mb
           )
       return f"{size_mb:.1f} MB"
   file_size_display.short_description = "Boyut"
   
   def chunk_count_display(self, obj):
       """Chunk sayısı görüntüleme"""
       count = getattr(obj, 'chunks_count', obj.chunk_count)
       avg_usage = getattr(obj, 'avg_chunk_usage', 0) or 0
       
       if count == 0:
           return format_html('<span style="color: #e74c3c;">0</span>')
       
       usage_indicator = ""
       if avg_usage > 10:
           usage_indicator = " 🔥"
       elif avg_usage > 5:
           usage_indicator = " ⭐"
       
       return format_html(
           '<span style="color: #27ae60; font-weight: bold;">{}{}</span>',
           count, usage_indicator
       )
   chunk_count_display.short_description = "Chunks"
   
   def priority_display(self, obj):
       """Öncelik görüntüleme"""
       priority_icons = {
           1: '🔵',  # Düşük
           2: '🟢',  # Normal
           3: '🟡',  # Yüksek
           4: '🔴'   # Kritik
       }
       
       icon = priority_icons.get(obj.priority, '⚪')
       return format_html(
           '{} {}',
           icon, obj.get_priority_display()
       )
   priority_display.short_description = "Öncelik"
   
   def file_info_display(self, obj):
       """Dosya bilgi görüntüleme"""
       if not obj.file_path:
           return "Dosya yok"
       
       extension = obj.get_file_extension()
       return format_html(
           "Uzantı: {}<br>Hash: {}<br>Boyut: {:.1f} MB",
           extension or "Bilinmiyor",
           obj.file_hash[:16] + "..." if obj.file_hash else "Yok",
           obj.file_size_mb
       )
   file_info_display.short_description = "Dosya Bilgileri"
   
   def processing_stats(self, obj):
       """İşleme istatistikleri"""
       if obj.processing_status == 'completed':
           chunks = obj.chunks.all()
           if chunks:
               total_usage = sum(chunk.usage_count for chunk in chunks)
               avg_relevance = sum(chunk.relevance_score for chunk in chunks) / len(chunks)
               verified_count = sum(1 for chunk in chunks if chunk.is_verified)
               
               return format_html(
                   "Toplam Kullanım: {}<br>Ort. Relevans: {:.2f}<br>Doğrulanmış: {}/{}",
                   total_usage,
                   avg_relevance,
                   verified_count,
                   len(chunks)
               )
       return "Henüz işlenmedi"
   processing_stats.short_description = "İşleme İstatistikleri"
   
   def reprocess_documents(self, request, queryset):
       """Dökümanları yeniden işle"""
       count = 0
       for doc in queryset:
           if doc.processing_status in ['completed', 'failed']:
               doc.processing_status = 'pending'
               doc.save()
               count += 1
               
               # Celery task tetikle (örnek)
               # process_document.delay(doc.id)
       
       self.message_user(
           request,
           f"{count} döküman yeniden işleme kuyruğuna alındı."
       )
   reprocess_documents.short_description = "Seçili dökümanları yeniden işle"
   
   def activate_documents(self, request, queryset):
       """Dökümanları aktif yap"""
       updated = queryset.update(is_active=True)
       self.message_user(request, f"{updated} döküman aktif edildi.")
   activate_documents.short_description = "Seçili dökümanları aktif et"
   
   def deactivate_documents(self, request, queryset):
       """Dökümanları pasif yap"""
       updated = queryset.update(is_active=False)
       self.message_user(request, f"{updated} döküman pasif edildi.")
   deactivate_documents.short_description = "Seçili dökümanları pasif et"
   
   def mark_high_priority(self, request, queryset):
       """Yüksek öncelik işaretle"""
       updated = queryset.update(priority=3)
       self.message_user(request, f"{updated} döküman yüksek öncelik olarak işaretlendi.")
   mark_high_priority.short_description = "Yüksek öncelik olarak işaretle"
   
   def export_document_stats(self, request, queryset):
       """Döküman istatistiklerini dışa aktar"""
       response = HttpResponse(content_type='application/json')
       response['Content-Disposition'] = 'attachment; filename="document_stats.json"'
       
       stats = []
       for doc in queryset:
           stats.append({
               'title': doc.title,
               'type': doc.document_type,
               'language': doc.language,
               'status': doc.processing_status,
               'chunk_count': doc.chunk_count,
               'file_size_mb': doc.file_size_mb,
               'created_at': doc.created_at.isoformat() if doc.created_at else None
           })
       
       json.dump(stats, response, indent=2, ensure_ascii=False)
       return response
   export_document_stats.short_description = "İstatistikleri JSON olarak dışa aktar"


class ChunkRelationsInline(admin.TabularInline):
   """Chunk ilişkileri inline"""
   model = DocumentChunkRelation
   fk_name = 'source_chunk'
   fields = ['target_chunk', 'relation_type', 'confidence', 'auto_generated']
   extra = 0
   max_num = 5


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(BaseModelAdmin):
   """Bilgi parçası admin"""
   
   list_display = [
       'content_preview', 'source_link', 'sap_module', 'technical_level',
       'usage_count_display', 'relevance_score_display', 'quality_score_display',
       'is_verified', 'last_used'
   ]
   
   list_filter = [
       'sap_module', 'technical_level', 'is_verified',
       'source__document_type', 'source__language',
       ('verified_by', admin.RelatedFieldListFilter),
       'last_used', 'created_at'
   ]
   
   search_fields = [
       'content', 'keywords', 'section_title',
       'source__title', 'content_hash'
   ]
   
   readonly_fields = [
       'id', 'content_hash', 'content_length', 'embedding_model',
       'created_at', 'updated_at', 'source_info', 'usage_stats'
   ]
   
   fieldsets = (
       ('İçerik', {
           'fields': (
               'source', 'content', 'section_title', 'page_number'
           )
       }),
       ('Kategorizasyon', {
           'fields': (
               'sap_module', 'technical_level', 'keywords'
           )
       }),
       ('Kalite ve Doğrulama', {
           'fields': (
               'relevance_score', 'quality_score', 'is_verified', 'verified_by'
           )
       }),
       ('Kullanım İstatistikleri', {
           'fields': (
               'usage_count', 'last_used', 'usage_stats'
           )
       }),
       ('Teknik', {
           'fields': (
               'id', 'content_hash', 'content_length', 'embedding_model',
               'created_at', 'updated_at'
           ),
           'classes': ('collapse',)
       })
   )
   
   actions = [
       'verify_chunks', 'unverify_chunks', 'reset_usage_stats',
       'mark_high_quality', 'regenerate_embeddings'
   ]
   
   inlines = [ChunkRelationsInline]
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'source', 'verified_by'
       )
   
   def content_preview(self, obj):
       """İçerik önizlemesi"""
       content = obj.content[:120] + "..." if len(obj.content) > 120 else obj.content
       
       # SAP modülüne göre renk kodlama
       color_map = {
           'FI': '#3498db',
           'MM': '#27ae60',
           'SD': '#e74c3c',
           'CRM': '#9b59b6',
           'PROD': '#f39c12',
           'HR': '#1abc9c'
       }
       
       color = color_map.get(obj.sap_module, '#333')
       
       return format_html(
           '<div style="color: {}; max-width: 300px;">{}</div>',
           color, content
       )
   content_preview.short_description = "İçerik"
   
   def source_link(self, obj):
       """Kaynak linki"""
       url = reverse('admin:sapbot_api_documentsource_change', 
                    args=[obj.source.pk])
       return format_html(
           '<a href="{}">{}</a>',
           url, obj.source.title[:30] + "..." if len(obj.source.title) > 30 else obj.source.title
       )
   source_link.short_description = "Kaynak"
   
   def usage_count_display(self, obj):
       """Kullanım sayısı görüntüleme"""
       count = obj.usage_count
       
       if count > 50:
           return format_html(
               '<span style="color: #e74c3c; font-weight: bold;">🔥 {}</span>',
               count
           )
       elif count > 20:
           return format_html(
               '<span style="color: #f39c12; font-weight: bold;">⭐ {}</span>',
               count
           )
       elif count > 5:
           return format_html(
               '<span style="color: #27ae60;">{}</span>',
               count
           )
       return str(count)
   usage_count_display.short_description = "Kullanım"
   
   def relevance_score_display(self, obj):
       """Relevans skoru görüntüleme"""
       score = obj.relevance_score
       
       if score >= 0.8:
           color = "#27ae60"
           icon = "🟢"
       elif score >= 0.6:
           color = "#f39c12"
           icon = "🟡"
       else:
           color = "#e74c3c"
           icon = "🔴"
       
       return format_html(
           '<span style="color: {};">{} {:.2f}</span>',
           color, icon, score
       )
   relevance_score_display.short_description = "Relevans"
   
   def quality_score_display(self, obj):
       """Kalite skoru görüntüleme"""
       if obj.quality_score is None:
           return "-"
       
       score = obj.quality_score
       stars = "⭐" * int(score * 5)
       
       return format_html(
           '<span title="Kalite: {:.2f}">{}</span>',
           score, stars
       )
   quality_score_display.short_description = "Kalite"
   
   def source_info(self, obj):
       """Kaynak bilgisi"""
       source = obj.source
       return format_html(
           "Döküman: {}<br>Tip: {}<br>Sayfa: {}",
           source.title,
           source.get_document_type_display(),
           obj.page_number or "Belirsiz"
       )
   source_info.short_description = "Kaynak Bilgisi"
   
   def usage_stats(self, obj):
       """Kullanım istatistikleri"""
       if obj.last_used:
           days_since = (timezone.now() - obj.last_used).days
           return format_html(
               "Son kullanım: {} gün önce<br>Toplam: {} kez",
               days_since,
               obj.usage_count
           )
       return "Hiç kullanılmamış"
   usage_stats.short_description = "Kullanım İstatistikleri"
   
   def verify_chunks(self, request, queryset):
       """Chunk'ları doğrula"""
       updated = queryset.update(is_verified=True, verified_by=request.user)
       self.message_user(request, f"{updated} chunk doğrulandı.")
   verify_chunks.short_description = "Seçili chunk'ları doğrula"
   
   def unverify_chunks(self, request, queryset):
       """Chunk doğrulamalarını kaldır"""
       updated = queryset.update(is_verified=False, verified_by=None)
       self.message_user(request, f"{updated} chunk doğrulaması kaldırıldı.")
   unverify_chunks.short_description = "Doğrulamaları kaldır"
   
   def reset_usage_stats(self, request, queryset):
       """Kullanım istatistiklerini sıfırla"""
       updated = queryset.update(usage_count=0, last_used=None)
       self.message_user(request, f"{updated} chunk kullanım istatistiği sıfırlandı.")
   reset_usage_stats.short_description = "Kullanım istatistiklerini sıfırla"
   
   def mark_high_quality(self, request, queryset):
       """Yüksek kalite işaretle"""
       updated = queryset.update(quality_score=0.9)
       self.message_user(request, f"{updated} chunk yüksek kalite olarak işaretlendi.")
   mark_high_quality.short_description = "Yüksek kalite olarak işaretle"
   
   def regenerate_embeddings(self, request, queryset):
       """Embedding'leri yeniden oluştur"""
       count = queryset.count()
       # Burada Celery task tetiklenebilir
       # for chunk in queryset:
       #     regenerate_chunk_embedding.delay(chunk.id)
       
       self.message_user(
           request,
           f"{count} chunk embedding yenileme kuyruğuna alındı."
       )
   regenerate_embeddings.short_description = "Embedding'leri yeniden oluştur"


@admin.register(DocumentTag)
class DocumentTagAdmin(BaseModelAdmin):
   """Döküman etiketi admin"""
   
   list_display = [
       'name', 'tag_type', 'color_display', 'usage_count_display', 'created_at'
   ]
   
   list_filter = ['tag_type', 'created_at']
   search_fields = ['name', 'description', 'slug']
   
   readonly_fields = ['id', 'slug', 'usage_count', 'created_at', 'updated_at']
   
   fieldsets = (
       ('Etiket Bilgileri', {
           'fields': ('name', 'slug', 'description', 'tag_type')
       }),
       ('Görünüm', {
           'fields': ('color',)
       }),
       ('İstatistikler', {
           'fields': ('usage_count', 'created_at', 'updated_at')
       })
   )
   
   def color_display(self, obj):
       """Renk görüntüleme"""
       return format_html(
           '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div> {}',
           obj.color, obj.color
       )
   color_display.short_description = "Renk"
   
   def usage_count_display(self, obj):
       """Kullanım sayısı görüntüleme"""
       count = obj.usage_count
       
       if count > 20:
           return format_html(
               '<span style="color: #27ae60; font-weight: bold;">{}</span>',
               count
           )
       elif count > 5:
           return format_html(
               '<span style="color: #f39c12;">{}</span>',
               count
           )
       return str(count)
   usage_count_display.short_description = "Kullanım"


@admin.register(DocumentChunkRelation)
class DocumentChunkRelationAdmin(BaseModelAdmin):
   """Döküman chunk ilişkisi admin"""
   
   list_display = [
       'source_chunk_preview', 'relation_type_display', 'target_chunk_preview',
       'confidence_display', 'auto_generated', 'created_at'
   ]
   
   list_filter = [
       'relation_type', 'auto_generated', 'created_at'
   ]
   
   search_fields = [
       'source_chunk__content', 'target_chunk__content'
   ]
   
   readonly_fields = ['id', 'created_at', 'updated_at']
   
   def get_queryset(self, request):
       return super().get_queryset(request).select_related(
           'source_chunk', 'target_chunk',
           'source_chunk__source', 'target_chunk__source'
       )
   
   def source_chunk_preview(self, obj):
       """Kaynak chunk önizlemesi"""
       content = obj.source_chunk.content[:50] + "..."
       return format_html(
           '<span style="color: #3498db;">{}</span>',
           content
       )
   source_chunk_preview.short_description = "Kaynak Chunk"
   
   def target_chunk_preview(self, obj):
       """Hedef chunk önizlemesi"""
       content = obj.target_chunk.content[:50] + "..."
       return format_html(
           '<span style="color: #27ae60;">{}</span>',
           content
       )
   target_chunk_preview.short_description = "Hedef Chunk"
   
   def relation_type_display(self, obj):
       """İlişki tipi görüntüleme"""
       icons = {
           'follows': '➡️',
           'references': '🔗',
           'contradicts': '❌',
           'supports': '✅',
           'updates': '🔄'
       }
       
       icon = icons.get(obj.relation_type, '🔗')
       return format_html(
           '{} {}',
           icon, obj.get_relation_type_display()
       )
   relation_type_display.short_description = "İlişki Tipi"
   
   def confidence_display(self, obj):
       """Güven değeri görüntüleme"""
       confidence = obj.confidence
       
       if confidence >= 0.8:
           color = "#27ae60"
       elif confidence >= 0.6:
           color = "#f39c12"
       else:
           color = "#e74c3c"
       
       return format_html(
           '<span style="color: {};">{:.2f}</span>',
           color, confidence
       )
   confidence_display.short_description = "Güven"


# Admin site özelleştirmeleri
admin.site.register_view('sapbot_api/document_analytics/', 
                       view=lambda request: None, 
                       name='Document Analytics')