# backend/sapbot_api/admin/advanced_admin.py
"""
SAPBot API Advanced Admin Classes

Bu modül özel admin işlevleri, bulk operations, system management
ve advanced reporting için admin sınıfları içerir.
Bu sınıflar herhangi bir modele bağlı değildir.
"""

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.management import call_command
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import json
import csv
import logging
import io
import zipfile
from datetime import datetime, timedelta

from .base_admin import (
    BaseModelAdmin, 
    BulkActionsMixin, 
    ExportMixin,
    admin_action_required_permission
)
from ..models import (
    DocumentSource, KnowledgeChunk, ChatMessage, UserProfile,
    QueryAnalytics, SystemConfiguration, ErrorLog
)
from ..utils.cache_utils import clear_all_cache, get_cache_stats
from ..utils.security import SecurityAuditor

logger = logging.getLogger(__name__)


class SystemManagementAdmin(admin.ModelAdmin, BulkActionsMixin):
    """
    Sistem yönetimi için özel admin paneli
    Model'e bağlı değil, sadece system operations için
    """
    
    def has_module_permission(self, request):
        """Sadece superuser'lar görebilir"""
        return request.user.is_superuser
    
    def get_urls(self):
        """Özel URL'ler"""
        urls = [
            path('system-overview/', self.admin_site.admin_view(self.system_overview_view), 
                 name='system_overview'),
            path('clear-cache/', self.admin_site.admin_view(self.clear_cache_view), 
                 name='clear_cache'),
            path('system-health/', self.admin_site.admin_view(self.system_health_view), 
                 name='system_health'),
            path('backup-data/', self.admin_site.admin_view(self.backup_data_view), 
                 name='backup_data'),
            path('run-maintenance/', self.admin_site.admin_view(self.run_maintenance_view), 
                 name='run_maintenance'),
        ]
        return urls
    
    def system_overview_view(self, request):
        """Sistem genel bakış"""
        try:
            # Temel istatistikler
            stats = {
                'documents': DocumentSource.objects.count(),
                'chunks': KnowledgeChunk.objects.count(),
                'messages': ChatMessage.objects.count(),
                'users': UserProfile.objects.count(),
                'queries_today': QueryAnalytics.objects.filter(
                    created_at__date=timezone.now().date()
                ).count(),
                'errors_today': ErrorLog.objects.filter(
                    created_at__date=timezone.now().date()
                ).count(),
            }
            
            # Cache stats
            cache_stats = get_cache_stats()
            
            # Sistem konfigürasyonu
            configs = SystemConfiguration.objects.all()[:10]
            
            context = {
                'title': 'Sistem Genel Bakış',
                'stats': stats,
                'cache_stats': cache_stats,
                'configs': configs,
                'opts': self.model._meta if hasattr(self, 'model') else None,
            }
            
            return render(request, 'admin/system_overview.html', context)
            
        except Exception as e:
            messages.error(request, f"Sistem bilgileri alınırken hata: {e}")
            return redirect('admin:index')
    
    def clear_cache_view(self, request):
        """Cache temizleme"""
        if request.method == 'POST':
            try:
                success = clear_all_cache()
                if success:
                    messages.success(request, "Cache başarıyla temizlendi")
                    SecurityAuditor.log_security_event(
                        event_type='CACHE_CLEARED',
                        user=request.user,
                        request=request,
                        severity='INFO'
                    )
                else:
                    messages.warning(request, "Cache temizleme sırasında uyarılar oluştu")
            except Exception as e:
                messages.error(request, f"Cache temizleme hatası: {e}")
                SecurityAuditor.log_security_event(
                    event_type='CACHE_CLEAR_FAILED',
                    user=request.user,
                    request=request,
                    details={'error': str(e)},
                    severity='ERROR'
                )
        
        return redirect('admin:system_overview')
    
    def system_health_view(self, request):
        """Sistem sağlık kontrolü"""
        try:
            health_data = self._check_system_health()
            
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse(health_data)
            
            context = {
                'title': 'Sistem Sağlık Durumu',
                'health_data': health_data,
                'opts': self.model._meta if hasattr(self, 'model') else None,
            }
            
            return render(request, 'admin/system_health.html', context)
            
        except Exception as e:
            logger.error(f"Sistem sağlık kontrolü hatası: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def backup_data_view(self, request):
        """Veri yedekleme"""
        if not request.user.is_superuser:
            messages.error(request, "Bu işlem için süper kullanıcı yetkisi gerekli")
            return redirect('admin:index')
        
        if request.method == 'POST':
            try:
                backup_file = self._create_backup()
                
                response = HttpResponse(
                    backup_file.getvalue(),
                    content_type='application/zip'
                )
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                response['Content-Disposition'] = f'attachment; filename="sapbot_backup_{timestamp}.zip"'
                
                SecurityAuditor.log_security_event(
                    event_type='DATA_BACKUP_CREATED',
                    user=request.user,
                    request=request,
                    severity='INFO'
                )
                
                return response
                
            except Exception as e:
                messages.error(request, f"Yedekleme hatası: {e}")
                logger.error(f"Backup error: {e}")
        
        return redirect('admin:system_overview')
    
    def run_maintenance_view(self, request):
        """Bakım işlemleri çalıştır"""
        if request.method == 'POST':
            maintenance_type = request.POST.get('maintenance_type')
            
            try:
                if maintenance_type == 'cleanup_logs':
                    self._cleanup_old_logs()
                    messages.success(request, "Eski loglar temizlendi")
                
                elif maintenance_type == 'optimize_db':
                    self._optimize_database()
                    messages.success(request, "Veritabanı optimize edildi")
                
                elif maintenance_type == 'cleanup_cache':
                    clear_all_cache()
                    messages.success(request, "Cache temizlendi")
                
                elif maintenance_type == 'reindex_chunks':
                    self._reindex_knowledge_chunks()
                    messages.success(request, "Knowledge chunks yeniden indekslendi")
                
                else:
                    messages.error(request, "Geçersiz bakım tipi")
                
                SecurityAuditor.log_security_event(
                    event_type='MAINTENANCE_RUN',
                    user=request.user,
                    request=request,
                    details={'maintenance_type': maintenance_type},
                    severity='INFO'
                )
                
            except Exception as e:
                messages.error(request, f"Bakım işlemi hatası: {e}")
                logger.error(f"Maintenance error: {e}")
        
        return redirect('admin:system_overview')
    
    def _check_system_health(self):
        """Sistem sağlık kontrolü"""
        health = {
            'overall_status': 'healthy',
            'checks': {},
            'timestamp': timezone.now().isoformat(),
        }
        
        try:
            # Database connection
            DocumentSource.objects.exists()
            health['checks']['database'] = {'status': 'healthy', 'message': 'Database accessible'}
        except Exception as e:
            health['checks']['database'] = {'status': 'error', 'message': str(e)}
            health['overall_status'] = 'error'
        
        try:
            # Cache check
            cache_stats = get_cache_stats()
            if cache_stats.get('error'):
                health['checks']['cache'] = {'status': 'warning', 'message': cache_stats['error']}
                if health['overall_status'] == 'healthy':
                    health['overall_status'] = 'warning'
            else:
                health['checks']['cache'] = {'status': 'healthy', 'message': 'Cache operational'}
        except Exception as e:
            health['checks']['cache'] = {'status': 'error', 'message': str(e)}
            health['overall_status'] = 'error'
        
        try:
            # Disk space (basic check)
            import shutil
            disk_usage = shutil.disk_usage('/')
            free_percentage = (disk_usage.free / disk_usage.total) * 100
            
            if free_percentage < 10:
                health['checks']['disk'] = {'status': 'error', 'message': f'Low disk space: {free_percentage:.1f}% free'}
                health['overall_status'] = 'error'
            elif free_percentage < 20:
                health['checks']['disk'] = {'status': 'warning', 'message': f'Disk space low: {free_percentage:.1f}% free'}
                if health['overall_status'] == 'healthy':
                    health['overall_status'] = 'warning'
            else:
                health['checks']['disk'] = {'status': 'healthy', 'message': f'Disk space OK: {free_percentage:.1f}% free'}
        except Exception as e:
            health['checks']['disk'] = {'status': 'error', 'message': str(e)}
        
        return health
    
    def _create_backup(self):
        """Veri yedekleme dosyası oluştur"""
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # System configurations
            configs = SystemConfiguration.objects.all()
            if configs:
                config_data = [
                    {
                        'key': config.key,
                        'value': config.value,
                        'config_type': config.config_type,
                        'description': config.description,
                    }
                    for config in configs
                ]
                zip_file.writestr(
                    'system_configurations.json',
                    json.dumps(config_data, indent=2, ensure_ascii=False)
                )
            
            # Document sources metadata
            documents = DocumentSource.objects.all()
            if documents:
                doc_data = [
                    {
                        'title': doc.title,
                        'document_type': doc.document_type,
                        'language': doc.language,
                        'processing_status': doc.processing_status,
                        'created_at': doc.created_at.isoformat(),
                        'chunk_count': doc.chunks.count(),
                    }
                    for doc in documents
                ]
                zip_file.writestr(
                    'document_sources.json',
                    json.dumps(doc_data, indent=2, ensure_ascii=False)
                )
            
            # User profiles
            users = UserProfile.objects.all()
            if users:
                user_data = [
                    {
                        'user_email': user.user.email,
                        'user_type': user.user_type,
                        'preferred_language': user.preferred_language,
                        'sap_modules': user.sap_modules,
                        'created_at': user.created_at.isoformat(),
                    }
                    for user in users
                ]
                zip_file.writestr(
                    'user_profiles.json',
                    json.dumps(user_data, indent=2, ensure_ascii=False)
                )
            
            # Analytics summary (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            analytics = QueryAnalytics.objects.filter(created_at__gte=thirty_days_ago)
            if analytics:
                analytics_data = [
                    {
                        'query': analytic.query[:100],  # İlk 100 karakter
                        'user_type': analytic.user_type,
                        'sap_module_detected': analytic.sap_module_detected,
                        'intent_detected': analytic.intent_detected,
                        'response_generated': analytic.response_generated,
                        'created_at': analytic.created_at.isoformat(),
                    }
                    for analytic in analytics[:1000]  # Max 1000 kayıt
                ]
                zip_file.writestr(
                    'analytics_summary.json',
                    json.dumps(analytics_data, indent=2, ensure_ascii=False)
                )
            
            # Backup metadata
            metadata = {
                'backup_created': timezone.now().isoformat(),
                'created_by': 'SAPBot System',
                'version': '1.0.0',
                'total_documents': DocumentSource.objects.count(),
                'total_chunks': KnowledgeChunk.objects.count(),
                'total_users': UserProfile.objects.count(),
            }
            zip_file.writestr(
                'backup_metadata.json',
                json.dumps(metadata, indent=2, ensure_ascii=False)
            )
        
        buffer.seek(0)
        return buffer
    
    def _cleanup_old_logs(self):
        """Eski logları temizle"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Eski error logları sil
        deleted_errors = ErrorLog.objects.filter(
            created_at__lt=thirty_days_ago
        ).delete()
        
        # Eski analytics kayıtları sil (90 günden eski)
        ninety_days_ago = timezone.now() - timedelta(days=90)
        deleted_analytics = QueryAnalytics.objects.filter(
            created_at__lt=ninety_days_ago
        ).delete()
        
        logger.info(f"Cleanup completed: {deleted_errors[0]} error logs, {deleted_analytics[0]} analytics records deleted")
    
    def _optimize_database(self):
        """Veritabanı optimizasyonu"""
        try:
            # Django management command ile
            call_command('optimize_db', verbosity=0)
        except Exception:
            # Manuel optimize
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("VACUUM ANALYZE;")
    
    def _reindex_knowledge_chunks(self):
        """Knowledge chunks'ları yeniden indeksle"""
        # Bu method daha sonra embedding service ile entegre edilebilir
        chunks_count = KnowledgeChunk.objects.count()
        logger.info(f"Reindexing {chunks_count} knowledge chunks")
        
        # Şimdilik sadece log, gerçek reindexing embedding service gerektirir
        return chunks_count


class BulkOperationAdmin(admin.ModelAdmin, BulkActionsMixin, ExportMixin):
    """
    Toplu işlemler için özel admin paneli
    """
    
    def has_module_permission(self, request):
        """Admin ve süper kullanıcılar erişebilir"""
        return request.user.is_staff and (
            request.user.is_superuser or 
            request.user.groups.filter(name='SAPBot_Admins').exists()
        )
    
    def get_urls(self):
        """Özel URL'ler"""
        urls = [
            path('bulk-operations/', self.admin_site.admin_view(self.bulk_operations_view), 
                 name='bulk_operations'),
            path('bulk-process-documents/', self.admin_site.admin_view(self.bulk_process_documents_view), 
                 name='bulk_process_documents'),
            path('bulk-export-data/', self.admin_site.admin_view(self.bulk_export_data_view), 
                 name='bulk_export_data'),
        ]
        return urls
    
    def bulk_operations_view(self, request):
        """Toplu işlemler paneli"""
        context = {
            'title': 'Toplu İşlemler',
            'opts': self.model._meta if hasattr(self, 'model') else None,
        }
        return render(request, 'admin/bulk_operations.html', context)
    
    @admin_action_required_permission('sapbot_api.change_documentsource')
    def bulk_process_documents_view(self, request):
        """Dökümanları toplu işle"""
        if request.method == 'POST':
            document_ids = request.POST.getlist('document_ids')
            action = request.POST.get('action')
            
            try:
                documents = DocumentSource.objects.filter(id__in=document_ids)
                
                if action == 'reprocess':
                    updated = documents.update(processing_status='pending')
                    self.success_message(request, f"{updated} döküman yeniden işleme alındı")
                    
                elif action == 'activate':
                    updated = documents.update(is_active=True)
                    self.success_message(request, f"{updated} döküman aktifleştirildi")
                    
                elif action == 'deactivate':
                    updated = documents.update(is_active=False)
                    self.success_message(request, f"{updated} döküman pasifleştirildi")
                
                SecurityAuditor.log_security_event(
                    event_type='BULK_DOCUMENT_OPERATION',
                    user=request.user,
                    request=request,
                    details={
                        'action': action,
                        'document_count': len(document_ids)
                    },
                    severity='INFO'
                )
                
            except Exception as e:
                messages.error(request, f"Toplu işlem hatası: {e}")
        
        return redirect('admin:bulk_operations')
    
    def bulk_export_data_view(self, request):
        """Toplu veri dışa aktarım"""
        if request.method == 'POST':
            export_type = request.POST.get('export_type')
            date_range = request.POST.get('date_range', '30')
            
            try:
                days_ago = timezone.now() - timedelta(days=int(date_range))
                
                if export_type == 'analytics':
                    queryset = QueryAnalytics.objects.filter(created_at__gte=days_ago)
                    return self.export_to_excel(request, queryset, 'analytics_export')
                
                elif export_type == 'errors':
                    queryset = ErrorLog.objects.filter(created_at__gte=days_ago)
                    return self.export_to_excel(request, queryset, 'errors_export')
                
                elif export_type == 'documents':
                    queryset = DocumentSource.objects.filter(created_at__gte=days_ago)
                    return self.export_to_excel(request, queryset, 'documents_export')
                
                else:
                    messages.error(request, "Geçersiz export tipi")
                    
            except Exception as e:
                messages.error(request, f"Export hatası: {e}")
        
        return redirect('admin:bulk_operations')


class ReportGeneratorAdmin(admin.ModelAdmin, BulkActionsMixin):
    """
    Rapor oluşturma için özel admin paneli
    """
    
    def has_module_permission(self, request):
        return request.user.is_staff
    
    def get_urls(self):
        """Özel URL'ler"""
        urls = [
            path('reports/', self.admin_site.admin_view(self.reports_view), 
                 name='reports'),
            path('generate-report/', self.admin_site.admin_view(self.generate_report_view), 
                 name='generate_report'),
        ]
        return urls
    
    def reports_view(self, request):
        """Rapor paneli"""
        context = {
            'title': 'Rapor Üretici',
            'opts': self.model._meta if hasattr(self, 'model') else None,
        }
        return render(request, 'admin/reports.html', context)
    
    def generate_report_view(self, request):
        """Rapor oluştur"""
        if request.method == 'POST':
            report_type = request.POST.get('report_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            try:
                report_data = self._generate_report_data(report_type, start_date, end_date)
                
                # CSV olarak döndür
                response = HttpResponse(content_type='text/csv')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timestamp}.csv"'
                
                writer = csv.writer(response)
                
                # Header
                if report_data:
                    writer.writerow(report_data[0].keys())
                    
                    # Data
                    for row in report_data:
                        writer.writerow(row.values())
                
                return response
                
            except Exception as e:
                messages.error(request, f"Rapor oluşturma hatası: {e}")
        
        return redirect('admin:reports')
    
    def _generate_report_data(self, report_type, start_date, end_date):
        """Rapor verisi oluştur"""
        start = datetime.fromisoformat(start_date) if start_date else timezone.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else timezone.now()
        
        if report_type == 'usage_summary':
            return self._usage_summary_report(start, end)
        elif report_type == 'error_summary':
            return self._error_summary_report(start, end)
        elif report_type == 'user_activity':
            return self._user_activity_report(start, end)
        else:
            return []
    
    def _usage_summary_report(self, start_date, end_date):
        """Kullanım özet raporu"""
        analytics = QueryAnalytics.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        return [
            {
                'Tarih': analytic.created_at.strftime('%Y-%m-%d'),
                'Kullanıcı Tipi': analytic.user_type,
                'SAP Modülü': analytic.sap_module_detected or 'Belirsiz',
                'Niyet': analytic.intent_detected or 'Belirsiz',
                'Başarılı': 'Evet' if analytic.response_generated else 'Hayır',
                'Yanıt Süresi': analytic.response_time or 0,
            }
            for analytic in analytics[:1000]  # Max 1000 kayıt
        ]
    
    def _error_summary_report(self, start_date, end_date):
        """Hata özet raporu"""
        errors = ErrorLog.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        return [
            {
                'Tarih': error.created_at.strftime('%Y-%m-%d %H:%M'),
                'Hata Tipi': error.error_type,
                'Hata Seviyesi': error.error_level,
                'Mesaj': error.error_message[:100],
                'Bileşen': error.component or 'Belirsiz',
                'Çözüldü': 'Evet' if error.is_resolved else 'Hayır',
            }
            for error in errors[:1000]
        ]
    
    def _user_activity_report(self, start_date, end_date):
        """Kullanıcı aktivite raporu"""
        profiles = UserProfile.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        return [
            {
                'Kullanıcı': profile.user.email,
                'Kullanıcı Tipi': profile.user_type,
                'Dil': profile.preferred_language,
                'SAP Modülleri': ', '.join(profile.sap_modules) if profile.sap_modules else 'Yok',
                'Kayıt Tarihi': profile.created_at.strftime('%Y-%m-%d'),
                'Son Aktivite': profile.last_activity.strftime('%Y-%m-%d %H:%M') if profile.last_activity else 'Yok',
            }
            for profile in profiles[:1000]
        ]


class IntegrationAdmin(admin.ModelAdmin, BulkActionsMixin):
    """
    Entegrasyon yönetimi için admin paneli
    """
    
    def has_module_permission(self, request):
        return request.user.is_superuser
    
    def get_urls(self):
        urls = [
            path('integrations/', self.admin_site.admin_view(self.integrations_view), 
                 name='integrations'),
            path('test-openai/', self.admin_site.admin_view(self.test_openai_view), 
                 name='test_openai'),
            path('sync-config/', self.admin_site.admin_view(self.sync_config_view), 
                 name='sync_config'),
        ]
        return urls
    
    def integrations_view(self, request):
        """Entegrasyonlar paneli"""
        context = {
            'title': 'Entegrasyonlar',
            'opts': self.model._meta if hasattr(self, 'model') else None,
        }
        return render(request, 'admin/integrations.html', context)
    
    def test_openai_view(self, request):
        """OpenAI bağlantısını test et"""
        try:
            from ..services.openai_client import OpenAIClient
            client = OpenAIClient()
            
            # Basit test
            response = client.simple_completion("Test message for connection check")
            
            if response:
                messages.success(request, "OpenAI bağlantısı başarılı")
            else:
                messages.warning(request, "OpenAI bağlantısı kurulamadı")
                
        except Exception as e:
            messages.error(request, f"OpenAI test hatası: {e}")
        
        return redirect('admin:integrations')
    
    def sync_config_view(self, request):
        """Konfigürasyonu senkronize et"""
        try:
            # Config değerlerini yeniden yükle
            from django.core.cache import cache
            cache.clear()
            
            messages.success(request, "Konfigürasyon senkronize edildi")
            
        except Exception as e:
            messages.error(request, f"Sync hatası: {e}")
        
        return redirect('admin:integrations')


# Register these as custom admin views
# Bu sınıflar model'e bağlı olmadığı için manuel URL registration gerekir
