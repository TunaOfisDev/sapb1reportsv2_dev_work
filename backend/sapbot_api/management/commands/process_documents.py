# backend/sapbot_api/management/commands/process_documents.py
"""
SAPBot API Document Processing Management Command
Dökümanları toplu olarak işleme, embedding oluşturma ve optimize etme
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import models
from datetime import timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
# SAPBot models
from sapbot_api.models import DocumentSource, KnowledgeChunk, ErrorLog
from sapbot_api.services.document_processor import DocumentProcessor
from sapbot_api.services.embedding_service import EmbeddingService
from sapbot_api.utils.file_handlers import FileValidator, PDFProcessor, VideoProcessor
from sapbot_api.utils.text_processing import TextAnalyzer, TextChunker
from sapbot_api.utils.exceptions import DocumentProcessingError
from sapbot_api.utils.helpers import format_file_size
from sapbot_api.tasks.document_tasks import process_document_async

logger = logging.getLogger('sapbot_api.management')

class Command(BaseCommand):
    """
    SAPBot döküman işleme komutu
    
    Usage examples:
    python manage.py process_documents --status pending --limit 10
    python manage.py process_documents --reprocess --document-id abc123
    python manage.py process_documents --batch --workers 4
    python manage.py process_documents --cleanup --days 7
    python manage.py process_documents --rebuild-embeddings --force
    """
    
    help = 'SAPBot dökümanları işler, embedding oluşturur ve optimize eder'
    
    def add_arguments(self, parser):
        """Command line arguments"""
        parser.add_argument(
            '--status',
            type=str,
            choices=['pending', 'processing', 'completed', 'failed', 'all'],
            default='pending',
            help='İşlenecek döküman durumu'
        )
        
        parser.add_argument(
            '--document-id',
            type=str,
            default=None,
            help='Belirli bir dökümanı işle (UUID)'
        )
        
        parser.add_argument(
            '--document-type',
            type=str,
            choices=['pdf', 'video', 'manual', 'api', 'web', 'all'],
            default='all',
            help='İşlenecek döküman tipi'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='İşlenecek maksimum döküman sayısı'
        )
        
        parser.add_argument(
            '--batch',
            action='store_true',
            help='Batch mode - birden fazla dökümanı paralel işle'
        )
        
        parser.add_argument(
            '--workers',
            type=int,
            default=2,
            help='Paralel worker sayısı (batch mode için)'
        )
        
        parser.add_argument(
            '--reprocess',
            action='store_true',
            help='Daha önce işlenmiş dökümanları yeniden işle'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Hataları görmezden gel ve işlemeye devam et'
        )
        
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Eski ve bozuk döküman kayıtlarını temizle'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Cleanup için gün sayısı (default: 30)'
        )
        
        parser.add_argument(
            '--rebuild-embeddings',
            action='store_true',
            help='Tüm embedding\'leri yeniden oluştur'
        )
        
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Metin chunk boyutu'
        )
        
        parser.add_argument(
            '--chunk-overlap',
            type=int,
            default=200,
            help='Chunk overlap boyutu'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Sadece analiz yap, işleme yapma'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Detaylı log çıktısı'
        )
        
        parser.add_argument(
            '--async-mode',
            action='store_true',
            help='Celery task\'lar ile asenkron işleme'
        )
        
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='Döküman optimizasyonu yap (duplicate removal, etc.)'
        )
    
    def handle(self, *args, **options):
        """Ana işleme metodu"""
        try:
            # Başlangıç mesajı
            self.stdout.write(
                self.style.HTTP_INFO(f"🚀 SAPBot Document Processing başlatılıyor...")
            )
            
            # Options validation
            self._validate_options(options)
            
            # Initialize services
            self.document_processor = DocumentProcessor()
            self.embedding_service = EmbeddingService()
            self.file_validator = FileValidator()
            
            # Performance tracking
            start_time = time.time()
            
            # Ana işlem seçimi
            if options['cleanup']:
                result = self._perform_cleanup(options)
            elif options['rebuild_embeddings']:
                result = self._rebuild_embeddings(options)
            elif options['optimize']:
                result = self._optimize_documents(options)
            else:
                result = self._process_documents(options)
            
            # Sonuç raporu
            end_time = time.time()
            duration = end_time - start_time
            self._display_results(result, duration, options)
            
        except Exception as e:
            logger.error(f"Document processing hatası: {e}")
            raise CommandError(f"İşlem başarısız: {str(e)}")
    
    def _validate_options(self, options):
        """Options doğrulama"""
        # Worker count validation
        if options['workers'] < 1 or options['workers'] > 10:
            raise CommandError("Worker sayısı 1-10 arasında olmalıdır")
        
        # Chunk size validation
        if options['chunk_size'] < 100 or options['chunk_size'] > 5000:
            raise CommandError("Chunk size 100-5000 arasında olmalıdır")
        
        # Document ID validation
        if options['document_id']:
            try:
                from uuid import UUID
                UUID(options['document_id'])
            except ValueError:
                raise CommandError("Geçersiz document ID formatı")
        
        # Conflicting options check
        if options['cleanup'] and options['rebuild_embeddings']:
            raise CommandError("Cleanup ve rebuild-embeddings aynı anda kullanılamaz")
    
    def _process_documents(self, options):
        """Ana döküman işleme"""
        # Documents queryset oluştur
        queryset = self._build_documents_queryset(options)
        
        if options['dry_run']:
            return self._perform_dry_run(queryset, options)
        
        # Processing mode seçimi
        if options['async_mode']:
            return self._process_documents_async(queryset, options)
        elif options['batch']:
            return self._process_documents_batch(queryset, options)
        else:
            return self._process_documents_sequential(queryset, options)
    
    def _build_documents_queryset(self, options):
        """İşlenecek dökümanların queryset'ini oluştur"""
        queryset = DocumentSource.objects.all()
        
        # Status filtering
        if options['status'] != 'all':
            if options['reprocess'] and options['status'] == 'pending':
                # Reprocess mode'da completed ve failed olanları da al
                queryset = queryset.filter(
                    processing_status__in=['pending', 'completed', 'failed']
                )
            else:
                queryset = queryset.filter(processing_status=options['status'])
        
        # Document type filtering
        if options['document_type'] != 'all':
            queryset = queryset.filter(document_type=options['document_type'])
        
        # Specific document
        if options['document_id']:
            queryset = queryset.filter(id=options['document_id'])
        
        # Ordering
        queryset = queryset.order_by('created_at')
        
        # Limit
        if options['limit']:
            queryset = queryset[:options['limit']]
        
        return queryset.select_related('uploaded_by')
    
    def _perform_dry_run(self, queryset, options):
        """Dry run - analiz yap"""
        self.stdout.write(self.style.WARNING("🔍 DRY RUN - Sadece analiz yapılıyor..."))
        
        total_docs = queryset.count()
        
        # Status breakdown
        status_breakdown = {}
        for status in ['pending', 'processing', 'completed', 'failed']:
            count = queryset.filter(processing_status=status).count()
            if count > 0:
                status_breakdown[status] = count
        
        # Type breakdown
        type_breakdown = {}
        for doc_type in ['pdf', 'video', 'manual', 'api', 'web']:
            count = queryset.filter(document_type=doc_type).count()
            if count > 0:
                type_breakdown[doc_type] = count
        
        # Size analysis
        total_size = 0
        size_breakdown = {'small': 0, 'medium': 0, 'large': 0}
        
        for doc in queryset:
            if doc.file_size:
                total_size += doc.file_size
                size_mb = doc.file_size / (1024 * 1024)
                if size_mb < 10:
                    size_breakdown['small'] += 1
                elif size_mb < 50:
                    size_breakdown['medium'] += 1
                else:
                    size_breakdown['large'] += 1
        
        # Chunk estimation
        estimated_chunks = 0
        for doc in queryset[:100]:  # Sample ilk 100 döküman
            if doc.document_type == 'pdf' and doc.file_size:
                # PDF için page estimate
                estimated_pages = max(1, doc.file_size // (1024 * 50))  # ~50KB per page
                estimated_chunks += estimated_pages * 2  # ~2 chunk per page
            elif doc.document_type == 'manual' and hasattr(doc, 'content'):
                # Manual content için estimate
                content_length = len(getattr(doc, 'content', ''))
                estimated_chunks += max(1, content_length // options['chunk_size'])
        
        # Results
        self.stdout.write(f"\n📊 İşleme Analizi:")
        self.stdout.write(f"  • Toplam döküman: {total_docs:,}")
        self.stdout.write(f"  • Toplam boyut: {format_file_size(total_size)}")
        
        if status_breakdown:
            self.stdout.write(f"\n📈 Status Dağılımı:")
            for status, count in status_breakdown.items():
                self.stdout.write(f"  • {status}: {count:,}")
        
        if type_breakdown:
            self.stdout.write(f"\n📄 Tip Dağılımı:")
            for doc_type, count in type_breakdown.items():
                self.stdout.write(f"  • {doc_type}: {count:,}")
        
        if any(size_breakdown.values()):
            self.stdout.write(f"\n💾 Boyut Dağılımı:")
            self.stdout.write(f"  • Küçük (<10MB): {size_breakdown['small']:,}")
            self.stdout.write(f"  • Orta (10-50MB): {size_breakdown['medium']:,}")
            self.stdout.write(f"  • Büyük (>50MB): {size_breakdown['large']:,}")
        
        self.stdout.write(f"\n🧩 Tahmini chunk sayısı: {estimated_chunks:,}")
        
        # Processing time estimation
        if options['batch']:
            estimated_time = total_docs * 30 / options['workers']  # 30 sec per doc per worker
        else:
            estimated_time = total_docs * 45  # 45 sec per doc sequential
        
        self.stdout.write(f"⏱️ Tahmini işlem süresi: {estimated_time/60:.1f} dakika")
        
        return {
            'total_documents': total_docs,
            'status_breakdown': status_breakdown,
            'type_breakdown': type_breakdown,
            'size_breakdown': size_breakdown,
            'estimated_chunks': estimated_chunks,
            'estimated_time': estimated_time,
            'dry_run': True
        }
    
    def _process_documents_sequential(self, queryset, options):
        """Sıralı döküman işleme"""
        total_docs = queryset.count()
        processed = 0
        succeeded = 0
        failed = 0
        chunks_created = 0
        errors = []
        
        self.stdout.write(f"📄 {total_docs} döküman sıralı işleniyor...")
        
        for i, document in enumerate(queryset, 1):
            try:
                if options['verbose']:
                    self.stdout.write(f"  [{i}/{total_docs}] İşleniyor: {document.title}")
                
                # Process document
                result = self._process_single_document(document, options)
                
                if result['success']:
                    succeeded += 1
                    chunks_created += result.get('chunks_created', 0)
                    if options['verbose']:
                        self.stdout.write(
                            self.style.SUCCESS(f"    ✅ Başarılı: {result.get('chunks_created', 0)} chunk")
                        )
                else:
                    failed += 1
                    errors.append({
                        'document': document.title,
                        'error': result.get('error', 'Unknown error')
                    })
                    if options['verbose']:
                        self.stdout.write(
                            self.style.ERROR(f"    ❌ Başarısız: {result.get('error', '')}")
                        )
                
                processed += 1
                
                # Progress indicator
                if not options['verbose'] and i % 10 == 0:
                    progress = (i / total_docs) * 100
                    self.stdout.write(f"  İlerleme: {progress:.1f}% ({i}/{total_docs})")
                
            except Exception as e:
                failed += 1
                error_msg = str(e)
                errors.append({
                    'document': document.title,
                    'error': error_msg
                })
                
                if not options['force']:
                    logger.error(f"Document processing hatası: {e}")
                    break
                
                if options['verbose']:
                    self.stdout.write(
                        self.style.ERROR(f"    ❌ Hata: {error_msg}")
                    )
        
        return {
            'total_documents': total_docs,
            'processed': processed,
            'succeeded': succeeded,
            'failed': failed,
            'chunks_created': chunks_created,
            'errors': errors,
            'mode': 'sequential'
        }
    
    def _process_documents_batch(self, queryset, options):
        """Paralel batch döküman işleme"""
        total_docs = queryset.count()
        workers = options['workers']
        
        self.stdout.write(f"⚡ {total_docs} döküman {workers} worker ile paralel işleniyor...")
        
        processed = 0
        succeeded = 0
        failed = 0
        chunks_created = 0
        errors = []
        
        # ThreadPoolExecutor ile paralel işleme
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all documents
            future_to_doc = {
                executor.submit(self._process_single_document, doc, options): doc
                for doc in queryset
            }
            
            # Process results as they complete
            for i, future in enumerate(as_completed(future_to_doc), 1):
                document = future_to_doc[future]
                
                try:
                    result = future.result()
                    
                    if result['success']:
                        succeeded += 1
                        chunks_created += result.get('chunks_created', 0)
                        if options['verbose']:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  [{i}/{total_docs}] ✅ {document.title}: {result.get('chunks_created', 0)} chunk"
                                )
                            )
                    else:
                        failed += 1
                        errors.append({
                            'document': document.title,
                            'error': result.get('error', 'Unknown error')
                        })
                        if options['verbose']:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"  [{i}/{total_docs}] ❌ {document.title}: {result.get('error', '')}"
                                )
                            )
                    
                    processed += 1
                    
                    # Progress indicator
                    if not options['verbose'] and i % 10 == 0:
                        progress = (i / total_docs) * 100
                        self.stdout.write(f"  İlerleme: {progress:.1f}% ({i}/{total_docs})")
                
                except Exception as e:
                    failed += 1
                    error_msg = str(e)
                    errors.append({
                        'document': document.title,
                        'error': error_msg
                    })
                    
                    if options['verbose']:
                        self.stdout.write(
                            self.style.ERROR(f"  [{i}/{total_docs}] ❌ {document.title}: {error_msg}")
                        )
        
        return {
            'total_documents': total_docs,
            'processed': processed,
            'succeeded': succeeded,
            'failed': failed,
            'chunks_created': chunks_created,
            'errors': errors,
            'mode': f'batch (workers: {workers})'
        }
    
    def _process_documents_async(self, queryset, options):
        """Asenkron Celery task ile işleme"""
        total_docs = queryset.count()
        
        self.stdout.write(f"🔄 {total_docs} döküman Celery task ile asenkron işleniyor...")
        
        task_ids = []
        
        # Submit tasks
        for document in queryset:
            task = process_document_async.delay(
                document.id,
                chunk_size=options['chunk_size'],
                chunk_overlap=options['chunk_overlap'],
                force_reprocess=options['reprocess']
            )
            task_ids.append(task.id)
            
            if options['verbose']:
                self.stdout.write(f"  📤 Task submitted: {document.title} (task_id: {task.id})")
        
        self.stdout.write(f"✅ {len(task_ids)} task Celery kuyruğuna gönderildi")
        self.stdout.write(f"🔍 Task durumunu şu komutla takip edebilirsiniz:")
        self.stdout.write(f"   celery -A sapreports inspect active")
        
        return {
            'total_documents': total_docs,
            'tasks_submitted': len(task_ids),
            'task_ids': task_ids,
            'mode': 'async (Celery)'
        }
    
    def _process_single_document(self, document, options):
        """Tek dökümanı işle"""
        try:
            # Status update
            document.processing_status = 'processing'
            document.save(update_fields=['processing_status'])
            
            # Document type'a göre işleme
            if document.document_type == 'pdf':
                result = self._process_pdf_document(document, options)
            elif document.document_type == 'video':
                result = self._process_video_document(document, options)
            elif document.document_type == 'manual':
                result = self._process_manual_document(document, options)
            else:
                raise DocumentProcessingError(f"Desteklenmeyen döküman tipi: {document.document_type}")
            
            # Success update
            document.processing_status = 'completed'
            document.processed_at = timezone.now()
            document.processing_error = None
            document.save(update_fields=['processing_status', 'processed_at', 'processing_error'])
            
            return {
                'success': True,
                'chunks_created': result.get('chunks_created', 0),
                'processing_time': result.get('processing_time', 0)
            }
            
        except Exception as e:
            # Error update
            error_msg = str(e)
            document.processing_status = 'failed'
            document.processing_error = error_msg
            document.save(update_fields=['processing_status', 'processing_error'])
            
            # Error log
            ErrorLog.objects.create(
                error_type='document_processing_error',
                error_level='high',
                error_message=error_msg,
                context={
                    'document_id': str(document.id),
                    'document_title': document.title,
                    'document_type': document.document_type,
                }
            )
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def _process_pdf_document(self, document, options):
        """PDF döküman işleme"""
        if not document.file_path:
            raise DocumentProcessingError("PDF dosya yolu bulunamadı")
        
        start_time = time.time()
        
        # PDF processor ile metin çıkar
        pdf_processor = PDFProcessor()
        file_path = document.file_path.path
        
        extract_result = pdf_processor.extract_text(file_path)
        
        # Text chunking
        text_chunker = TextChunker()
        chunks_created = 0
        
        for page_data in extract_result['text_content']:
            page_text = page_data['text']
            page_number = page_data['page_number']
            
            if not page_text.strip():
                continue
            
            # Chunk'lara böl
            chunks = text_chunker.intelligent_split(
                page_text,
                max_chunk_size=options['chunk_size'],
                overlap=options['chunk_overlap'],
                preserve_paragraphs=True
            )
            
            # Chunk'ları kaydet
            for chunk in chunks:
                # Text analysis
                analysis = TextAnalyzer.analyze_text(chunk.text)
                
                # Embedding generate
                embedding = self.embedding_service.generate_embedding(chunk.text)
                
                # Knowledge chunk oluştur
                knowledge_chunk = KnowledgeChunk.objects.create(
                    source=document,
                    content=chunk.text,
                    content_length=chunk.char_count,
                    embedding=embedding,
                    embedding_model=self.embedding_service.model_name,
                    page_number=page_number,
                    sap_module=analysis.sap_modules[0] if analysis.sap_modules else None,
                    technical_level=analysis.technical_level,
                    keywords=analysis.keywords,
                    relevance_score=1.0,
                )
                
                chunks_created += 1
        
        processing_time = time.time() - start_time
        
        return {
            'chunks_created': chunks_created,
            'processing_time': processing_time,
            'pages_processed': len(extract_result['text_content'])
        }
    
    def _process_video_document(self, document, options):
        """Video döküman işleme"""
        if not document.file_path:
            raise DocumentProcessingError("Video dosya yolu bulunamadı")
        
        start_time = time.time()
        
        # Video processor ile transkript çıkar
        video_processor = VideoProcessor()
        file_path = document.file_path.path
        
        transcript_result = video_processor.extract_transcript(file_path)
        
        # Text chunking
        text_chunker = TextChunker()
        chunks_created = 0
        
        full_text = transcript_result['full_text']
        
        if full_text.strip():
            # Chunk'lara böl
            chunks = text_chunker.intelligent_split(
                full_text,
                max_chunk_size=options['chunk_size'],
                overlap=options['chunk_overlap'],
                preserve_sentences=True
            )
            
            # Chunk'ları kaydet
            for chunk in chunks:
                # Text analysis
                analysis = TextAnalyzer.analyze_text(chunk.text)
                
                # Embedding generate
                embedding = self.embedding_service.generate_embedding(chunk.text)
                
                # Knowledge chunk oluştur
                knowledge_chunk = KnowledgeChunk.objects.create(
                    source=document,
                    content=chunk.text,
                    content_length=chunk.char_count,
                    embedding=embedding,
                    embedding_model=self.embedding_service.model_name,
                    sap_module=analysis.sap_modules[0] if analysis.sap_modules else None,
                    technical_level=analysis.technical_level,
                    keywords=analysis.keywords,
                    relevance_score=1.0,
                )
                
                chunks_created += 1
        
        processing_time = time.time() - start_time
        
        return {
            'chunks_created': chunks_created,
            'processing_time': processing_time,
            'video_duration': transcript_result['duration']
        }
    
    def _process_manual_document(self, document, options):
        """Manuel döküman işleme"""
        # Manuel dökümanlar için content field'ı olmalı
        if not hasattr(document, 'content') or not document.content:
            raise DocumentProcessingError("Manuel döküman içeriği bulunamadı")
        
        start_time = time.time()
        
        # Text chunking
        text_chunker = TextChunker()
        chunks_created = 0
        
        content = document.content
        
        # Chunk'lara böl
        chunks = text_chunker.intelligent_split(
            content,
            max_chunk_size=options['chunk_size'],
            overlap=options['chunk_overlap'],
            preserve_paragraphs=True
        )
        
        # Chunk'ları kaydet
        for chunk in chunks:
            # Text analysis
            analysis = TextAnalyzer.analyze_text(chunk.text)
            
            # Embedding generate
            embedding = self.embedding_service.generate_embedding(chunk.text)
            
            # Knowledge chunk oluştur
            knowledge_chunk = KnowledgeChunk.objects.create(
                source=document,
                content=chunk.text,
                content_length=chunk.char_count,
                embedding=embedding,
                embedding_model=self.embedding_service.model_name,
                sap_module=analysis.sap_modules[0] if analysis.sap_modules else None,
                technical_level=analysis.technical_level,
                keywords=analysis.keywords,
                relevance_score=1.0,
            )
            
            chunks_created += 1
        
        processing_time = time.time() - start_time
        
        return {
            'chunks_created': chunks_created,
            'processing_time': processing_time,
            'content_length': len(content)
        }
    
    def _perform_cleanup(self, options):
        """Eski ve bozuk dökümanları temizle"""
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"🧹 {days} günden eski dökümanlar temizleniyor...")
        
        # Failed documents
        failed_docs = DocumentSource.objects.filter(
            processing_status='failed',
            created_at__lt=cutoff_date
        )
        failed_count = failed_docs.count()
        
        # Orphaned chunks
        orphaned_chunks = KnowledgeChunk.objects.filter(
            source__isnull=True
        )
        orphaned_count = orphaned_chunks.count()
        
        # Empty documents
        empty_docs = DocumentSource.objects.filter(
            chunks__isnull=True,
            processing_status='completed',
            created_at__lt=cutoff_date
        )
        empty_count = empty_docs.count()
        
        if options['dry_run']:
            self.stdout.write(f"  📊 Temizlenecek veriler:")
            self.stdout.write(f"    • Başarısız dökümanlar: {failed_count}")
            self.stdout.write(f"    • Yetim chunk'lar: {orphaned_count}")
            self.stdout.write(f"    • Boş dökümanlar: {empty_count}")
            return {
                'failed_documents': failed_count,
                'orphaned_chunks': orphaned_count,
                'empty_documents': empty_count,
                'dry_run': True
            }
        
        # Actual cleanup
        deleted_counts = {}
        
        if failed_count > 0:
            deleted_counts['failed_documents'] = failed_docs.delete()[0]
            self.stdout.write(f"  ✅ {deleted_counts['failed_documents']} başarısız döküman silindi")
        
        if orphaned_count > 0:
            deleted_counts['orphaned_chunks'] = orphaned_chunks.delete()[0]
            self.stdout.write(f"  ✅ {deleted_counts['orphaned_chunks']} yetim chunk silindi")
        
        if empty_count > 0:
            deleted_counts['empty_documents'] = empty_docs.delete()[0]
            self.stdout.write(f"  ✅ {deleted_counts['empty_documents']} boş döküman silindi")
        
        return {
            'cleanup_completed': True,
            'deleted_counts': deleted_counts,
            'cutoff_date': cutoff_date
        }
    
    def _rebuild_embeddings(self, options):
        """Tüm embedding'leri yeniden oluştur"""
        chunks = KnowledgeChunk.objects.all()
        total_chunks = chunks.count()
        
        if options['dry_run']:
            self.stdout.write(f"  📊 {total_chunks} chunk için embedding yeniden oluşturulacak")
            return {'total_chunks': total_chunks, 'dry_run': True}
        
        self.stdout.write(f"🧠 {total_chunks} chunk için embedding yeniden oluşturuluyor...")
        updated_count = 0
        failed_count = 0
        batch_size = 50
       
        # Batch processing for better performance
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            for chunk in batch_chunks:
                try:
                    # Generate new embedding
                    new_embedding = self.embedding_service.generate_embedding(chunk.content)
                    
                    # Update chunk
                    chunk.embedding = new_embedding
                    chunk.embedding_model = self.embedding_service.model_name
                    chunk.save(update_fields=['embedding', 'embedding_model'])
                    
                    updated_count += 1
                    
                    if options['verbose']:
                        self.stdout.write(f"  ✅ Updated: {chunk.source.title} - Chunk {chunk.id}")
                
                except Exception as e:
                    failed_count += 1
                    if options['verbose']:
                        self.stdout.write(f"  ❌ Failed: {chunk.id} - {str(e)}")
                    
                    if not options['force']:
                        break
            
            # Progress update
            progress = min((i + batch_size) / total_chunks * 100, 100)
            self.stdout.write(f"  İlerleme: {progress:.1f}% ({updated_count + failed_count}/{total_chunks})")
        
        return {
            'total_chunks': total_chunks,
            'updated_count': updated_count,
            'failed_count': failed_count,
            'rebuild_completed': True
        }
    
    def _optimize_documents(self, options):
        """Döküman optimizasyonu"""
        self.stdout.write("🔧 Döküman optimizasyonu başlatılıyor...")
        
        optimizations = {}
        
        # 1. Duplicate content removal
        duplicates = self._find_duplicate_chunks()
        if duplicates and not options['dry_run']:
            removed_duplicates = self._remove_duplicate_chunks(duplicates)
            optimizations['duplicates_removed'] = removed_duplicates
        else:
            optimizations['duplicates_found'] = len(duplicates)
        
        # 2. Low quality chunk removal
        low_quality = self._find_low_quality_chunks()
        if low_quality and not options['dry_run']:
            removed_low_quality = self._remove_low_quality_chunks(low_quality)
            optimizations['low_quality_removed'] = removed_low_quality
        else:
            optimizations['low_quality_found'] = len(low_quality)
        
        # 3. Update relevance scores
        if not options['dry_run']:
            updated_relevance = self._update_relevance_scores()
            optimizations['relevance_updated'] = updated_relevance
        
        # 4. Consolidate similar chunks
        if not options['dry_run']:
            consolidated = self._consolidate_similar_chunks()
            optimizations['chunks_consolidated'] = consolidated
        
        return {
            'optimization_completed': True,
            'optimizations': optimizations,
            'dry_run': options['dry_run']
        }
    
    def _find_duplicate_chunks(self):
        """Duplicate chunk'ları bul"""
        from django.db.models import Count
        
        duplicates = KnowledgeChunk.objects.values('content_hash')\
            .annotate(count=Count('id'))\
            .filter(count__gt=1)
        
        duplicate_chunks = []
        for dup in duplicates:
            chunks = KnowledgeChunk.objects.filter(content_hash=dup['content_hash'])
            duplicate_chunks.extend(list(chunks[1:]))  # İlkini tut, diğerlerini sil
        
        return duplicate_chunks
    
    def _remove_duplicate_chunks(self, duplicates):
        """Duplicate chunk'ları sil"""
        count = 0
        for chunk in duplicates:
            chunk.delete()
            count += 1
        return count
    
    def _find_low_quality_chunks(self):
        """Düşük kaliteli chunk'ları bul"""
        # Kriterler: çok kısa, çok az kelime, tekrarlayan içerik
        low_quality = KnowledgeChunk.objects.filter(
            models.Q(content_length__lt=50) |  # 50 karakterden kısa
            models.Q(content__icontains="...") |  # Eksik içerik
            models.Q(content__regex=r'^.{1,10}$')  # Çok kısa
        )
        
        return list(low_quality)
    
    def _remove_low_quality_chunks(self, low_quality_chunks):
        """Düşük kaliteli chunk'ları sil"""
        count = 0
        for chunk in low_quality_chunks:
            chunk.delete()
            count += 1
        return count
    
    def _update_relevance_scores(self):
        """Relevance score'ları güncelle"""
        chunks = KnowledgeChunk.objects.all()
        updated_count = 0
        
        for chunk in chunks:
            # Usage count'a göre relevance hesapla
            usage_score = min(chunk.usage_count / 10.0, 1.0)  # Max 1.0
            
            # Content quality'ye göre score
            content_score = min(chunk.content_length / 1000.0, 1.0)  # Max 1.0
            
            # Combined score
            new_relevance = (usage_score * 0.6) + (content_score * 0.4)
            
            if abs(chunk.relevance_score - new_relevance) > 0.1:
                chunk.relevance_score = new_relevance
                chunk.save(update_fields=['relevance_score'])
                updated_count += 1
        
        return updated_count
    
    def _consolidate_similar_chunks(self):
        """Benzer chunk'ları birleştir"""
        # Bu işlem çok karmaşık olduğu için basit bir implementasyon
        # Gelecekte ML-based similarity detection eklenebilir
        consolidated_count = 0
        
        # Şimdilik sadece aynı source ve page'deki küçük chunk'ları birleştir
        from django.db.models import Count
        
        sources_with_multiple_chunks = DocumentSource.objects.annotate(
            chunk_count=Count('chunks')
        ).filter(chunk_count__gt=5)
        
        for source in sources_with_multiple_chunks:
            pages = source.chunks.values('page_number').distinct()
            
            for page_data in pages:
                page_number = page_data['page_number']
                if page_number is None:
                    continue
                
                page_chunks = source.chunks.filter(
                    page_number=page_number,
                    content_length__lt=200
                ).order_by('created_at')
                
                if page_chunks.count() > 2:
                    # Küçük chunk'ları birleştir
                    combined_content = '\n\n'.join([chunk.content for chunk in page_chunks])
                    
                    if len(combined_content) < 1500:  # Çok büyük olmasın
                        # Yeni birleştirilmiş chunk oluştur
                        first_chunk = page_chunks.first()
                        first_chunk.content = combined_content
                        first_chunk.content_length = len(combined_content)
                        
                        # Yeni embedding generate et
                        new_embedding = self.embedding_service.generate_embedding(combined_content)
                        first_chunk.embedding = new_embedding
                        first_chunk.save()
                        
                        # Diğer chunk'ları sil
                        page_chunks.exclude(id=first_chunk.id).delete()
                        consolidated_count += page_chunks.count() - 1
        
        return consolidated_count
    
    def _display_results(self, result, duration, options):
        """Sonuçları göster"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 İşlem Tamamlandı!"))
        self.stdout.write("="*60)
        
        # Duration
        duration_str = f"{duration:.1f} saniye"
        if duration > 60:
            duration_str = f"{duration/60:.1f} dakika"
        self.stdout.write(f"⏱️ Süre: {duration_str}")
        
        # Mode specific results
        if result.get('dry_run'):
            self.stdout.write(self.style.WARNING("\n🔍 DRY RUN - Hiçbir değişiklik yapılmadı"))
            
            if 'total_documents' in result:
                self.stdout.write(f"📄 Analiz edilen döküman: {result['total_documents']:,}")
                if 'estimated_chunks' in result:
                    self.stdout.write(f"🧩 Tahmini chunk: {result['estimated_chunks']:,}")
        
        elif result.get('cleanup_completed'):
            self.stdout.write(f"\n🧹 Cleanup Tamamlandı")
            for key, count in result.get('deleted_counts', {}).items():
                self.stdout.write(f"  • {key.replace('_', ' ').title()}: {count:,}")
        
        elif result.get('rebuild_completed'):
            self.stdout.write(f"\n🧠 Embedding Rebuild Tamamlandı")
            self.stdout.write(f"  • Güncellenen: {result.get('updated_count', 0):,}")
            self.stdout.write(f"  • Başarısız: {result.get('failed_count', 0):,}")
        
        elif result.get('optimization_completed'):
            self.stdout.write(f"\n🔧 Optimizasyon Tamamlandı")
            for key, count in result.get('optimizations', {}).items():
                self.stdout.write(f"  • {key.replace('_', ' ').title()}: {count:,}")
        
        elif result.get('mode') == 'async (Celery)':
            self.stdout.write(f"\n🔄 Asenkron İşlem Başlatıldı")
            self.stdout.write(f"  • Gönderilen task: {result.get('tasks_submitted', 0):,}")
            self.stdout.write(f"  • Task ID'ler: {len(result.get('task_ids', []))}")
        
        else:
            # Normal processing results
            self.stdout.write(f"\n📊 İşlem Sonuçları ({result.get('mode', 'unknown')})")
            
            if 'total_documents' in result:
                self.stdout.write(f"  • Toplam döküman: {result['total_documents']:,}")
            
            if 'processed' in result:
                self.stdout.write(f"  • İşlenen: {result['processed']:,}")
                success_rate = (result.get('succeeded', 0) / result['processed']) * 100 if result['processed'] > 0 else 0
                self.stdout.write(f"  • Başarılı: {result.get('succeeded', 0):,} ({success_rate:.1f}%)")
                self.stdout.write(f"  • Başarısız: {result.get('failed', 0):,}")
            
            if 'chunks_created' in result:
                self.stdout.write(f"  • Oluşturulan chunk: {result['chunks_created']:,}")
                if result['chunks_created'] > 0 and duration > 0:
                    chunks_per_sec = result['chunks_created'] / duration
                    self.stdout.write(f"  • Chunk/saniye: {chunks_per_sec:.1f}")
        
        # Errors
        if result.get('errors'):
            error_count = len(result['errors'])
            self.stdout.write(f"\n❌ Hatalar ({error_count}):")
            
            # İlk 5 hatayı göster
            for i, error in enumerate(result['errors'][:5]):
                self.stdout.write(f"  {i+1}. {error['document']}: {error['error']}")
            
            if error_count > 5:
                self.stdout.write(f"  ... ve {error_count - 5} hata daha")
        
        # Performance stats
        if 'chunks_created' in result and result['chunks_created'] > 0:
            avg_time_per_chunk = duration / result['chunks_created']
            self.stdout.write(f"\n📈 Performans")
            self.stdout.write(f"  • Chunk başına ortalama süre: {avg_time_per_chunk:.3f} saniye")
        
        # Recommendations
        self._display_recommendations(result, options)
    
    def _display_recommendations(self, result, options):
        """Öneriler göster"""
        recommendations = []
        
        # Performance recommendations
        if result.get('mode') == 'sequential' and result.get('total_documents', 0) > 10:
            recommendations.append("⚡ Büyük döküman setleri için --batch modunu kullanın")
        
        if result.get('failed', 0) > 0 and not options.get('force'):
            recommendations.append("🔧 Hataları görmezden gelmek için --force kullanın")
        
        # Optimization recommendations
        if result.get('chunks_created', 0) > 1000:
            recommendations.append("🔧 Çok sayıda chunk oluştu, --optimize ile optimizasyon yapın")
        
        # Cleanup recommendations
        if not result.get('cleanup_completed') and not options.get('cleanup'):
            recommendations.append("🧹 Periyodik temizlik için --cleanup kullanın")
        
        # Async recommendations
        if result.get('total_documents', 0) > 50 and not options.get('async_mode'):
            recommendations.append("🔄 Büyük işlemler için --async-mode kullanın")
        
        if recommendations:
            self.stdout.write(f"\n💡 Öneriler:")
            for rec in recommendations:
                self.stdout.write(f"  • {rec}")
        
        # Next steps
        self.stdout.write(f"\n📝 Sonraki Adımlar:")
        
        if result.get('chunks_created', 0) > 0:
            self.stdout.write(f"  • Test sorguları ile sistem performansını kontrol edin")
            self.stdout.write(f"  • Analytics dashboard'u ile kullanım istatistiklerini inceleyin")
        
        if result.get('failed', 0) > 0:
            self.stdout.write(f"  • Başarısız dökümanların loglarını kontrol edin")
            self.stdout.write(f"  • Problem olan dosyaları manuel olarak düzeltin")
        
        if result.get('mode') == 'async (Celery)':
            self.stdout.write(f"  • Celery worker durumunu kontrol edin")
            self.stdout.write(f"  • Task sonuçlarını bekleyin ve kontrol edin")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✨ SAPBot Document Processing tamamlandı!"))            
                        