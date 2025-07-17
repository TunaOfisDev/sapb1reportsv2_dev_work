# backend/sapbot_api/management/commands/export_data.py
"""
SAPBot API Data Export Management Command
Analitik ve sistem verilerini çeşitli formatlarda export etme
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
import logging
import zipfile
from pathlib import Path

# SAPBot models
from sapbot_api.models import (
    DocumentSource, KnowledgeChunk, ChatConversation, ChatMessage,
    QueryAnalytics, UserFeedback, UsageStatistics, PerformanceMetrics,
    ErrorLog, UserProfile, SystemConfiguration
)
from sapbot_api.utils.helpers import format_file_size, time_ago
from sapbot_api.utils.exceptions import raise_validation_error

logger = logging.getLogger('sapbot_api.management')


class Command(BaseCommand):
    """
    SAPBot veri export komutu
    
    Usage examples:
    python manage.py export_data --type analytics --format json --days 30
    python manage.py export_data --type all --format excel --output /tmp/sapbot_export/
    python manage.py export_data --type documents --compressed --email admin@tunacelik.com.tr
    """
    
    help = 'SAPBot API verilerini export eder (analytics, documents, logs, etc.)'
    
    def add_arguments(self, parser):
        """Command line arguments"""
        parser.add_argument(
            '--type',
            type=str,
            choices=['analytics', 'documents', 'chat', 'users', 'system', 'all'],
            default='analytics',
            help='Export edilecek veri tipi'
        )
        
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv', 'excel', 'sql'],
            default='json',
            help='Export format'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output klasörü (default: media/sapbot_exports/)'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Son X günün verisi (default: 30)'
        )
        
        parser.add_argument(
            '--start-date',
            type=str,
            default=None,
            help='Başlangıç tarihi (YYYY-MM-DD format)'
        )
        
        parser.add_argument(
            '--end-date',
            type=str,
            default=None,
            help='Bitiş tarihi (YYYY-MM-DD format)'
        )
        
        parser.add_argument(
            '--compressed',
            action='store_true',
            help='ZIP olarak sıkıştır'
        )
        
        parser.add_argument(
            '--include-sensitive',
            action='store_true',
            help='Hassas verileri dahil et (IP, email, etc.)'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            default=None,
            help='Export tamamlandığında email gönder'
        )
        
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Batch processing chunk size'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Sadece ne export edileceğini göster, dosya oluşturma'
        )
    
    def handle(self, *args, **options):
        """Ana export işlemi"""
        try:
            # Command başlangıç logları
            self.stdout.write(
                self.style.HTTP_INFO(f"🚀 SAPBot Data Export başlatılıyor...")
            )
            
            # Arguments validation
            self._validate_arguments(options)
            
            # Date range hesaplama
            start_date, end_date = self._calculate_date_range(options)
            
            # Export configuration
            export_config = {
                'type': options['type'],
                'format': options['format'],
                'start_date': start_date,
                'end_date': end_date,
                'include_sensitive': options['include_sensitive'],
                'chunk_size': options['chunk_size'],
                'compressed': options['compressed'],
                'dry_run': options['dry_run'],
            }
            
            # Output directory setup
            output_dir = self._setup_output_directory(options['output'])
            
            if options['dry_run']:
                self._perform_dry_run(export_config)
                return
            
            # Export işlemi
            export_result = self._perform_export(export_config, output_dir)
            
            # Post-processing
            if options['compressed']:
                export_result = self._compress_export(export_result, output_dir)
            
            # Email notification
            if options['email']:
                self._send_email_notification(options['email'], export_result)
            
            # Success message
            self._display_success_message(export_result)
            
        except Exception as e:
            logger.error(f"Export hatası: {e}")
            raise CommandError(f"Export işlemi başarısız: {str(e)}")
    
    def _validate_arguments(self, options):
        """Arguments doğrulama"""
        # Date format validation
        for date_key in ['start_date', 'end_date']:
            if options[date_key]:
                try:
                    datetime.strptime(options[date_key], '%Y-%m-%d')
                except ValueError:
                    raise CommandError(f"Geçersiz tarih formatı: {options[date_key]}. YYYY-MM-DD kullanın.")
        
        # Date range validation
        if options['start_date'] and options['end_date']:
            start = datetime.strptime(options['start_date'], '%Y-%m-%d')
            end = datetime.strptime(options['end_date'], '%Y-%m-%d')
            if start >= end:
                raise CommandError("Başlangıç tarihi bitiş tarihinden önce olmalıdır.")
        
        # Chunk size validation
        if options['chunk_size'] < 1 or options['chunk_size'] > 10000:
            raise CommandError("Chunk size 1-10000 arasında olmalıdır.")
        
        # Email validation
        if options['email']:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(options['email'])
            except ValidationError:
                raise CommandError(f"Geçersiz email adresi: {options['email']}")
    
    def _calculate_date_range(self, options):
        """Date range hesaplama"""
        if options['start_date'] and options['end_date']:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(options['end_date'], '%Y-%m-%d')
        else:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=options['days'])
        
        return start_date, end_date
    
    def _setup_output_directory(self, output_path):
        """Output klasörü hazırlama"""
        if output_path:
            output_dir = Path(output_path)
        else:
            media_root = getattr(settings, 'MEDIA_ROOT', '/tmp')
            output_dir = Path(media_root) / 'sapbot_exports'
        
        # Timestamp'li subfolder
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        output_dir = output_dir / f'export_{timestamp}'
        
        # Klasör oluştur
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write(f"📁 Output klasörü: {output_dir}")
        return output_dir
    
    def _perform_dry_run(self, config):
        """Dry run - sadece bilgi göster"""
        self.stdout.write(self.style.WARNING("🔍 DRY RUN - Sadece analiz yapılıyor..."))
        
        start_date = config['start_date']
        end_date = config['end_date']
        export_type = config['type']
        
        stats = {}
        
        if export_type in ['analytics', 'all']:
            stats['analytics'] = {
                'query_analytics': QueryAnalytics.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
                'user_feedback': UserFeedback.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
                'usage_statistics': UsageStatistics.objects.filter(
                    date__range=[start_date, end_date]
                ).count(),
                'performance_metrics': PerformanceMetrics.objects.filter(
                    timestamp__range=[start_date, end_date]
                ).count(),
            }
        
        if export_type in ['documents', 'all']:
            stats['documents'] = {
                'document_sources': DocumentSource.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
                'knowledge_chunks': KnowledgeChunk.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
            }
        
        if export_type in ['chat', 'all']:
            stats['chat'] = {
                'conversations': ChatConversation.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
                'messages': ChatMessage.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
            }
        
        if export_type in ['users', 'all']:
            stats['users'] = {
                'user_profiles': UserProfile.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
            }
        
        if export_type in ['system', 'all']:
            stats['system'] = {
                'error_logs': ErrorLog.objects.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
                'system_configs': SystemConfiguration.objects.count(),
            }
        
        # Display stats
        self.stdout.write(f"\n📊 Export edilecek veriler ({start_date.date()} - {end_date.date()}):")
        for category, items in stats.items():
            self.stdout.write(f"\n{category.upper()}:")
            for item_type, count in items.items():
                self.stdout.write(f"  • {item_type}: {count:,} kayıt")
        
        total_records = sum(sum(items.values()) for items in stats.values())
        self.stdout.write(f"\n📈 Toplam: {total_records:,} kayıt")
    
    def _perform_export(self, config, output_dir):
        """Ana export işlemi"""
        export_type = config['type']
        export_format = config['format']
        start_date = config['start_date']
        end_date = config['end_date']
        
        exported_files = []
        export_stats = {}
        
        self.stdout.write(f"📤 Export başlatılıyor: {export_type} ({export_format})")
        
        # Analytics export
        if export_type in ['analytics', 'all']:
            analytics_files = self._export_analytics(config, output_dir)
            exported_files.extend(analytics_files)
            export_stats['analytics'] = len(analytics_files)
        
        # Documents export
        if export_type in ['documents', 'all']:
            documents_files = self._export_documents(config, output_dir)
            exported_files.extend(documents_files)
            export_stats['documents'] = len(documents_files)
        
        # Chat export
        if export_type in ['chat', 'all']:
            chat_files = self._export_chat(config, output_dir)
            exported_files.extend(chat_files)
            export_stats['chat'] = len(chat_files)
        
        # Users export
        if export_type in ['users', 'all']:
            users_files = self._export_users(config, output_dir)
            exported_files.extend(users_files)
            export_stats['users'] = len(users_files)
        
        # System export
        if export_type in ['system', 'all']:
            system_files = self._export_system(config, output_dir)
            exported_files.extend(system_files)
            export_stats['system'] = len(system_files)
        
        # Export metadata
        metadata_file = self._create_export_metadata(config, output_dir, export_stats)
        exported_files.append(metadata_file)
        
        return {
            'files': exported_files,
            'output_dir': output_dir,
            'stats': export_stats,
            'total_files': len(exported_files),
            'config': config
        }
    
    def _export_analytics(self, config, output_dir):
        """Analytics verilerini export et"""
        files = []
        start_date = config['start_date']
        end_date = config['end_date']
        format_type = config['format']
        
        self.stdout.write("  📊 Analytics verileri export ediliyor...")
        
        # Query Analytics
        query_analytics = QueryAnalytics.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('user')
        
        if query_analytics.exists():
            filename = f"query_analytics.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(query_analytics, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {query_analytics.count():,} kayıt")
        
        # User Feedback
        user_feedback = UserFeedback.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('user', 'message')
        
        if user_feedback.exists():
            filename = f"user_feedback.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(user_feedback, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {user_feedback.count():,} kayıt")
        
        # Usage Statistics
        usage_stats = UsageStatistics.objects.filter(
            date__range=[start_date, end_date]
        )
        
        if usage_stats.exists():
            filename = f"usage_statistics.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(usage_stats, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {usage_stats.count():,} kayıt")
        
        return files
    
    def _export_documents(self, config, output_dir):
        """Document verilerini export et"""
        files = []
        start_date = config['start_date']
        end_date = config['end_date']
        format_type = config['format']
        
        self.stdout.write("  📄 Document verileri export ediliyor...")
        
        # Document Sources
        documents = DocumentSource.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('uploaded_by')
        
        if documents.exists():
            filename = f"document_sources.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(documents, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {documents.count():,} kayıt")
        
        # Knowledge Chunks
        chunks = KnowledgeChunk.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('source', 'verified_by')
        
        if chunks.exists():
            filename = f"knowledge_chunks.{format_type}"
            filepath = output_dir / filename
            # Embedding verilerini hariç tut (çok büyük)
            self._export_queryset_to_file(
                chunks.defer('embedding'), filepath, format_type, config
            )
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {chunks.count():,} kayıt")
        
        return files
    
    def _export_chat(self, config, output_dir):
        """Chat verilerini export et"""
        files = []
        start_date = config['start_date']
        end_date = config['end_date']
        format_type = config['format']
        
        self.stdout.write("  💬 Chat verileri export ediliyor...")
        
        # Chat Conversations
        conversations = ChatConversation.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('user')
        
        if conversations.exists():
            filename = f"chat_conversations.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(conversations, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {conversations.count():,} kayıt")
        
        # Chat Messages
        messages = ChatMessage.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('conversation__user').prefetch_related('sources_used')
        
        if messages.exists():
            filename = f"chat_messages.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(messages, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {messages.count():,} kayıt")
        
        return files
    
    def _export_users(self, config, output_dir):
        """User verilerini export et"""
        files = []
        start_date = config['start_date']
        end_date = config['end_date']
        format_type = config['format']
        
        self.stdout.write("  👤 User verileri export ediliyor...")
        
        # User Profiles
        users = UserProfile.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('user')
        
        if users.exists():
            filename = f"user_profiles.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(users, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {users.count():,} kayıt")
        
        return files
    
    def _export_system(self, config, output_dir):
        """System verilerini export et"""
        files = []
        start_date = config['start_date']
        end_date = config['end_date']
        format_type = config['format']
        
        self.stdout.write("  ⚙️ System verileri export ediliyor...")
        
        # Error Logs
        errors = ErrorLog.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('user')
        
        if errors.exists():
            filename = f"error_logs.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(errors, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {errors.count():,} kayıt")
        
        # System Configuration
        configs = SystemConfiguration.objects.all()
        
        if configs.exists():
            filename = f"system_configurations.{format_type}"
            filepath = output_dir / filename
            self._export_queryset_to_file(configs, filepath, format_type, config)
            files.append(filepath)
            self.stdout.write(f"    ✅ {filename}: {configs.count():,} kayıt")
        
        return files
    
    def _export_queryset_to_file(self, queryset, filepath, format_type, config):
        """QuerySet'i dosyaya export et"""
        include_sensitive = config['include_sensitive']
        chunk_size = config['chunk_size']
        
        if format_type == 'json':
            self._export_to_json(queryset, filepath, include_sensitive, chunk_size)
        elif format_type == 'csv':
            self._export_to_csv(queryset, filepath, include_sensitive, chunk_size)
        elif format_type == 'excel':
            self._export_to_excel(queryset, filepath, include_sensitive, chunk_size)
        elif format_type == 'sql':
            self._export_to_sql(queryset, filepath, include_sensitive, chunk_size)
    
    def _export_to_json(self, queryset, filepath, include_sensitive, chunk_size):
        """JSON export"""
        from django.core import serializers
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # JSON array başlat
            f.write('[\n')
            
            first_item = True
            for chunk in self._chunk_queryset(queryset, chunk_size):
                for obj in chunk:
                    if not first_item:
                        f.write(',\n')
                    
                    # Serialize object
                    serialized = serializers.serialize('json', [obj])
                    # JSON array wrapper'ı kaldır
                    obj_json = json.loads(serialized)[0]
                    
                    # Sensitive data filtering
                    if not include_sensitive:
                        obj_json = self._filter_sensitive_data(obj_json)
                    
                    json.dump(obj_json, f, ensure_ascii=False, indent=2)
                    first_item = False
            
            f.write('\n]')
    
    def _export_to_csv(self, queryset, filepath, include_sensitive, chunk_size):
        """CSV export"""
        if not queryset.exists():
            return
        
        # Model field'larını al
        model = queryset.model
        fields = [f.name for f in model._meta.fields]
        
        # Sensitive field'ları filtrele
        if not include_sensitive:
            sensitive_fields = ['ip_address', 'user_agent', 'email', 'password']
            fields = [f for f in fields if f not in sensitive_fields]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header yaz
            writer.writerow(fields)
            
            # Data yaz
            for chunk in self._chunk_queryset(queryset, chunk_size):
                for obj in chunk:
                    row = []
                    for field in fields:
                        value = getattr(obj, field, '')
                        # JSON field'ları string'e çevir
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                        row.append(str(value) if value is not None else '')
                    writer.writerow(row)
    
    def _export_to_excel(self, queryset, filepath, include_sensitive, chunk_size):
        """Excel export"""
        try:
            import pandas as pd
        except ImportError:
            self.stdout.write(
                self.style.WARNING("⚠️ pandas yüklü değil, CSV formatı kullanılıyor")
            )
            csv_path = filepath.with_suffix('.csv')
            self._export_to_csv(queryset, csv_path, include_sensitive, chunk_size)
            return
        
        # Django QuerySet'i pandas DataFrame'e çevir
        data = []
        for chunk in self._chunk_queryset(queryset, chunk_size):
            for obj in chunk:
                obj_dict = {}
                for field in obj._meta.fields:
                    value = getattr(obj, field.name)
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    obj_dict[field.name] = value
                
                # Sensitive data filtering
                if not include_sensitive:
                    obj_dict = self._filter_sensitive_data({'fields': obj_dict})['fields']
                
                data.append(obj_dict)
        
        if data:
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
    
    def _export_to_sql(self, queryset, filepath, include_sensitive, chunk_size):
        """SQL export"""
        from django.core.management import call_command
        from io import StringIO
        
        # Django'nun dumpdata komutunu kullan
        output = StringIO()
        model_name = f"{queryset.model._meta.app_label}.{queryset.model._meta.model_name}"
        
        # Primary key'leri al
        pks = list(queryset.values_list('pk', flat=True))
        
        if pks:
            call_command(
                'dumpdata',
                model_name,
                format='json',
                indent=2,
                pks=','.join(map(str, pks)),
                stdout=output
            )
            
            # SQL INSERT statements'e çevir
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"-- SAPBot Export: {model_name}\n")
                f.write(f"-- Generated: {timezone.now()}\n\n")
                
                # JSON'dan SQL'e conversion burada yapılabilir
                # Şimdilik JSON formatında kaydet
                f.write(output.getvalue())
    
    def _chunk_queryset(self, queryset, chunk_size):
        """QuerySet'i chunk'lara böl"""
        count = queryset.count()
        for i in range(0, count, chunk_size):
            yield queryset[i:i + chunk_size]
    
    def _filter_sensitive_data(self, obj_data):
        """Hassas verileri filtrele"""
        sensitive_fields = [
            'ip_address', 'user_agent', 'email', 'password', 
            'phone', 'address', 'last_login_ip', 'api_key'
        ]
        
        if 'fields' in obj_data:
            for field in sensitive_fields:
                if field in obj_data['fields']:
                    obj_data['fields'][field] = '[FILTERED]'
        
        return obj_data
    
    def _create_export_metadata(self, config, output_dir, export_stats):
        """Export metadata dosyası oluştur"""
        metadata = {
            'export_info': {
                'timestamp': timezone.now().isoformat(),
                'type': config['type'],
                'format': config['format'],
                'date_range': {
                    'start': config['start_date'].isoformat(),
                    'end': config['end_date'].isoformat(),
                },
                'include_sensitive': config['include_sensitive'],
                'compressed': config['compressed'],
            },
            'statistics': export_stats,
            'system_info': {
                'sapbot_version': '1.0.0',
                'django_version': settings.get('VERSION', 'unknown'),
                'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
            },
            'files_created': len(export_stats),
        }
        
        metadata_file = output_dir / 'export_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata_file
    
    def _compress_export(self, export_result, output_dir):
        """Export dosyalarını ZIP'le"""
        self.stdout.write("📦 Dosyalar sıkıştırılıyor...")
        
        zip_filename = f"sapbot_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = output_dir.parent / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in export_result['files']:
                arcname = file_path.name
                zipf.write(file_path, arcname)
        
        # Orijinal dosyaları sil
        for file_path in export_result['files']:
            file_path.unlink()
        
        # Output directory'yi sil (boşsa)
        try:
            output_dir.rmdir()
        except OSError:
            pass
        
        export_result['compressed_file'] = zip_path
        export_result['file_size'] = format_file_size(zip_path.stat().st_size)
        
        return export_result
    
    def _send_email_notification(self, email, export_result):
        """Email bildirimi gönder"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"SAPBot Export Tamamlandı - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            
            message = f"""
SAPBot veri export işlemi başarıyla tamamlandı.

Export Detayları:
- Tip: {export_result['config']['type']}
- Format: {export_result['config']['format']}
- Dosya Sayısı: {export_result['total_files']}
- Tarih Aralığı: {export_result['config']['start_date'].date()} - {export_result['config']['end_date'].date()}

Dosya Konumu: {export_result['output_dir']}

Bu otomatik bir mesajdır.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            self.stdout.write(f"📧 Email bildirimi gönderildi: {email}")
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Email gönderme hatası: {e}")
            )
    
    def _display_success_message(self, export_result):
        """Başarı mesajını göster"""
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Export başarıyla tamamlandı!")
        )
        
        self.stdout.write(f"📁 Konum: {export_result['output_dir']}")
        self.stdout.write(f"📊 Toplam dosya: {export_result['total_files']}")
        
        if 'compressed_file' in export_result:
            self.stdout.write(f"📦 Sıkıştırılmış dosya: {export_result['compressed_file']}")
            self.stdout.write(f"💾 Dosya boyutu: {export_result['file_size']}")
            
            # Export istatistikleri
            self.stdout.write(f"\n📈 Export İstatistikleri:")
            for category, file_count in export_result['stats'].items():
                self.stdout.write(f"  • {category}: {file_count} dosya")
            
            # Kullanım önerileri
            self.stdout.write(f"\n💡 Kullanım Önerileri:")
            if export_result['config']['format'] == 'json':
                self.stdout.write("  • JSON dosyalarını Python/JavaScript ile işleyebilirsiniz")
            elif export_result['config']['format'] == 'csv':
                self.stdout.write("  • CSV dosyalarını Excel veya pandas ile açabilirsiniz")
            elif export_result['config']['format'] == 'excel':
                self.stdout.write("  • Excel dosyalarını Microsoft Excel ile açabilirsiniz")
            
            if not export_result['config']['include_sensitive']:
                self.stdout.write("  • Hassas veriler filtrelenmiştir")
            
            self.stdout.write(f"\n🔍 Metadata dosyası: export_metadata.json")
            self.stdout.write(f"⏱️ İşlem süresi: {time_ago(timezone.now())}")