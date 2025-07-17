# backend/sapbot_api/management/commands/rebuild_embeddings.py
"""
SAPBot API Embedding Rebuild Management Command
Mevcut chunk'ların embedding'lerini yeniden oluşturur ve optimize eder
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Count, Avg, Sum, Max, Min
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from collections import defaultdict

# SAPBot models and services
from sapbot_api.models import (
   KnowledgeChunk, SystemConfiguration, PerformanceMetrics
)
from sapbot_api.services.embedding_service import EmbeddingService
from sapbot_api.utils.helpers import format_file_size, generate_hash
from sapbot_api.utils.cache_utils import embedding_cache
from sapbot_api.utils.text_processing import clean_text

logger = logging.getLogger('sapbot_api.management')


class Command(BaseCommand):
   """
   SAPBot embedding rebuild komutu
   
   Usage examples:
   python manage.py rebuild_embeddings --all
   python manage.py rebuild_embeddings --model-change --new-model sentence-transformers/all-MiniLM-L6-v2
   python manage.py rebuild_embeddings --chunks-without-embeddings
   python manage.py rebuild_embeddings --source-id abc123 --force
   python manage.py rebuild_embeddings --batch-size 100 --workers 4
   python manage.py rebuild_embeddings --similarity-check --threshold 0.95
   python manage.py rebuild_embeddings --optimize --remove-outliers
   """
   
   help = 'SAPBot embedding\'leri yeniden oluşturur ve optimize eder'
   
   def add_arguments(self, parser):
       """Command line arguments"""
       
       # Target selection
       parser.add_argument(
           '--all',
           action='store_true',
           help='Tüm chunk\'ların embedding\'lerini yeniden oluştur'
       )
       
       parser.add_argument(
           '--chunks-without-embeddings',
           action='store_true',
           help='Sadece embedding\'i olmayan chunk\'ları işle'
       )
       
       parser.add_argument(
           '--source-id',
           type=str,
           help='Belirli bir döküman kaynağının chunk\'larını işle'
       )
       
       parser.add_argument(
           '--chunk-ids',
           type=str,
           help='Belirli chunk ID\'lerini işle (virgülle ayrılmış)'
       )
       
       parser.add_argument(
           '--sap-module',
           type=str,
           choices=['FI', 'MM', 'SD', 'CRM', 'PROD', 'HR', 'QM', 'PM', 'CO', 'WM', 'BI', 'ADMIN', 'OTHER'],
           help='Belirli SAP modülünün chunk\'larını işle'
       )
       
       parser.add_argument(
           '--technical-level',
           type=str,
           choices=['user', 'admin', 'developer', 'mixed'],
           help='Belirli teknik seviyenin chunk\'larını işle'
       )
       
       # Model configuration
       parser.add_argument(
           '--model-change',
           action='store_true',
           help='Model değişikliği nedeniyle yeniden oluştur'
       )
       
       parser.add_argument(
           '--new-model',
           type=str,
           help='Yeni embedding model adı'
       )
       
       parser.add_argument(
           '--old-model',
           type=str,
           help='Eski model ile oluşturulan embedding\'leri bul'
       )
       
       # Processing options
       parser.add_argument(
           '--batch-size',
           type=int,
           default=50,
           help='Batch işleme boyutu (default: 50)'
       )
       
       parser.add_argument(
           '--workers',
           type=int,
           default=2,
           help='Paralel worker sayısı (default: 2)'
       )
       
       parser.add_argument(
           '--force',
           action='store_true',
           help='Mevcut embedding\'leri zorla yeniden oluştur'
       )
       
       parser.add_argument(
           '--skip-errors',
           action='store_true',
           help='Hatalı chunk\'ları atlayıp devam et'
       )
       
       # Quality and optimization
       parser.add_argument(
           '--similarity-check',
           action='store_true',
           help='Embedding similarity kontrolü yap'
       )
       
       parser.add_argument(
           '--threshold',
           type=float,
           default=0.95,
           help='Similarity threshold (default: 0.95)'
       )
       
       parser.add_argument(
           '--optimize',
           action='store_true',
           help='Embedding optimizasyonu yap'
       )
       
       parser.add_argument(
           '--remove-outliers',
           action='store_true',
           help='Outlier embedding\'leri kaldır'
       )
       
       parser.add_argument(
           '--validate-embeddings',
           action='store_true',
           help='Embedding kalitesini doğrula'
       )
       
       # Output options
       parser.add_argument(
           '--dry-run',
           action='store_true',
           help='Sadece analiz yap, değişiklik yapma'
       )
       
       parser.add_argument(
           '--verbose',
           action='store_true',
           help='Detaylı çıktı'
       )
       
       parser.add_argument(
           '--progress',
           action='store_true',
           help='Progress bar göster'
       )
       
       parser.add_argument(
           '--export-stats',
           type=str,
           help='İstatistikleri dosyaya aktar'
       )
       
       # Performance
       parser.add_argument(
           '--cache-embeddings',
           action='store_true',
           help='Embedding\'leri cache\'le'
       )
       
       parser.add_argument(
           '--clear-cache',
           action='store_true',
           help='Embedding cache\'ini temizle'
       )
   
   def handle(self, *args, **options):
       """Ana işleme metodu"""
       try:
           # Başlangıç
           self.stdout.write(
               self.style.HTTP_INFO("🧠 SAPBot Embedding Rebuild başlatılıyor...")
           )
           
           # Validation
           self._validate_options(options)
           
           # Initialize services
           self.embedding_service = EmbeddingService()
           self.stats = {
               'start_time': time.time(),
               'total_processed': 0,
               'successful': 0,
               'failed': 0,
               'skipped': 0,
               'errors': []
           }
           
           # Cache operations
           if options['clear_cache']:
               self._clear_embedding_cache()
           
           # Model değişikliği kontrolü
           if options['model_change'] and options['new_model']:
               self._update_embedding_model(options['new_model'])
           
           # Ana işlem
           if options['similarity_check']:
               result = self._perform_similarity_check(options)
           elif options['validate_embeddings']:
               result = self._validate_all_embeddings(options)
           elif options['optimize']:
               result = self._optimize_embeddings(options)
           else:
               result = self._rebuild_embeddings(options)
           
           # Sonuç raporu
           self._display_results(result, options)
           
       except Exception as e:
           logger.error(f"Embedding rebuild hatası: {e}")
           raise CommandError(f"İşlem başarısız: {str(e)}")
   
   def _validate_options(self, options):
       """Options doğrulama"""
       # Batch size validation
       if options['batch_size'] < 1 or options['batch_size'] > 500:
           raise CommandError("Batch size 1-500 arasında olmalıdır")
       
       # Worker validation
       if options['workers'] < 1 or options['workers'] > 10:
           raise CommandError("Worker sayısı 1-10 arasında olmalıdır")
       
       # Threshold validation
       if options['threshold'] < 0.0 or options['threshold'] > 1.0:
           raise CommandError("Threshold 0.0-1.0 arasında olmalıdır")
       
       # Conflicting options
       if options['all'] and options['chunks_without_embeddings']:
           raise CommandError("--all ve --chunks-without-embeddings aynı anda kullanılamaz")
       
       # Model validation
       if options['new_model'] and not options['model_change']:
           raise CommandError("--new-model için --model-change gerekli")
   
   def _rebuild_embeddings(self, options):
       """Ana embedding rebuild işlemi"""
       # Chunk queryset oluştur
       queryset = self._build_chunks_queryset(options)
       total_chunks = queryset.count()
       
       if total_chunks == 0:
           self.stdout.write(self.style.WARNING("İşlenecek chunk bulunamadı"))
           return {'total_chunks': 0}
       
       if options['dry_run']:
           return self._perform_dry_run_analysis(queryset, options)
       
       self.stdout.write(f"🔄 {total_chunks:,} chunk için embedding yeniden oluşturuluyor...")
       
       # Processing mode
       if options['workers'] > 1:
           return self._rebuild_parallel(queryset, options)
       else:
           return self._rebuild_sequential(queryset, options)
   
   def _build_chunks_queryset(self, options):
       """İşlenecek chunk'ların queryset'ini oluştur"""
       queryset = KnowledgeChunk.objects.select_related('source')
       
       # Target selection
       if options['all']:
           pass  # Tüm chunk'lar
       elif options['chunks_without_embeddings']:
           queryset = queryset.filter(embedding__isnull=True)
       elif options['source_id']:
           queryset = queryset.filter(source_id=options['source_id'])
       elif options['chunk_ids']:
           chunk_ids = [id.strip() for id in options['chunk_ids'].split(',')]
           queryset = queryset.filter(id__in=chunk_ids)
       
       # Module filtering
       if options['sap_module']:
           queryset = queryset.filter(sap_module=options['sap_module'])
       
       # Technical level filtering
       if options['technical_level']:
           queryset = queryset.filter(technical_level=options['technical_level'])
       
       # Model filtering
       if options['old_model']:
           queryset = queryset.filter(embedding_model=options['old_model'])
       
       # Force rebuild filtering
       if not options['force']:
           queryset = queryset.filter(
               Q(embedding__isnull=True) | 
               Q(embedding_model__isnull=True) |
               Q(embedding_model__ne=self.embedding_service.model_name)
           )
       
       return queryset.order_by('created_at')
   
   def _perform_dry_run_analysis(self, queryset, options):
       """Dry run analizi"""
       self.stdout.write(self.style.WARNING("🔍 DRY RUN - Analiz yapılıyor..."))
       
       total_chunks = queryset.count()
       
       # Model breakdown
       model_breakdown = queryset.values('embedding_model')\
           .annotate(count=Count('id'))\
           .order_by('-count')
       
       # Source breakdown
       source_breakdown = queryset.values('source__title')\
           .annotate(count=Count('id'))\
           .order_by('-count')[:10]
       
       # Content analysis
       content_stats = queryset.aggregate(
           avg_length=Avg('content_length'),
           min_length=Min('content_length'),
           max_length=Max('content_length'),
           total_content=Sum('content_length')
       )
       
       # Missing embeddings
       missing_embeddings = queryset.filter(embedding__isnull=True).count()
       
       # Outdated embeddings
       current_model = self.embedding_service.model_name
       outdated_embeddings = queryset.exclude(embedding_model=current_model).count()
       
       # Results
       self.stdout.write(f"\n📊 Embedding Analizi:")
       self.stdout.write(f"  • Toplam chunk: {total_chunks:,}")
       self.stdout.write(f"  • Embedding eksik: {missing_embeddings:,}")
       self.stdout.write(f"  • Eski model: {outdated_embeddings:,}")
       self.stdout.write(f"  • Mevcut model: {current_model}")
       
       if model_breakdown:
           self.stdout.write(f"\n🤖 Model Dağılımı:")
           for model_data in model_breakdown:
               model_name = model_data['embedding_model'] or 'None'
               count = model_data['count']
               self.stdout.write(f"  • {model_name}: {count:,}")
       
       if content_stats['avg_length']:
           self.stdout.write(f"\n📝 İçerik İstatistikleri:")
           self.stdout.write(f"  • Ortalama uzunluk: {content_stats['avg_length']:.0f} karakter")
           self.stdout.write(f"  • Min-Max: {content_stats['min_length']}-{content_stats['max_length']}")
           self.stdout.write(f"  • Toplam içerik: {format_file_size(content_stats['total_content'])}")
       
       # Estimation
       estimated_time = total_chunks * 0.5  # 0.5 saniye per chunk
       estimated_cost = total_chunks * 0.0001  # Tahmini API cost
       
       self.stdout.write(f"\n⏱️ Tahminler:")
       self.stdout.write(f"  • Tahmini süre: {estimated_time/60:.1f} dakika")
       self.stdout.write(f"  • Tahmini maliyet: ${estimated_cost:.4f}")
       
       return {
           'total_chunks': total_chunks,
           'missing_embeddings': missing_embeddings,
           'outdated_embeddings': outdated_embeddings,
           'model_breakdown': list(model_breakdown),
           'content_stats': content_stats,
           'estimated_time': estimated_time,
           'dry_run': True
       }
   
   def _rebuild_sequential(self, queryset, options):
       """Sıralı embedding rebuild"""
       total_chunks = queryset.count()
       batch_size = options['batch_size']
       
       self.stdout.write(f"📄 Sequential processing: {total_chunks:,} chunks")
       
       for i in range(0, total_chunks, batch_size):
           batch_chunks = list(queryset[i:i + batch_size])
           
           # Batch processing
           batch_result = self._process_embedding_batch(batch_chunks, options)
           
           # Update stats
           self.stats['total_processed'] += len(batch_chunks)
           self.stats['successful'] += batch_result['successful']
           self.stats['failed'] += batch_result['failed']
           self.stats['errors'].extend(batch_result['errors'])
           
           # Progress
           progress = min((i + batch_size) / total_chunks * 100, 100)
           if options['progress'] or options['verbose']:
               success_rate = (self.stats['successful'] / max(self.stats['total_processed'], 1)) * 100
               self.stdout.write(
                   f"  İlerleme: {progress:.1f}% "
                   f"({self.stats['total_processed']}/{total_chunks}) "
                   f"Başarı: {success_rate:.1f}%"
               )
           
           # Error handling
           if batch_result['failed'] > 0 and not options['skip_errors']:
               if batch_result['failed'] > len(batch_chunks) * 0.5:  # %50'den fazla hata
                   self.stdout.write(
                       self.style.ERROR(f"❌ Batch'te çok fazla hata! İşlem durduruluyor...")
                   )
                   break
       
       return {
           'total_chunks': total_chunks,
           'processed': self.stats['total_processed'],
           'successful': self.stats['successful'],
           'failed': self.stats['failed'],
           'errors': self.stats['errors'][:10],  # İlk 10 hata
           'mode': 'sequential'
       }
   
   def _rebuild_parallel(self, queryset, options):
       """Paralel embedding rebuild"""
       total_chunks = queryset.count()
       batch_size = options['batch_size']
       workers = options['workers']
       
       self.stdout.write(f"⚡ Parallel processing: {total_chunks:,} chunks, {workers} workers")
       
       # Batch'leri oluştur
       batches = []
       for i in range(0, total_chunks, batch_size):
           batch_chunks = list(queryset[i:i + batch_size])
           batches.append(batch_chunks)
       
       # Parallel processing
       with ThreadPoolExecutor(max_workers=workers) as executor:
           # Submit all batches
           future_to_batch = {
               executor.submit(self._process_embedding_batch, batch, options): batch
               for batch in batches
           }
           
           # Process results
           completed_batches = 0
           for future in as_completed(future_to_batch):
               batch = future_to_batch[future]
               
               try:
                   batch_result = future.result()
                   
                   # Update stats
                   self.stats['total_processed'] += len(batch)
                   self.stats['successful'] += batch_result['successful']
                   self.stats['failed'] += batch_result['failed']
                   self.stats['errors'].extend(batch_result['errors'])
                   
                   completed_batches += 1
                   
                   # Progress
                   if options['progress'] or options['verbose']:
                       progress = (completed_batches / len(batches)) * 100
                       success_rate = (self.stats['successful'] / max(self.stats['total_processed'], 1)) * 100
                       self.stdout.write(
                           f"  Batch {completed_batches}/{len(batches)} "
                           f"({progress:.1f}%) Başarı: {success_rate:.1f}%"
                       )
               
               except Exception as e:
                   self.stats['failed'] += len(batch)
                   self.stats['errors'].append(f"Batch processing error: {str(e)}")
                   
                   if not options['skip_errors']:
                       self.stdout.write(
                           self.style.ERROR(f"❌ Batch hatası: {str(e)}")
                       )
       
       return {
           'total_chunks': total_chunks,
           'processed': self.stats['total_processed'],
           'successful': self.stats['successful'],
           'failed': self.stats['failed'],
           'errors': self.stats['errors'][:10],
           'mode': f'parallel ({workers} workers)'
       }
   
   def _process_embedding_batch(self, chunks, options):
       """Bir batch chunk'ı işle"""
       successful = 0
       failed = 0
       errors = []
       
       # Batch embedding generation
       try:
           # Content'leri hazırla
           contents = []
           valid_chunks = []
           
           for chunk in chunks:
               if chunk.content and chunk.content.strip():
                   # Content temizliği
                   cleaned_content = clean_text(chunk.content)
                   if len(cleaned_content) > 10:  # Minimum length check
                       contents.append(cleaned_content)
                       valid_chunks.append(chunk)
           
           if not contents:
               return {'successful': 0, 'failed': len(chunks), 'errors': ['No valid content']}
           
           # Batch embedding generation
           embeddings = self.embedding_service.generate_batch_embeddings(contents)
           
           # Save embeddings
           for i, chunk in enumerate(valid_chunks):
               try:
                   if i < len(embeddings):
                       embedding = embeddings[i]
                       
                       # Embedding validation
                       if self._validate_embedding(embedding):
                           # Update chunk
                           chunk.embedding = embedding
                           chunk.embedding_model = self.embedding_service.model_name
                           chunk.save(update_fields=['embedding', 'embedding_model'])
                           
                           # Cache embedding
                           if options['cache_embeddings']:
                               content_hash = generate_hash(chunk.content)
                               embedding_cache.set_embedding(content_hash, embedding)
                           
                           successful += 1
                           
                           if options['verbose']:
                               self.stdout.write(f"    ✅ {chunk.id}")
                       else:
                           failed += 1
                           errors.append(f"Invalid embedding for chunk {chunk.id}")
                   else:
                       failed += 1
                       errors.append(f"No embedding generated for chunk {chunk.id}")
               
               except Exception as e:
                   failed += 1
                   error_msg = f"Chunk {chunk.id}: {str(e)}"
                   errors.append(error_msg)
                   
                   if options['verbose']:
                       self.stdout.write(f"    ❌ {error_msg}")
       
       except Exception as e:
           # Entire batch failed
           failed = len(chunks)
           errors.append(f"Batch processing failed: {str(e)}")
       
       return {
           'successful': successful,
           'failed': failed,
           'errors': errors
       }
   
   def _validate_embedding(self, embedding):
       """Embedding kalitesini doğrula"""
       if not embedding or not isinstance(embedding, list):
           return False
       
       # Dimension check
       expected_dim = getattr(self.embedding_service, 'embedding_dimension', 384)
       if len(embedding) != expected_dim:
           return False
       
       # NaN/Inf check
       try:
           arr = np.array(embedding)
           if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
               return False
       except:
           return False
       
       # Norm check (should not be zero vector)
       norm = np.linalg.norm(arr)
       if norm < 1e-6:
           return False
       
       return True
   
   def _perform_similarity_check(self, options):
       """Embedding similarity kontrolü"""
       self.stdout.write("🔍 Embedding similarity kontrolü başlatılıyor...")
       
       # Sample chunks al
       chunks = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       ).order_by('?')[:1000]  # Random 1000 chunk
       
       threshold = options['threshold']
       similar_pairs = []
       
       self.stdout.write(f"📊 {len(chunks)} chunk similarity kontrolü...")
       
       # Pairwise similarity check
       embeddings = []
       chunk_ids = []
       
       for chunk in chunks:
           if chunk.embedding:
               embeddings.append(np.array(chunk.embedding))
               chunk_ids.append(chunk.id)
       
       if len(embeddings) < 2:
           return {'similar_pairs': 0, 'message': 'Yeterli embedding bulunamadı'}
       
       embeddings = np.array(embeddings)
       
       # Cosine similarity matrix
       norms = np.linalg.norm(embeddings, axis=1)
       normalized_embeddings = embeddings / norms[:, np.newaxis]
       similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
       
       # Find similar pairs
       for i in range(len(chunk_ids)):
           for j in range(i + 1, len(chunk_ids)):
               similarity = similarity_matrix[i, j]
               if similarity >= threshold:
                   similar_pairs.append({
                       'chunk1': chunk_ids[i],
                       'chunk2': chunk_ids[j],
                       'similarity': float(similarity)
                   })
       
       # Results
       self.stdout.write(f"🎯 Similarity Sonuçları:")
       self.stdout.write(f"  • Kontrol edilen: {len(chunks):,}")
       self.stdout.write(f"  • Threshold: {threshold}")
       self.stdout.write(f"  • Benzer çiftler: {len(similar_pairs):,}")
       
       if similar_pairs and options['verbose']:
           self.stdout.write(f"  🔍 İlk 5 benzer çift:")
           for pair in similar_pairs[:5]:
               self.stdout.write(f"    • {pair['chunk1']} ↔ {pair['chunk2']}: {pair['similarity']:.3f}")
       
       return {
           'checked_chunks': len(chunks),
           'similar_pairs': len(similar_pairs),
           'threshold': threshold,
           'pairs_sample': similar_pairs[:10] if similar_pairs else []
       }
   
   def _optimize_embeddings(self, options):
       """Embedding optimizasyonu"""
       self.stdout.write("🔧 Embedding optimizasyonu başlatılıyor...")
       
       optimizations = {}
       
       # 1. Remove invalid embeddings
       invalid_count = self._remove_invalid_embeddings(options)
       optimizations['invalid_removed'] = invalid_count
       
       # 2. Remove outliers
       if options['remove_outliers']:
           outlier_count = self._remove_outlier_embeddings(options)
           optimizations['outliers_removed'] = outlier_count
       
       # 3. Update embedding statistics
       stats_updated = self._update_embedding_statistics()
       optimizations['stats_updated'] = stats_updated
       
       # 4. Compact similar embeddings
       if options['similarity_check']:
           compacted = self._compact_similar_embeddings(options)
           optimizations['embeddings_compacted'] = compacted
       
       return {
           'optimization_completed': True,
           'optimizations': optimizations
       }
   
   def _remove_invalid_embeddings(self, options):
       """Geçersiz embedding'leri kaldır"""
       invalid_chunks = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       )
       
       removed_count = 0
       
       for chunk in invalid_chunks:
           if not self._validate_embedding(chunk.embedding):
               if not options['dry_run']:
                   chunk.embedding = None
                   chunk.embedding_model = None
                   chunk.save(update_fields=['embedding', 'embedding_model'])
               removed_count += 1
       
       self.stdout.write(f"  🗑️ {removed_count} geçersiz embedding kaldırıldı")
       return removed_count
   
   def _remove_outlier_embeddings(self, options):
       """Outlier embedding'leri kaldır"""
       chunks_with_embeddings = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       )
       
       if chunks_with_embeddings.count() < 100:
           return 0
       
       # Sample embeddings for outlier detection
       sample_size = min(1000, chunks_with_embeddings.count())
       sample_chunks = chunks_with_embeddings.order_by('?')[:sample_size]
       
       embeddings = []
       chunk_ids = []
       
       for chunk in sample_chunks:
           if chunk.embedding:
               embeddings.append(np.array(chunk.embedding))
               chunk_ids.append(chunk.id)
       
       if len(embeddings) < 10:
           return 0
       
       embeddings = np.array(embeddings)
       
       # Calculate centroid and distances
       centroid = np.mean(embeddings, axis=0)
       distances = np.linalg.norm(embeddings - centroid, axis=1)
       
       # Outlier threshold (3 standard deviations)
       threshold = np.mean(distances) + 3 * np.std(distances)
       outlier_indices = np.where(distances > threshold)[0]
       
       removed_count = 0
       
       if not options['dry_run']:
           for idx in outlier_indices:
               chunk_id = chunk_ids[idx]
               try:
                   chunk = KnowledgeChunk.objects.get(id=chunk_id)
                   chunk.embedding = None
                   chunk.embedding_model = None
                   chunk.save(update_fields=['embedding', 'embedding_model'])
                   removed_count += 1
               except KnowledgeChunk.DoesNotExist:
                   continue
       else:
           removed_count = len(outlier_indices)
       
       self.stdout.write(f"  🎯 {removed_count} outlier embedding kaldırıldı")
       return removed_count
   
   def _update_embedding_statistics(self):
       """Embedding istatistiklerini güncelle"""
       # Performance metrics kaydet
       total_chunks = KnowledgeChunk.objects.count()
       chunks_with_embeddings = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       ).count()
       
       embedding_coverage = (chunks_with_embeddings / max(total_chunks, 1)) * 100
       
       PerformanceMetrics.objects.create(
           component='embedding',
           metric_name='coverage_percentage',
           value=embedding_coverage,
           unit='percent'
       )
       
       # Model breakdown
       model_stats = KnowledgeChunk.objects.values('embedding_model')\
           .annotate(count=Count('id'))\
           .order_by('-count')
       
       for stat in model_stats:
           model_name = stat['embedding_model'] or 'none'
           count = stat['count']
           
           PerformanceMetrics.objects.create(
               component='embedding',
               metric_name=f'model_{model_name}_count',
               value=count,
               unit='count'
           )
       
       return len(model_stats)
   
   def _compact_similar_embeddings(self, options):
       """Benzer embedding'leri kompaktla"""
       # Bu gelişmiş bir özellik - basit implementasyon
       threshold = options.get('threshold', 0.95)
       
       # Çok benzer chunk'ları bul ve birleştir
       similar_groups = self._find_similar_embedding_groups(threshold)

       compacted_count = 0
       
       for group in similar_groups:
           if len(group) > 1 and not options['dry_run']:
               # En kaliteli chunk'ı seç (usage_count ve relevance_score'a göre)
               best_chunk = max(group, key=lambda c: (c.usage_count, c.relevance_score))
               
               # Diğer chunk'ların referanslarını best_chunk'a yönlendir
               for chunk in group:
                   if chunk.id != best_chunk.id:
                       # Chunk'ı soft delete yap
                       chunk.is_active = False
                       chunk.save(update_fields=['is_active'])
                       compacted_count += 1
       
       self.stdout.write(f"  📦 {compacted_count} benzer embedding kompaktlandı")
       return compacted_count
   
   def _find_similar_embedding_groups(self, threshold):
       """Benzer embedding gruplarını bul"""
       chunks_with_embeddings = KnowledgeChunk.objects.filter(
           embedding__isnull=False,
           is_active=True
       )[:500]  # Performans için limit
       
       if chunks_with_embeddings.count() < 2:
           return []
       
       embeddings = []
       chunks = []
       
       for chunk in chunks_with_embeddings:
           if chunk.embedding:
               embeddings.append(np.array(chunk.embedding))
               chunks.append(chunk)
       
       if len(embeddings) < 2:
           return []
       
       embeddings = np.array(embeddings)
       
       # Cosine similarity matrix
       norms = np.linalg.norm(embeddings, axis=1)
       normalized_embeddings = embeddings / norms[:, np.newaxis]
       similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
       
       # Group similar embeddings
       visited = set()
       groups = []
       
       for i in range(len(chunks)):
           if i in visited:
               continue
           
           group = [chunks[i]]
           visited.add(i)
           
           for j in range(i + 1, len(chunks)):
               if j not in visited and similarity_matrix[i, j] >= threshold:
                   group.append(chunks[j])
                   visited.add(j)
           
           if len(group) > 1:
               groups.append(group)
       
       return groups
   
   def _validate_all_embeddings(self, options):
       """Tüm embedding'leri doğrula"""
       self.stdout.write("✅ Embedding doğrulama başlatılıyor...")
       
       chunks_with_embeddings = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       )
       
       total_chunks = chunks_with_embeddings.count()
       valid_count = 0
       invalid_count = 0
       issues = defaultdict(int)
       
       self.stdout.write(f"🔍 {total_chunks:,} embedding doğrulanıyor...")
       
       for i, chunk in enumerate(chunks_with_embeddings):
           validation_result = self._detailed_embedding_validation(chunk)
           
           if validation_result['valid']:
               valid_count += 1
           else:
               invalid_count += 1
               for issue in validation_result['issues']:
                   issues[issue] += 1
           
           # Progress
           if i % 1000 == 0 and (options['progress'] or options['verbose']):
               progress = (i / total_chunks) * 100
               self.stdout.write(f"  İlerleme: {progress:.1f}% ({i:,}/{total_chunks:,})")
       
       # Results
       validation_rate = (valid_count / max(total_chunks, 1)) * 100
       
       self.stdout.write(f"\n✅ Doğrulama Sonuçları:")
       self.stdout.write(f"  • Toplam kontrol edilen: {total_chunks:,}")
       self.stdout.write(f"  • Geçerli: {valid_count:,} ({validation_rate:.1f}%)")
       self.stdout.write(f"  • Geçersiz: {invalid_count:,}")
       
       if issues:
           self.stdout.write(f"\n🔧 Sorun Dağılımı:")
           for issue, count in sorted(issues.items(), key=lambda x: x[1], reverse=True):
               self.stdout.write(f"  • {issue}: {count:,}")
       
       return {
           'total_checked': total_chunks,
           'valid_count': valid_count,
           'invalid_count': invalid_count,
           'validation_rate': validation_rate,
           'issues': dict(issues)
       }
   
   def _detailed_embedding_validation(self, chunk):
       """Detaylı embedding doğrulaması"""
       issues = []
       
       embedding = chunk.embedding
       
       # Basic checks
       if not embedding:
           issues.append('null_embedding')
           return {'valid': False, 'issues': issues}
       
       if not isinstance(embedding, list):
           issues.append('invalid_type')
           return {'valid': False, 'issues': issues}
       
       # Dimension check
       expected_dim = getattr(self.embedding_service, 'embedding_dimension', 384)
       if len(embedding) != expected_dim:
           issues.append('wrong_dimension')
       
       # Convert to numpy array
       try:
           arr = np.array(embedding, dtype=np.float32)
       except (ValueError, TypeError):
           issues.append('conversion_error')
           return {'valid': False, 'issues': issues}
       
       # NaN/Inf check
       if np.any(np.isnan(arr)):
           issues.append('contains_nan')
       
       if np.any(np.isinf(arr)):
           issues.append('contains_inf')
       
       # Zero vector check
       norm = np.linalg.norm(arr)
       if norm < 1e-6:
           issues.append('zero_vector')
       
       # Range check (reasonable values)
       if np.any(np.abs(arr) > 10):
           issues.append('extreme_values')
       
       # Model consistency check
       current_model = self.embedding_service.model_name
       if chunk.embedding_model != current_model:
           issues.append('outdated_model')
       
       # Content-embedding consistency
       if chunk.content and len(chunk.content.strip()) < 10:
           issues.append('short_content')
       
       return {
           'valid': len(issues) == 0,
           'issues': issues
       }
   
   def _update_embedding_model(self, new_model):
       """Embedding modelini güncelle"""
       self.stdout.write(f"🔄 Embedding model güncelleniyor: {new_model}")
       
       try:
           # Embedding service'i yeni model ile yeniden başlat
           self.embedding_service = EmbeddingService(model_name=new_model)
           
           # System configuration'ı güncelle
           config, created = SystemConfiguration.objects.get_or_create(
               key='embedding_model',
               defaults={
                   'value': new_model,
                   'config_type': 'string',
                   'description': 'Kullanılan embedding modeli'
               }
           )
           
           if not created:
               config.value = new_model
               config.save()
           
           self.stdout.write(f"✅ Model güncellendi: {new_model}")
           
       except Exception as e:
           raise CommandError(f"Model güncelleme hatası: {str(e)}")
   
   def _clear_embedding_cache(self):
       """Embedding cache'ini temizle"""
       self.stdout.write("🗑️ Embedding cache temizleniyor...")
       
       try:
           # Cache patterns to clear
           patterns = [
               'sapbot:embedding:*',
               'sapbot:response:*',
               'sapbot:search:*'
           ]
           
           cleared_count = 0
           for pattern in patterns:
               count = embedding_cache.clear_pattern(pattern)
               cleared_count += count
           
           self.stdout.write(f"✅ {cleared_count} cache entry temizlendi")
           
       except Exception as e:
           self.stdout.write(f"❌ Cache temizleme hatası: {str(e)}")
   
   def _export_statistics(self, stats, file_path):
       """İstatistikleri dosyaya aktar"""
       try:
           import json
           from datetime import datetime
           
           export_data = {
               'timestamp': datetime.now().isoformat(),
               'embedding_model': self.embedding_service.model_name,
               'statistics': stats,
               'system_info': {
                   'total_chunks': KnowledgeChunk.objects.count(),
                   'chunks_with_embeddings': KnowledgeChunk.objects.filter(
                       embedding__isnull=False
                   ).count(),
                   'active_chunks': KnowledgeChunk.objects.filter(
                       is_active=True
                   ).count()
               }
           }
           
           with open(file_path, 'w', encoding='utf-8') as f:
               json.dump(export_data, f, indent=2, ensure_ascii=False)
           
           self.stdout.write(f"📊 İstatistikler dışa aktarıldı: {file_path}")
           
       except Exception as e:
           self.stdout.write(f"❌ Export hatası: {str(e)}")
   
   def _display_results(self, result, options):
       """Sonuçları göster"""
       end_time = time.time()
       duration = end_time - self.stats['start_time']
       
       self.stdout.write("\n" + "="*60)
       self.stdout.write(self.style.SUCCESS("🧠 Embedding Rebuild Tamamlandı!"))
       self.stdout.write("="*60)
       
       # Duration
       duration_str = f"{duration:.1f} saniye"
       if duration > 60:
           duration_str = f"{duration/60:.1f} dakika"
       self.stdout.write(f"⏱️ Toplam süre: {duration_str}")
       
       # Model info
       self.stdout.write(f"🤖 Kullanılan model: {self.embedding_service.model_name}")
       
       # Mode specific results
       if result.get('dry_run'):
           self.stdout.write(self.style.WARNING("\n🔍 DRY RUN - Hiçbir değişiklik yapılmadı"))
           
           if 'total_chunks' in result:
               self.stdout.write(f"📊 Analiz edilen chunk: {result['total_chunks']:,}")
               
           if 'missing_embeddings' in result:
               self.stdout.write(f"  • Embedding eksik: {result['missing_embeddings']:,}")
               self.stdout.write(f"  • Eski model: {result['outdated_embeddings']:,}")
       
       elif result.get('optimization_completed'):
           self.stdout.write(f"\n🔧 Optimizasyon Tamamlandı")
           for key, count in result.get('optimizations', {}).items():
               self.stdout.write(f"  • {key.replace('_', ' ').title()}: {count:,}")
       
       elif result.get('similar_pairs') is not None:
           self.stdout.write(f"\n🔍 Similarity Check Tamamlandı")
           self.stdout.write(f"  • Kontrol edilen: {result.get('checked_chunks', 0):,}")
           self.stdout.write(f"  • Benzer çiftler: {result['similar_pairs']:,}")
           self.stdout.write(f"  • Threshold: {result.get('threshold', 0):.2f}")
       
       elif result.get('validation_rate') is not None:
           self.stdout.write(f"\n✅ Validation Tamamlandı")
           self.stdout.write(f"  • Kontrol edilen: {result.get('total_checked', 0):,}")
           self.stdout.write(f"  • Geçerli: {result.get('valid_count', 0):,}")
           self.stdout.write(f"  • Geçersiz: {result.get('invalid_count', 0):,}")
           self.stdout.write(f"  • Başarı oranı: {result['validation_rate']:.1f}%")
       
       else:
           # Normal rebuild results
           self.stdout.write(f"\n📊 Rebuild Sonuçları ({result.get('mode', 'unknown')})")
           
           if 'total_chunks' in result:
               self.stdout.write(f"  • Toplam chunk: {result['total_chunks']:,}")
           
           if 'processed' in result:
               self.stdout.write(f"  • İşlenen: {result['processed']:,}")
               success_rate = (result.get('successful', 0) / max(result['processed'], 1)) * 100
               self.stdout.write(f"  • Başarılı: {result.get('successful', 0):,} ({success_rate:.1f}%)")
               self.stdout.write(f"  • Başarısız: {result.get('failed', 0):,}")
       
       # Performance metrics
       if 'successful' in result and result['successful'] > 0 and duration > 0:
           embeddings_per_sec = result['successful'] / duration
           self.stdout.write(f"\n📈 Performans")
           self.stdout.write(f"  • Embedding/saniye: {embeddings_per_sec:.1f}")
           
           if 'processed' in result:
               avg_time_per_chunk = duration / result['processed']
               self.stdout.write(f"  • Chunk başına ortalama süre: {avg_time_per_chunk:.3f} saniye")
       
       # Errors
       if result.get('errors'):
           error_count = len(result['errors'])
           self.stdout.write(f"\n❌ Hatalar ({error_count}):")
           for i, error in enumerate(result['errors'][:5]):
               self.stdout.write(f"  {i+1}. {error}")
           
           if error_count > 5:
               self.stdout.write(f"  ... ve {error_count - 5} hata daha")
       
       # Current system status
       self._display_system_status()
       
       # Export statistics if requested
       if options.get('export_stats'):
           self._export_statistics(result, options['export_stats'])
       
       # Recommendations
       self._display_recommendations(result, options)
   
   def _display_system_status(self):
       """Mevcut sistem durumunu göster"""
       total_chunks = KnowledgeChunk.objects.count()
       chunks_with_embeddings = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       ).count()
       
       coverage = (chunks_with_embeddings / max(total_chunks, 1)) * 100
       
       self.stdout.write(f"\n📈 Sistem Durumu")
       self.stdout.write(f"  • Toplam chunk: {total_chunks:,}")
       self.stdout.write(f"  • Embedding coverage: {coverage:.1f}%")
       
       # Model breakdown
       model_stats = KnowledgeChunk.objects.filter(
           embedding__isnull=False
       ).values('embedding_model').annotate(
           count=Count('id')
       ).order_by('-count')[:5]
       
       if model_stats:
           self.stdout.write(f"  • Model dağılımı:")
           for stat in model_stats:
               model_name = stat['embedding_model'] or 'Unknown'
               count = stat['count']
               percentage = (count / max(chunks_with_embeddings, 1)) * 100
               self.stdout.write(f"    - {model_name}: {count:,} ({percentage:.1f}%)")
   
   def _display_recommendations(self, result, options):
       """Öneriler göster"""
       recommendations = []
       
       # Coverage recommendations
       if result.get('total_chunks', 0) > 0:
           missing_embeddings = result.get('missing_embeddings', 0)
           if missing_embeddings > 0:
               recommendations.append(f"📝 {missing_embeddings:,} chunk için embedding eksik")
       
       # Performance recommendations
       if result.get('mode') == 'sequential' and result.get('total_chunks', 0) > 100:
           recommendations.append("⚡ Büyük veri setleri için --workers kullanın")
       
       # Quality recommendations
       if result.get('invalid_count', 0) > 0:
           recommendations.append("🔧 Geçersiz embedding'ler için --optimize kullanın")
       
       # Model recommendations
       current_model = self.embedding_service.model_name
       if 'outdated_embeddings' in result and result['outdated_embeddings'] > 0:
           recommendations.append(f"🆕 {result['outdated_embeddings']:,} chunk eski model kullanıyor")
       
       # Cache recommendations
       if not options.get('cache_embeddings'):
           recommendations.append("💾 Performans için --cache-embeddings kullanın")
       
       if recommendations:
           self.stdout.write(f"\n💡 Öneriler:")
           for rec in recommendations:
               self.stdout.write(f"  • {rec}")
       
       # Next steps
       self.stdout.write(f"\n📝 Sonraki Adımlar:")
       
       if result.get('successful', 0) > 0:
           self.stdout.write(f"  • Semantic search testleri yapın")
           self.stdout.write(f"  • Chat performansını kontrol edin")
       
       if result.get('failed', 0) > 0:
           self.stdout.write(f"  • Başarısız chunk'ları tekrar işleyin")
           self.stdout.write(f"  • Log dosyalarını inceleyin")
       
       self.stdout.write(f"  • Periyodik embedding kalite kontrolü yapın")
       self.stdout.write(f"  • Model güncellemelerini takip edin")
       
       self.stdout.write("\n" + "="*60)
       self.stdout.write(self.style.SUCCESS("✨ Embedding işlemleri tamamlandı!"))