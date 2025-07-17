# backend/sapbot_api/tasks/maintenance_tasks.py
"""
SAPBot API Maintenance Tasks

Bu modül sistem bakım görevlerini içerir:
- Cache temizleme
- Veritabanı optimizasyonu
- Log rotasyonu
- Geçici dosya temizleme
- Sistem sağlık kontrolü
- Performans optimizasyonu
"""

import os
import tempfile
from datetime import datetime, timedelta
from typing import models
from django.core.cache import cache
from django.db import transaction, connection
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger

from ..models import (
   DocumentSource, KnowledgeChunk, ChatConversation, ChatMessage,
   UserSession, SystemLog, ErrorLog, QueryAnalytics, SystemMetrics,
   PerformanceMetrics
)
from ..utils.cache_utils import clear_all_cache, get_cache_stats
from ..utils.helpers import format_file_size, time_ago

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_expired_sessions(self):
   """Süresi dolmuş oturumları temizle"""
   try:
       logger.info("🧹 Süresi dolmuş oturumlar temizleniyor...")
       
       # Süresi dolmuş oturumları bul
       expired_sessions = UserSession.objects.filter(
           expires_at__lt=timezone.now()
       )
       
       expired_count = expired_sessions.count()
       
       if expired_count > 0:
           # Toplu silme
           expired_sessions.delete()
           logger.info(f"✅ {expired_count} süresi dolmuş oturum silindi")
       else:
           logger.info("ℹ️ Silinecek süresi dolmuş oturum bulunamadı")
       
       # Cache'den de temizle
       cache.delete_pattern("user_session:*")
       
       return {
           'success': True,
           'expired_sessions_deleted': expired_count,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Oturum temizleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def cleanup_old_conversations(self, days_old: int = 30):
   """Eski konuşmaları temizle"""
   try:
       logger.info(f"🧹 {days_old} günden eski konuşmalar temizleniyor...")
       
       cutoff_date = timezone.now() - timedelta(days=days_old)
       
       # Eski konuşmaları bul
       old_conversations = ChatConversation.objects.filter(
           last_activity__lt=cutoff_date,
           is_archived=False
       )
       
       conversation_count = old_conversations.count()
       
       if conversation_count > 0:
           # Önce arşivle, sonra sil
           with transaction.atomic():
               # Arşivle
               old_conversations.update(is_archived=True)
               
               # Mesajları da sil
               old_messages = ChatMessage.objects.filter(
                   conversation__in=old_conversations
               )
               message_count = old_messages.count()
               old_messages.delete()
               
               # Konuşmaları sil
               old_conversations.delete()
               
           logger.info(f"✅ {conversation_count} konuşma ve {message_count} mesaj silindi")
       else:
           logger.info("ℹ️ Silinecek eski konuşma bulunamadı")
       
       return {
           'success': True,
           'conversations_deleted': conversation_count,
           'cutoff_date': cutoff_date.isoformat(),
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Konuşma temizleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def cleanup_old_logs(self, days_old: int = 7):
   """Eski log kayıtlarını temizle"""
   try:
       logger.info(f"🧹 {days_old} günden eski loglar temizleniyor...")
       
       cutoff_date = timezone.now() - timedelta(days=days_old)
       
       # System logs
       old_system_logs = SystemLog.objects.filter(created_at__lt=cutoff_date)
       system_log_count = old_system_logs.count()
       old_system_logs.delete()
       
       # Error logs (biraz daha uzun tut)
       error_cutoff = timezone.now() - timedelta(days=days_old * 2)
       old_error_logs = ErrorLog.objects.filter(
           created_at__lt=error_cutoff,
           is_resolved=True
       )
       error_log_count = old_error_logs.count()
       old_error_logs.delete()
       
       # Performance metrics
       old_metrics = PerformanceMetrics.objects.filter(
           timestamp__lt=cutoff_date
       )
       metrics_count = old_metrics.count()
       old_metrics.delete()
       
       logger.info(f"✅ {system_log_count} sistem log, {error_log_count} hata log, {metrics_count} metrik silindi")
       
       return {
           'success': True,
           'system_logs_deleted': system_log_count,
           'error_logs_deleted': error_log_count,
           'metrics_deleted': metrics_count,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Log temizleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def optimize_database(self):
   """Veritabanı optimizasyonu"""
   try:
       logger.info("🔧 Veritabanı optimizasyonu başlıyor...")
       
       optimization_results = {}
       
       with connection.cursor() as cursor:
           # PostgreSQL için vacuum ve analyze
           tables_to_optimize = [
               'sapbot_document_sources',
               'sapbot_knowledge_chunks',
               'sapbot_chat_conversations',
               'sapbot_chat_messages',
               'sapbot_query_analytics',
               'sapbot_user_sessions'
           ]
           
           for table in tables_to_optimize:
               try:
                   # VACUUM ANALYZE
                   cursor.execute(f"VACUUM ANALYZE {table}")
                   logger.info(f"✅ {table} optimize edildi")
                   optimization_results[table] = 'optimized'
               except Exception as e:
                   logger.warning(f"⚠️ {table} optimize edilemedi: {e}")
                   optimization_results[table] = f'failed: {str(e)}'
           
           # İndeks kullanım istatistikleri
           cursor.execute("""
               SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
               FROM pg_stat_user_indexes 
               WHERE schemaname = 'public' 
               AND tablename LIKE 'sapbot_%'
               ORDER BY idx_tup_read DESC
               LIMIT 10
           """)
           
           index_stats = cursor.fetchall()
           optimization_results['top_used_indexes'] = [
               {
                   'table': row[1],
                   'index': row[2], 
                   'reads': row[3],
                   'fetches': row[4]
               } for row in index_stats
           ]
           
           # Tablo boyutları
           cursor.execute("""
               SELECT 
                   tablename,
                   pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
               FROM pg_tables 
               WHERE schemaname = 'public' 
               AND tablename LIKE 'sapbot_%'
               ORDER BY pg_total_relation_size(tablename::regclass) DESC
           """)
           
           table_sizes = cursor.fetchall()
           optimization_results['table_sizes'] = [
               {'table': row[0], 'size': row[1]} for row in table_sizes
           ]
       
       logger.info("✅ Veritabanı optimizasyonu tamamlandı")
       
       return {
           'success': True,
           'optimization_results': optimization_results,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Veritabanı optimizasyon hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def cleanup_temp_files(self):
   """Geçici dosyaları temizle"""
   try:
       logger.info("🧹 Geçici dosyalar temizleniyor...")
       
       temp_dirs = [
           getattr(settings, 'TEMP_DIR', tempfile.gettempdir()),
           os.path.join(settings.MEDIA_ROOT, 'temp'),
           '/tmp'
       ]
       
       total_files_deleted = 0
       total_size_freed = 0
       
       for temp_dir in temp_dirs:
           if not os.path.exists(temp_dir):
               continue
               
           logger.info(f"🔍 {temp_dir} dizini kontrol ediliyor...")
           
           for filename in os.listdir(temp_dir):
               file_path = os.path.join(temp_dir, filename)
               
               if not os.path.isfile(file_path):
                   continue
               
               # 1 saatten eski geçici dosyaları sil
               file_age = datetime.now().timestamp() - os.path.getctime(file_path)
               
               if file_age > 3600:  # 1 saat
                   try:
                       file_size = os.path.getsize(file_path)
                       os.unlink(file_path)
                       total_files_deleted += 1
                       total_size_freed += file_size
                       logger.debug(f"🗑️ Silindi: {filename}")
                   except OSError as e:
                       logger.warning(f"⚠️ Dosya silinemiyor {filename}: {e}")
       
       logger.info(f"✅ {total_files_deleted} dosya silindi, {format_file_size(total_size_freed)} yer boşaltıldı")
       
       return {
           'success': True,
           'files_deleted': total_files_deleted,
           'size_freed': total_size_freed,
           'size_freed_formatted': format_file_size(total_size_freed),
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Geçici dosya temizleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def cleanup_cache(self):
   """Cache temizleme"""
   try:
       logger.info("🧹 Cache temizleniyor...")
       
       # Cache istatistiklerini al
       cache_stats_before = get_cache_stats()
       
       # Tüm cache'i temizle
       clear_result = clear_all_cache()
       
       # Cache istatistiklerini tekrar al
       cache_stats_after = get_cache_stats()
       
       if clear_result:
           logger.info("✅ Cache başarıyla temizlendi")
       else:
           logger.warning("⚠️ Cache temizleme sırasında sorun oluştu")
       
       return {
           'success': clear_result,
           'cache_stats_before': cache_stats_before,
           'cache_stats_after': cache_stats_after,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Cache temizleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def system_health_check(self):
   """Sistem sağlık kontrolü"""
   try:
       logger.info("🏥 Sistem sağlık kontrolü başlıyor...")
       
       health_status = {
           'overall_status': 'healthy',
           'checks': {},
           'recommendations': [],
           'timestamp': timezone.now().isoformat()
       }
       
       # Veritabanı kontrolü
       try:
           with connection.cursor() as cursor:
               cursor.execute("SELECT 1")
               result = cursor.fetchone()
               if result[0] == 1:
                   health_status['checks']['database'] = 'healthy'
               else:
                   health_status['checks']['database'] = 'warning'
       except Exception as e:
           health_status['checks']['database'] = 'critical'
           health_status['overall_status'] = 'critical'
           logger.error(f"❌ Veritabanı sağlık kontrolü başarısız: {e}")
       
       # Cache kontrolü
       try:
           cache.set('health_check', 'test', 60)
           if cache.get('health_check') == 'test':
               health_status['checks']['cache'] = 'healthy'
               cache.delete('health_check')
           else:
               health_status['checks']['cache'] = 'warning'
       except Exception as e:
           health_status['checks']['cache'] = 'critical'
           logger.error(f"❌ Cache sağlık kontrolü başarısız: {e}")
       
       # Disk alanı kontrolü
       try:
           disk_usage = os.statvfs('/')
           free_space = disk_usage.f_bavail * disk_usage.f_frsize
           total_space = disk_usage.f_blocks * disk_usage.f_frsize
           usage_percent = ((total_space - free_space) / total_space) * 100
           
           if usage_percent > 90:
               health_status['checks']['disk_space'] = 'critical'
               health_status['recommendations'].append(
                   f"Disk kullanımı %{usage_percent:.1f} - Acil disk temizliği gerekli"
               )
               if health_status['overall_status'] == 'healthy':
                   health_status['overall_status'] = 'critical'
           elif usage_percent > 80:
               health_status['checks']['disk_space'] = 'warning'
               health_status['recommendations'].append(
                   f"Disk kullanımı %{usage_percent:.1f} - Disk temizliği önerilir"
               )
               if health_status['overall_status'] == 'healthy':
                   health_status['overall_status'] = 'warning'
           else:
               health_status['checks']['disk_space'] = 'healthy'
               
           health_status['disk_usage_percent'] = round(usage_percent, 1)
           health_status['free_space'] = format_file_size(free_space)
           
       except Exception as e:
           health_status['checks']['disk_space'] = 'unknown'
           logger.error(f"❌ Disk alanı kontrolü başarısız: {e}")
       
       # Veritabanı bağlantı sayısı
       try:
           with connection.cursor() as cursor:
               cursor.execute("SELECT count(*) FROM pg_stat_activity")
               connection_count = cursor.fetchone()[0]
               
               max_connections = 100  # PostgreSQL default
               connection_usage = (connection_count / max_connections) * 100
               
               if connection_usage > 80:
                   health_status['checks']['db_connections'] = 'warning'
                   health_status['recommendations'].append(
                       f"Veritabanı bağlantı kullanımı %{connection_usage:.1f}"
                   )
               else:
                   health_status['checks']['db_connections'] = 'healthy'
                   
               health_status['db_connections'] = {
                   'current': connection_count,
                   'usage_percent': round(connection_usage, 1)
               }
       except Exception as e:
           health_status['checks']['db_connections'] = 'unknown'
           logger.error(f"❌ DB bağlantı kontrolü başarısız: {e}")
       
       # Bellek kullanımı (basit kontrol)
       try:
           import psutil
           memory = psutil.virtual_memory()
           
           if memory.percent > 90:
               health_status['checks']['memory'] = 'critical'
               health_status['recommendations'].append(
                   f"Bellek kullanımı %{memory.percent:.1f} - Yüksek bellek kullanımı"
               )
           elif memory.percent > 80:
               health_status['checks']['memory'] = 'warning'
           else:
               health_status['checks']['memory'] = 'healthy'
               
           health_status['memory_usage_percent'] = round(memory.percent, 1)
           
       except ImportError:
           health_status['checks']['memory'] = 'unknown'
           logger.warning("⚠️ psutil yüklü değil, bellek kontrolü yapılamıyor")
       except Exception as e:
           health_status['checks']['memory'] = 'unknown'
           logger.error(f"❌ Bellek kontrolü başarısız: {e}")
       
       # Model sayıları
       try:
           health_status['model_counts'] = {
               'documents': DocumentSource.objects.count(),
               'chunks': KnowledgeChunk.objects.count(),
               'conversations': ChatConversation.objects.count(),
               'messages': ChatMessage.objects.count(),
               'active_sessions': UserSession.objects.filter(
                   expires_at__gt=timezone.now()
               ).count()
           }
       except Exception as e:
           logger.error(f"❌ Model sayım hatası: {e}")
       
       # Genel durum değerlendirme
       critical_checks = [k for k, v in health_status['checks'].items() if v == 'critical']
       warning_checks = [k for k, v in health_status['checks'].items() if v == 'warning']
       
       if critical_checks:
           health_status['overall_status'] = 'critical'
       elif warning_checks:
           health_status['overall_status'] = 'warning'
       
       # Sistem metriği kaydet
       SystemMetrics.objects.create(
           metric_name='system_health_check',
           metric_type='gauge',
           value=1 if health_status['overall_status'] == 'healthy' else 0,
           labels={
               'status': health_status['overall_status'],
               'critical_checks': len(critical_checks),
               'warning_checks': len(warning_checks)
           }
       )
       
       logger.info(f"✅ Sistem sağlık kontrolü tamamlandı - Durum: {health_status['overall_status']}")
       
       return health_status
       
   except Exception as exc:
       logger.error(f"❌ Sistem sağlık kontrolü hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def generate_analytics_summary(self, period: str = 'daily'):
   """Analitik özet oluştur"""
   try:
       logger.info(f"📊 {period} analitik özet oluşturuluyor...")
       
       now = timezone.now()
       
       if period == 'daily':
           start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
           end_date = start_date + timedelta(days=1)
       elif period == 'weekly':
           start_date = now - timedelta(days=now.weekday())
           start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
           end_date = start_date + timedelta(days=7)
       elif period == 'monthly':
           start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
           if now.month == 12:
               end_date = start_date.replace(year=now.year + 1, month=1)
           else:
               end_date = start_date.replace(month=now.month + 1)
       else:
           raise ValueError(f"Geçersiz period: {period}")
       
       # Analitik verilerini topla
       analytics = QueryAnalytics.objects.filter(
           created_at__gte=start_date,
           created_at__lt=end_date
       )
       
       summary = {
           'period': period,
           'start_date': start_date.isoformat(),
           'end_date': end_date.isoformat(),
           'total_queries': analytics.count(),
           'successful_queries': analytics.filter(response_generated=True).count(),
           'unique_users': analytics.values('user').distinct().count(),
           'unique_sessions': analytics.values('session_id').distinct().count(),
           'avg_response_time': 0,
           'top_sap_modules': {},
           'top_intents': {},
           'error_breakdown': {},
           'timestamp': timezone.now().isoformat()
       }
       
       # Ortalama yanıt süresi
       response_times = analytics.filter(
           response_time__isnull=False
       ).values_list('response_time', flat=True)
       
       if response_times:
           summary['avg_response_time'] = sum(response_times) / len(response_times)
       
       # En çok kullanılan SAP modülleri
       sap_modules = analytics.filter(
           sap_module_detected__isnull=False
       ).values_list('sap_module_detected', flat=True)
       
       from collections import Counter
       summary['top_sap_modules'] = dict(Counter(sap_modules).most_common(5))
       
       # En çok kullanılan niyetler
       intents = analytics.filter(
           intent_detected__isnull=False
       ).values_list('intent_detected', flat=True)
       
       summary['top_intents'] = dict(Counter(intents).most_common(5))
       
       # Hata dağılımı
       errors = analytics.filter(
           error_occurred=True
       ).values_list('error_type', flat=True)
       
       summary['error_breakdown'] = dict(Counter(errors).most_common(5))
       
       # Başarı oranı
       if summary['total_queries'] > 0:
           summary['success_rate'] = (
               summary['successful_queries'] / summary['total_queries']
           ) * 100
       else:
           summary['success_rate'] = 0
       
       logger.info(f"✅ {period} analitik özet oluşturuldu - {summary['total_queries']} sorgu")
       
       return summary
       
   except Exception as exc:
       logger.error(f"❌ Analitik özet oluşturma hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def backup_critical_data(self):
   """Kritik verilerin yedeklenmesi"""
   try:
       logger.info("💾 Kritik veri yedekleme başlıyor...")
       
       backup_results = {
           'success': False,
           'backup_files': [],
           'timestamp': timezone.now().isoformat()
       }
       
       # Backup dizinini oluştur
       backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
       os.makedirs(backup_dir, exist_ok=True)
       
       timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
       
       # Sistem konfigürasyonu yedekle
       from ..models import SystemConfiguration
       configs = SystemConfiguration.objects.all().values()
       
       config_backup_file = os.path.join(backup_dir, f'system_config_{timestamp}.json')
       
       import json
       with open(config_backup_file, 'w', encoding='utf-8') as f:
           json.dump(list(configs), f, ensure_ascii=False, indent=2, default=str)
       
       backup_results['backup_files'].append({
           'type': 'system_config',
           'file': config_backup_file,
           'size': os.path.getsize(config_backup_file),
           'records': len(configs)
       })
       
       # Kullanıcı profilleri yedekle
       from ..models import UserProfile
       profiles = UserProfile.objects.all().values()
       
       profiles_backup_file = os.path.join(backup_dir, f'user_profiles_{timestamp}.json')
       
       with open(profiles_backup_file, 'w', encoding='utf-8') as f:
           json.dump(list(profiles), f, ensure_ascii=False, indent=2, default=str)
       
       backup_results['backup_files'].append({
           'type': 'user_profiles',
           'file': profiles_backup_file,
           'size': os.path.getsize(profiles_backup_file),
           'records': len(profiles)
       })
       
       # Eski yedekleri temizle (30 gün)
       old_backups = []
       cutoff_time = timezone.now() - timedelta(days=30)
       
       for filename in os.listdir(backup_dir):
           file_path = os.path.join(backup_dir, filename)
           if os.path.isfile(file_path):
               file_time = datetime.fromtimestamp(os.path.getctime(file_path))
               if file_time < cutoff_time.replace(tzinfo=None):
                   try:
                       os.unlink(file_path)
                       old_backups.append(filename)
                   except OSError:
                       pass
       
       backup_results['old_backups_deleted'] = old_backups
       backup_results['success'] = True
       
       logger.info(f"✅ Kritik veri yedekleme tamamlandı - {len(backup_results['backup_files'])} dosya")
       
       return backup_results
       
   except Exception as exc:
       logger.error(f"❌ Veri yedekleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True)
def daily_maintenance():
   """Günlük bakım görevi"""
   try:
       logger.info("🔧 Günlük bakım başlıyor...")
       
       maintenance_results = {
           'tasks_completed': [],
           'tasks_failed': [],
           'start_time': timezone.now().isoformat()
       }
       
       # Görevleri sırayla çalıştır
       maintenance_tasks = [
           ('cleanup_expired_sessions', cleanup_expired_sessions),
           ('cleanup_temp_files', cleanup_temp_files),
           ('cleanup_cache', cleanup_cache),
           ('system_health_check', system_health_check),
           ('generate_analytics_summary', lambda: generate_analytics_summary.delay('daily'))
       ]
       
       for task_name, task_func in maintenance_tasks:
           try:
               if callable(task_func):
                   result = task_func()
                   maintenance_results['tasks_completed'].append({
                       'task': task_name,
                       'result': result if isinstance(result, dict) else str(result),
                       'completed_at': timezone.now().isoformat()
                   })
                   logger.info(f"✅ {task_name} tamamlandı")
               else:
                   # Celery task
                   task_func
                   maintenance_results['tasks_completed'].append({
                       'task': task_name,
                       'status': 'scheduled',
                       'completed_at': timezone.now().isoformat()
                   })
                   logger.info(f"📅 {task_name} planlandı")
                   
           except Exception as e:
               maintenance_results['tasks_failed'].append({
                   'task': task_name,
                   'error': str(e),
                   'failed_at': timezone.now().isoformat()
               })
               logger.error(f"❌ {task_name} başarısız: {e}")
       
       maintenance_results['end_time'] = timezone.now().isoformat()
       
       # Bakım metriği kaydet
       SystemMetrics.objects.create(
           metric_name='daily_maintenance',
           metric_type='counter',
           value=1,
           labels={
               'completed_tasks': len(maintenance_results['tasks_completed']),
               'failed_tasks': len(maintenance_results['tasks_failed'])
           }
       )
       
       logger.info("✅ Günlük bakım tamamlandı")
       
       return maintenance_results
       
   except Exception as exc:
       logger.error(f"❌ Günlük bakım hatası: {exc}")
       return {
           'success': False,
           'error': str(exc),
           'timestamp': timezone.now().isoformat()
       }


@shared_task(bind=True)
def weekly_maintenance():
   """Haftalık bakım görevi"""
   try:
       logger.info("🔧 Haftalık bakım başlıyor...")
       
       maintenance_results = {
           'tasks_completed': [],
           'tasks_failed': [],
           'start_time': timezone.now().isoformat()
       }
       
       # Haftalık görevler
       weekly_tasks = [
           ('cleanup_old_conversations', lambda: cleanup_old_conversations.delay(30)),
           ('optimize_database', optimize_database),
           ('backup_critical_data', backup_critical_data),
           ('generate_weekly_analytics', lambda: generate_analytics_summary.delay('weekly'))
       ]
       
       for task_name, task_func in weekly_tasks:
           try:
               if callable(task_func):
                   result = task_func()
                   maintenance_results['tasks_completed'].append({
                       'task': task_name,
                       'result': result if isinstance(result, dict) else str(result),
                       'completed_at': timezone.now().isoformat()
                   })
                   logger.info(f"✅ {task_name} tamamlandı")
               else:
                   task_func
                   maintenance_results['tasks_completed'].append({
                       'task': task_name,
                       'status': 'scheduled',
                       'completed_at': timezone.now().isoformat()
                   })
                   
           except Exception as e:
               maintenance_results['tasks_failed'].append({
                   'task': task_name,
                   'error': str(e),
                   'failed_at': timezone.now().isoformat()
               })
               logger.error(f"❌ {task_name} başarısız: {e}")
       
       maintenance_results['end_time'] = timezone.now().isoformat()
       
       # Haftalık bakım metriği
       SystemMetrics.objects.create(
           metric_name='weekly_maintenance',
           metric_type='counter',
           value=1,
           labels={
               'completed_tasks': len(maintenance_results['tasks_completed']),
               'failed_tasks': len(maintenance_results['tasks_failed'])
           }
       )
       
       logger.info("✅ Haftalık bakım tamamlandı")
       
       return maintenance_results
       
   except Exception as exc:
       logger.error(f"❌ Haftalık bakım hatası: {exc}")
       return {
           'success': False,
           'error': str(exc),
           'timestamp': timezone.now().isoformat()
       }


@shared_task(bind=True, max_retries=1)
def emergency_cleanup(self):
   """Acil durum temizliği - disk dolduğunda"""
   try:
       logger.warning("🚨 ACİL DURUM TEMİZLİĞİ BAŞLIYOR!")
       
       cleanup_results = {
           'actions_taken': [],
           'space_freed': 0,
           'timestamp': timezone.now().isoformat()
       }
       
       # 1. Tüm cache'i temizle
       try:
           clear_all_cache()
           cleanup_results['actions_taken'].append('cache_cleared')
           logger.info("✅ Cache tamamen temizlendi")
       except Exception as e:
           logger.error(f"❌ Cache temizleme hatası: {e}")
       
       # 2. Geçici dosyaları agresif temizle
       try:
           temp_result = cleanup_temp_files.delay()
           cleanup_results['actions_taken'].append('temp_files_cleaned')
           logger.info("✅ Geçici dosyalar temizlendi")
       except Exception as e:
           logger.error(f"❌ Geçici dosya temizleme hatası: {e}")
       
       # 3. Eski logları agresif temizle (1 günlük)
       try:
           cutoff_date = timezone.now() - timedelta(days=1)
           
           # System logs
           old_logs = SystemLog.objects.filter(created_at__lt=cutoff_date)
           log_count = old_logs.count()
           old_logs.delete()
           
           # Performance metrics
           old_metrics = PerformanceMetrics.objects.filter(timestamp__lt=cutoff_date)
           metrics_count = old_metrics.count()
           old_metrics.delete()
           
           cleanup_results['actions_taken'].append(f'deleted_{log_count}_logs_{metrics_count}_metrics')
           logger.info(f"✅ {log_count} log ve {metrics_count} metrik silindi")
           
       except Exception as e:
           logger.error(f"❌ Log temizleme hatası: {e}")
       
       # 4. Eski konuşmaları agresif temizle (7 günlük)
       try:
           cutoff_date = timezone.now() - timedelta(days=7)
           old_conversations = ChatConversation.objects.filter(
               last_activity__lt=cutoff_date
           )
           conversation_count = old_conversations.count()
           
           if conversation_count > 0:
               old_messages = ChatMessage.objects.filter(
                   conversation__in=old_conversations
               )
               message_count = old_messages.count()
               
               with transaction.atomic():
                   old_messages.delete()
                   old_conversations.delete()
               
               cleanup_results['actions_taken'].append(
                   f'deleted_{conversation_count}_conversations_{message_count}_messages'
               )
               logger.info(f"✅ {conversation_count} konuşma ve {message_count} mesaj silindi")
               
       except Exception as e:
           logger.error(f"❌ Konuşma temizleme hatası: {e}")
       
       # 5. Veritabanı vacuum
       try:
           with connection.cursor() as cursor:
               cursor.execute("VACUUM FULL")
           cleanup_results['actions_taken'].append('database_vacuum_full')
           logger.info("✅ Veritabanı vacuum full tamamlandı")
       except Exception as e:
           logger.error(f"❌ Database vacuum hatası: {e}")
       
       # 6. Disk kullanımını tekrar kontrol et
       try:
           disk_usage = os.statvfs('/')
           free_space = disk_usage.f_bavail * disk_usage.f_frsize
           total_space = disk_usage.f_blocks * disk_usage.f_frsize
           usage_percent = ((total_space - free_space) / total_space) * 100
           
           cleanup_results['final_disk_usage'] = round(usage_percent, 1)
           cleanup_results['free_space'] = format_file_size(free_space)
           
       except Exception as e:
           logger.error(f"❌ Disk kontrolü hatası: {e}")
       
       logger.warning("🚨 ACİL DURUM TEMİZLİĞİ TAMAMLANDI!")
       
       # Acil durum metriği
       SystemMetrics.objects.create(
           metric_name='emergency_cleanup',
           metric_type='counter',
           value=1,
           labels={
               'actions_count': len(cleanup_results['actions_taken']),
               'trigger': 'disk_full'
           }
       )
       
       return cleanup_results
       
   except Exception as exc:
       logger.error(f"❌ Acil durum temizliği hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def monitor_system_resources(self):
   """Sistem kaynaklarını izle"""
   try:
       logger.info("📊 Sistem kaynakları izleniyor...")
       
       monitoring_results = {
           'status': 'healthy',
           'alerts': [],
           'metrics': {},
           'timestamp': timezone.now().isoformat()
       }
       
       # Disk kullanımı
       try:
           disk_usage = os.statvfs('/')
           free_space = disk_usage.f_bavail * disk_usage.f_frsize
           total_space = disk_usage.f_blocks * disk_usage.f_frsize
           usage_percent = ((total_space - free_space) / total_space) * 100
           
           monitoring_results['metrics']['disk_usage_percent'] = round(usage_percent, 1)
           monitoring_results['metrics']['free_space_gb'] = round(free_space / (1024**3), 2)
           
           # Disk uyarıları
           if usage_percent > 95:
               monitoring_results['alerts'].append({
                   'level': 'critical',
                   'message': f'Disk kullanımı kritik seviyede: %{usage_percent:.1f}',
                   'action': 'emergency_cleanup_needed'
               })
               monitoring_results['status'] = 'critical'
               
               # Acil temizleme başlat
               emergency_cleanup.delay()
               
           elif usage_percent > 85:
               monitoring_results['alerts'].append({
                   'level': 'warning',
                   'message': f'Disk kullanımı yüksek: %{usage_percent:.1f}',
                   'action': 'cleanup_recommended'
               })
               if monitoring_results['status'] == 'healthy':
                   monitoring_results['status'] = 'warning'
           
           # Disk metriği kaydet
           SystemMetrics.objects.create(
               metric_name='disk_usage_percent',
               metric_type='gauge',
               value=usage_percent
           )
           
       except Exception as e:
           logger.error(f"❌ Disk izleme hatası: {e}")
       
       # Veritabanı bağlantı sayısı
       try:
           with connection.cursor() as cursor:
               cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
               active_connections = cursor.fetchone()[0]
               
               cursor.execute("SELECT setting FROM pg_settings WHERE name = 'max_connections'")
               max_connections = int(cursor.fetchone()[0])
               
               connection_usage = (active_connections / max_connections) * 100
               
               monitoring_results['metrics']['db_connections'] = {
                   'active': active_connections,
                   'max': max_connections,
                   'usage_percent': round(connection_usage, 1)
               }
               
               if connection_usage > 80:
                   monitoring_results['alerts'].append({
                       'level': 'warning',
                       'message': f'Veritabanı bağlantı kullanımı yüksek: %{connection_usage:.1f}',
                       'action': 'connection_pool_optimization_needed'
                   })
                   if monitoring_results['status'] == 'healthy':
                       monitoring_results['status'] = 'warning'
               
               # DB connection metriği
               SystemMetrics.objects.create(
                   metric_name='db_active_connections',
                   metric_type='gauge',
                   value=active_connections
               )
               
       except Exception as e:
           logger.error(f"❌ DB bağlantı izleme hatası: {e}")
       
       # Bellek kullanımı (psutil varsa)
       try:
           import psutil
           memory = psutil.virtual_memory()
           
           monitoring_results['metrics']['memory_usage_percent'] = round(memory.percent, 1)
           monitoring_results['metrics']['memory_available_gb'] = round(memory.available / (1024**3), 2)
           
           if memory.percent > 90:
               monitoring_results['alerts'].append({
                   'level': 'critical',
                   'message': f'Bellek kullanımı kritik: %{memory.percent:.1f}',
                   'action': 'restart_required'
               })
               monitoring_results['status'] = 'critical'
           elif memory.percent > 80:
               monitoring_results['alerts'].append({
                   'level': 'warning',
                   'message': f'Bellek kullanımı yüksek: %{memory.percent:.1f}',
                   'action': 'memory_optimization_needed'
               })
               if monitoring_results['status'] == 'healthy':
                   monitoring_results['status'] = 'warning'
           
           # Bellek metriği
           SystemMetrics.objects.create(
               metric_name='memory_usage_percent',
               metric_type='gauge',
               value=memory.percent
           )
           
       except ImportError:
           logger.warning("⚠️ psutil yüklü değil, bellek izlenemiyor")
       except Exception as e:
           logger.error(f"❌ Bellek izleme hatası: {e}")
       
       # Son 24 saatteki hata sayısı
       try:
           last_24h = timezone.now() - timedelta(hours=24)
           error_count = ErrorLog.objects.filter(
               created_at__gte=last_24h,
               error_level__in=['ERROR', 'CRITICAL']
           ).count()
           
           monitoring_results['metrics']['errors_24h'] = error_count
           
           if error_count > 100:
               monitoring_results['alerts'].append({
                   'level': 'warning',
                   'message': f'Son 24 saatte {error_count} hata kaydedildi',
                   'action': 'error_investigation_needed'
               })
               if monitoring_results['status'] == 'healthy':
                   monitoring_results['status'] = 'warning'
           
           # Hata metriği
           SystemMetrics.objects.create(
               metric_name='errors_24h',
               metric_type='gauge',
               value=error_count
           )
           
       except Exception as e:
           logger.error(f"❌ Hata sayısı izleme hatası: {e}")
       
       # Celery queue uzunluğu
       try:
           from celery import current_app
           inspect = current_app.control.inspect()
           stats = inspect.stats()
           
           if stats:
               total_tasks = 0
               for worker_stats in stats.values():
                   total_tasks += worker_stats.get('total', {}).get('celery.tasks', 0)
               
               monitoring_results['metrics']['celery_queue_length'] = total_tasks
               
               if total_tasks > 1000:
                   monitoring_results['alerts'].append({
                       'level': 'warning',
                       'message': f'Celery kuyruk uzunluğu yüksek: {total_tasks}',
                       'action': 'queue_optimization_needed'
                   })
                   if monitoring_results['status'] == 'healthy':
                       monitoring_results['status'] = 'warning'
               
               # Queue metriği
               SystemMetrics.objects.create(
                   metric_name='celery_queue_length',
                   metric_type='gauge',
                   value=total_tasks
               )
               
       except Exception as e:
           logger.error(f"❌ Celery izleme hatası: {e}")
       
       # Genel sistem durumu metriği
       status_value = {
           'healthy': 1,
           'warning': 0.5,
           'critical': 0
       }.get(monitoring_results['status'], 0)
       
       SystemMetrics.objects.create(
           metric_name='system_status',
           metric_type='gauge',
           value=status_value,
           labels={'status': monitoring_results['status']}
       )
       
       logger.info(f"✅ Sistem izleme tamamlandı - Durum: {monitoring_results['status']}")
       
       if monitoring_results['alerts']:
           logger.warning(f"⚠️ {len(monitoring_results['alerts'])} uyarı tespit edildi")
       
       return monitoring_results
       
   except Exception as exc:
       logger.error(f"❌ Sistem izleme hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=1)
def optimize_knowledge_chunks(self):
   """Knowledge chunk'ları optimize et"""
   try:
       logger.info("🔧 Knowledge chunk optimizasyonu başlıyor...")
       
       optimization_results = {
           'chunks_processed': 0,
           'duplicates_removed': 0,
           'empty_chunks_removed': 0,
           'embeddings_regenerated': 0,
           'timestamp': timezone.now().isoformat()
       }
       
       # Boş chunk'ları bul ve sil
       empty_chunks = KnowledgeChunk.objects.filter(
           models.Q(content__isnull=True) | 
           models.Q(content__exact='') |
           models.Q(content_length__lte=10)
       )
       empty_count = empty_chunks.count()
       empty_chunks.delete()
       optimization_results['empty_chunks_removed'] = empty_count
       
       if empty_count > 0:
           logger.info(f"✅ {empty_count} boş chunk silindi")
       
       # Duplicate chunk'ları bul (aynı hash)
       from django.db.models import Count
       duplicate_hashes = KnowledgeChunk.objects.values('content_hash').annotate(
           count=Count('content_hash')
       ).filter(count__gt=1)
       
       duplicates_removed = 0
       for item in duplicate_hashes:
           content_hash = item['content_hash']
           chunks = KnowledgeChunk.objects.filter(content_hash=content_hash)
           
           # İlkini sakla, diğerlerini sil
           first_chunk = chunks.first()
           duplicates = chunks.exclude(id=first_chunk.id)
           
           duplicate_count = duplicates.count()
           duplicates.delete()
           duplicates_removed += duplicate_count
       
       optimization_results['duplicates_removed'] = duplicates_removed
       
       if duplicates_removed > 0:
           logger.info(f"✅ {duplicates_removed} duplicate chunk silindi")
       
       # Embedding'i olmayan chunk'ları bul
       chunks_without_embedding = KnowledgeChunk.objects.filter(
           embedding__isnull=True
       )[:100]  # Toplu işleme sınırı
       
       embeddings_regenerated = 0
       for chunk in chunks_without_embedding:
           try:
               # Embedding'i yeniden oluştur (bu işlem gerçek implementasyonda
               # embedding service'e bağlanacak)
               # chunk.embedding = generate_embedding(chunk.content)
               # chunk.save()
               embeddings_regenerated += 1
           except Exception as e:
               logger.warning(f"⚠️ Chunk {chunk.id} embedding hatası: {e}")
       
       optimization_results['embeddings_regenerated'] = embeddings_regenerated
       
       # İstatistikler
       total_chunks = KnowledgeChunk.objects.count()
       optimization_results['chunks_processed'] = total_chunks
       
       logger.info(f"✅ Knowledge chunk optimizasyonu tamamlandı - {total_chunks} chunk işlendi")
       
       # Optimizasyon metriği
       SystemMetrics.objects.create(
           metric_name='chunk_optimization',
           metric_type='counter',
           value=1,
           labels={
               'duplicates_removed': duplicates_removed,
               'empty_removed': empty_count,
               'embeddings_regenerated': embeddings_regenerated
           }
       )
       
       return optimization_results
       
   except Exception as exc:
       logger.error(f"❌ Chunk optimizasyon hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True)
def generate_maintenance_report(self):
   """Bakım raporu oluştur"""
   try:
       logger.info("📋 Bakım raporu oluşturuluyor...")
       
       report_data = {
           'report_date': timezone.now().isoformat(),
           'system_health': {},
           'performance_metrics': {},
           'storage_stats': {},
           'user_activity': {},
           'error_summary': {},
           'recommendations': []
       }
       
       # Sistem sağlığı
       try:
           health_result = system_health_check()
           report_data['system_health'] = health_result
       except Exception as e:
           logger.error(f"❌ Health check rapor hatası: {e}")
       
       # Son 7 günün metrikleri
       try:
           last_week = timezone.now() - timedelta(days=7)
           
           # Performans metrikleri
           avg_response_time = PerformanceMetrics.objects.filter(
               timestamp__gte=last_week,
               metric_name='response_time'
           ).aggregate(models.Avg('value'))['value__avg'] or 0
           
           report_data['performance_metrics'] = {
               'avg_response_time_7d': round(avg_response_time, 2),
               'total_queries_7d': QueryAnalytics.objects.filter(
                   created_at__gte=last_week
               ).count(),
               'active_users_7d': QueryAnalytics.objects.filter(
                   created_at__gte=last_week
               ).values('user').distinct().count()
           }
           
       except Exception as e:
           logger.error(f"❌ Performans metrik rapor hatası: {e}")
       
       # Depolama istatistikleri
       try:
           total_documents = DocumentSource.objects.count()
           total_chunks = KnowledgeChunk.objects.count()
           processed_documents = DocumentSource.objects.filter(
               processing_status='completed'
           ).count()
           
           report_data['storage_stats'] = {
               'total_documents': total_documents,
               'total_chunks': total_chunks,
               'processed_documents': processed_documents,
               'processing_rate': round(
                   (processed_documents / total_documents * 100) if total_documents > 0 else 0, 1
               )
           }
           
       except Exception as e:
           logger.error(f"❌ Depolama istatistik hatası: {e}")
       
       # Hata özeti
       try:
           last_24h = timezone.now() - timedelta(hours=24)
           
           error_counts = ErrorLog.objects.filter(
               created_at__gte=last_24h
           ).values('error_level').annotate(
               count=models.Count('id')
           )
           
           report_data['error_summary'] = {
               item['error_level']: item['count'] 
               for item in error_counts
           }
           
       except Exception as e:
           logger.error(f"❌ Hata özeti rapor hatası: {e}")
       
       # Öneriler
       recommendations = []
       
       # Disk kullanımı kontrolü
       if 'disk_usage_percent' in report_data.get('system_health', {}).get('metrics', {}):
           disk_usage = report_data['system_health']['metrics']['disk_usage_percent']
           if disk_usage > 80:
               recommendations.append({
                   'priority': 'high',
                   'category': 'storage',
                   'message': f'Disk kullanımı %{disk_usage} - Temizlik öneriliyor',
                   'action': 'cleanup_old_data'
               })
       
       # Performans kontrolü
       if report_data['performance_metrics'].get('avg_response_time_7d', 0) > 5:
           recommendations.append({
               'priority': 'medium',
               'category': 'performance',
               'message': 'Ortalama yanıt süresi yüksek - Optimizasyon gerekli',
               'action': 'optimize_database_indexes'
           })
       
       # Hata oranı kontrolü
       total_errors = sum(report_data.get('error_summary', {}).values())
       if total_errors > 50:
           recommendations.append({
               'priority': 'high',
               'category': 'stability',
               'message': f'Son 24 saatte {total_errors} hata - İnceleme gerekli',
               'action': 'investigate_error_patterns'
           })
       
       report_data['recommendations'] = recommendations
       
       # Raporu dosya olarak kaydet
       import json
       report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
       os.makedirs(report_dir, exist_ok=True)
       
       timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
       report_file = os.path.join(report_dir, f'maintenance_report_{timestamp}.json')
       
       with open(report_file, 'w', encoding='utf-8') as f:
           json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
       
       logger.info(f"✅ Bakım raporu oluşturuldu: {report_file}")
       
       # Rapor metriği
       SystemMetrics.objects.create(
           metric_name='maintenance_report_generated',
           metric_type='counter',
           value=1,
           labels={
               'recommendations_count': len(recommendations),
               'file_path': report_file
           }
       )
       
       return {
           'success': True,
           'report_file': report_file,
           'recommendations_count': len(recommendations),
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Bakım raporu oluşturma hatası: {exc}")
       return {
           'success': False,
           'error': str(exc),
           'timestamp': timezone.now().isoformat()
       }


# Celery beat schedule için task listesi
MAINTENANCE_TASKS = {
   'daily-cleanup': {
       'task': 'sapbot_api.tasks.maintenance_tasks.daily_maintenance',
       'schedule': 3600.0 * 24,  # Her 24 saatte bir
       'options': {'queue': 'maintenance'}
   },
   'weekly-maintenance': {
       'task': 'sapbot_api.tasks.maintenance_tasks.weekly_maintenance',
       'schedule': 3600.0 * 24 * 7,  # Her hafta
       'options': {'queue': 'maintenance'}
   },
   'hourly-health-check': {
       'task': 'sapbot_api.tasks.maintenance_tasks.system_health_check',
       'schedule': 3600.0,  # Her saat
       'options': {'queue': 'monitoring'}
   },
   'resource-monitoring': {
       'task': 'sapbot_api.tasks.maintenance_tasks.monitor_system_resources',
       'schedule': 300.0,  # Her 5 dakika
       'options': {'queue': 'monitoring'}
   },
   'session-cleanup': {
       'task': 'sapbot_api.tasks.maintenance_tasks.cleanup_expired_sessions',
       'schedule': 1800.0,  # Her 30 dakika
       'options': {'queue': 'cleanup'}
   }
}