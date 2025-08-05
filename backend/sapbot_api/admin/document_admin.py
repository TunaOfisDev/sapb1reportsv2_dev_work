# backend/sapbot_api/admin/document_admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
import json
import csv

from ..models import DocumentSource, KnowledgeChunk
from ..utils.validators import validate_document_upload
from ..utils.file_handlers import FileManager
from ..utils.helpers import format_file_size, time_ago


class DocumentAnalyticsView(TemplateView):
    """Döküman analytics görünümü"""
    template_name = 'admin/sapbot_api/document_analytics.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Temel istatistikler
        total_documents = DocumentSource.objects.count()
        completed_documents = DocumentSource.objects.filter(processing_status='completed').count()
        pending_documents = DocumentSource.objects.filter(processing_status='pending').count()
        failed_documents = DocumentSource.objects.filter(processing_status='failed').count()
        
        # Chunk istatistikleri
        total_chunks = KnowledgeChunk.objects.count()
        
        # Son 30 gün
        last_30_days = timezone.now() - timedelta(days=30)
        recent_documents = DocumentSource.objects.filter(created_at__gte=last_30_days)
        
        # Döküman tipi dağılımı
        doc_type_stats = DocumentSource.objects.values('document_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # SAP modül dağılımı
        sap_module_stats = KnowledgeChunk.objects.values('sap_module').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # En çok kullanılan chunk'lar
        popular_chunks = KnowledgeChunk.objects.filter(
            usage_count__gt=0
        ).order_by('-usage_count')[:10]
        
        context.update({
            'total_documents': total_documents,
            'completed_documents': completed_documents,
            'pending_documents': pending_documents,
            'failed_documents': failed_documents,
            'success_rate': (completed_documents / total_documents * 100) if total_documents > 0 else 0,
            'total_chunks': total_chunks,
            'avg_chunks_per_doc': (total_chunks / completed_documents) if completed_documents > 0 else 0,
            'recent_documents_count': recent_documents.count(),
            'doc_type_stats': doc_type_stats,
            'sap_module_stats': sap_module_stats,
            'popular_chunks': popular_chunks,
        })
        
        return context


class BulkDocumentProcessView(TemplateView):
    """Toplu döküman işleme"""
    template_name = 'admin/sapbot_api/bulk_document_process.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        document_ids = request.POST.getlist('document_ids')
        
        if not document_ids:
            messages.error(request, 'Hiç döküman seçilmedi')
            return redirect('admin:bulk_document_process')
        
        documents = DocumentSource.objects.filter(id__in=document_ids)
        
        if action == 'reprocess':
            # Celery task ile yeniden işle
            from ..tasks import reprocess_documents_task
            task = reprocess_documents_task.delay(document_ids)
            
            messages.success(
                request, 
                f'{len(documents)} döküman yeniden işleme kuyruğuna eklendi. Task ID: {task.id}'
            )
            
        elif action == 'delete':
            chunk_count = KnowledgeChunk.objects.filter(source__in=documents).count()
            documents.delete()
            
            messages.success(
                request,
                f'{len(documents)} döküman ve {chunk_count} chunk silindi'
            )
            
        elif action == 'export':
            return self.export_documents(documents)
        
        return redirect('admin:bulk_document_process')
    
    def export_documents(self, documents):
        """Döküman listesini CSV olarak export et"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="documents_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Başlık', 'Tip', 'Dil', 'Durum', 'Boyut', 
            'Chunk Sayısı', 'Oluşturma Tarihi'
        ])
        
        for doc in documents:
            writer.writerow([
                doc.id,
                doc.title,
                doc.get_document_type_display(),
                doc.get_language_display(),
                doc.get_processing_status_display(),
                format_file_size(doc.file_size or 0),
                doc.chunk_count,
                doc.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


class DocumentSourceAdmin(admin.ModelAdmin):
    """Gelişmiş DocumentSource admin"""
    
    list_display = [
        'title', 'document_type', 'language', 'processing_status',
        'file_size_mb', 'chunk_count', 'created_at'
    ]
    
    list_filter = [
        'document_type', 'language', 'processing_status', 
        'is_active', 'created_at'
    ]
    
    search_fields = ['title', 'description', 'tags']
    
    readonly_fields = [
        'file_hash', 'processed_at', 'chunk_count', 
        'file_size_mb', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'description', 'document_type', 'language')
        }),
        ('Dosya Bilgileri', {
            'fields': ('file_path', 'file_size', 'file_size_mb', 'file_hash')
        }),
        ('İşleme Durumu', {
            'fields': ('processing_status', 'processed_at', 'processing_error')
        }),
        ('Metaveri', {
            'fields': ('tags', 'metadata', 'priority', 'is_public')
        }),
        ('Zaman Damgaları', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['reprocess_documents', 'mark_as_public', 'mark_as_private']
    
    def file_size_mb(self, obj):
        """Dosya boyutunu MB cinsinden göster"""
        if obj.file_size:
            return f"{obj.file_size / 1024 / 1024:.2f} MB"
        return "N/A"
    file_size_mb.short_description = 'Boyut (MB)'
    
    def chunk_count(self, obj):
        """Chunk sayısını göster"""
        return obj.chunks.count()
    chunk_count.short_description = 'Chunk Sayısı'
    
    def reprocess_documents(self, request, queryset):
        """Seçili dökümanları yeniden işle"""
        from ..tasks import reprocess_documents_task
        
        document_ids = list(queryset.values_list('id', flat=True))
        task = reprocess_documents_task.delay(document_ids)
        
        self.message_user(
            request,
            f'{len(document_ids)} döküman yeniden işleme kuyruğuna eklendi. Task ID: {task.id}'
        )
    reprocess_documents.short_description = 'Seçili dökümanları yeniden işle'
    
    def mark_as_public(self, request, queryset):
        """Herkese açık yap"""
        count = queryset.update(is_public=True)
        self.message_user(request, f'{count} döküman herkese açık yapıldı')
    mark_as_public.short_description = 'Herkese açık yap'
    
    def mark_as_private(self, request, queryset):
        """Özel yap"""
        count = queryset.update(is_public=False)
        self.message_user(request, f'{count} döküman özel yapıldı')
    mark_as_private.short_description = 'Özel yap'


class KnowledgeChunkAdmin(admin.ModelAdmin):
    """Gelişmiş KnowledgeChunk admin"""
    
    list_display = [
        'content_preview', 'source_title', 'sap_module', 
        'technical_level', 'usage_count', 'is_verified'
    ]
    
    list_filter = [
        'sap_module', 'technical_level', 'is_verified',
        'source__document_type', 'created_at'
    ]
    
    search_fields = ['content', 'keywords', 'source__title']
    
    readonly_fields = [
        'content_hash', 'content_length', 'usage_count', 
        'last_used', 'created_at', 'updated_at'
    ]
    
    raw_id_fields = ['source', 'verified_by']
    
    fieldsets = (
        ('İçerik', {
            'fields': ('source', 'content', 'content_hash', 'content_length')
        }),
        ('Sınıflandırma', {
            'fields': ('sap_module', 'technical_level', 'keywords')
        }),
        ('Sayfa Bilgileri', {
            'fields': ('page_number', 'section_title')
        }),
        ('Kalite ve Kullanım', {
            'fields': ('relevance_score', 'quality_score', 'usage_count', 'last_used')
        }),
        ('Doğrulama', {
            'fields': ('is_verified', 'verified_by')
        })
    )
    
    actions = ['mark_as_verified', 'reset_usage_count']
    
    def content_preview(self, obj):
        """İçerik önizlemesi"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'İçerik Önizlemesi'
    
    def source_title(self, obj):
        """Kaynak döküman başlığı"""
        return obj.source.title
    source_title.short_description = 'Kaynak Döküman'
    
    def mark_as_verified(self, request, queryset):
        """Doğrulanmış olarak işaretle"""
        count = queryset.update(is_verified=True, verified_by=request.user)
        self.message_user(request, f'{count} chunk doğrulandı')
    mark_as_verified.short_description = 'Doğrulanmış olarak işaretle'
    
    def reset_usage_count(self, request, queryset):
        """Kullanım sayacını sıfırla"""
        count = queryset.update(usage_count=0, last_used=None)
        self.message_user(request, f'{count} chunk kullanım sayacı sıfırlandı')
    reset_usage_count.short_description = 'Kullanım sayacını sıfırla'


# Custom AdminSite to handle custom views
class SAPBotAdminSite(admin.AdminSite):
    """SAPBot özel admin site"""
    site_header = 'SAPBot API Yönetimi'
    site_title = 'SAPBot Admin'
    index_title = 'SAPBot API Administration'
    
    def get_urls(self):
        """Admin URL'lerine custom view'ları ekle"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'sapbot_api/document_analytics/',
                self.admin_view(DocumentAnalyticsView.as_view()),
                name='document_analytics'
            ),
            path(
                'sapbot_api/bulk_document_process/',
                self.admin_view(BulkDocumentProcessView.as_view()),
                name='bulk_document_process'
            ),
        ]
        return custom_urls + urls


# Varsayılan admin site yerine custom site kullan
admin_site = SAPBotAdminSite(name='sapbot_admin')

# Model'leri kaydet
admin_site.register(DocumentSource, DocumentSourceAdmin)
admin_site.register(KnowledgeChunk, KnowledgeChunkAdmin)

# Django'nun varsayılan admin site'ını da güncelle
admin.site.register(DocumentSource, DocumentSourceAdmin)
admin.site.register(KnowledgeChunk, KnowledgeChunkAdmin)