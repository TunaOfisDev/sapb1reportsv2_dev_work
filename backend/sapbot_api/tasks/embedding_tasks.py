# backend/sapbot_api/tasks/embedding_tasks.py
"""
SAPBot API Embedding Tasks

Bu modül embedding oluşturma, güncelleme ve toplu işlem
Celery task'larını içerir.
"""

import logging
import hashlib
import time
from typing import List, Dict, Any
from datetime import  timedelta
from celery import shared_task

from django.db import transaction, connection
from django.utils import timezone
from django.conf import settings

from ..models import DocumentSource, KnowledgeChunk
from ..utils.cache_utils import embedding_cache
from ..utils.exceptions import (
   EmbeddingError, 
   DocumentProcessingError,
  
)
from ..utils.helpers import clean_text

logger = logging.getLogger(__name__)


class EmbeddingService:
   """Embedding servis sınıfı"""
   
   def __init__(self):
       self.model_name = getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
       self.model = None
       self.batch_size = getattr(settings, 'EMBEDDING_BATCH_SIZE', 32)
       self.max_retries = 3
       self.retry_delay = 5  # saniye
   
   def load_model(self):
       """Model yükle - lazy loading"""
       if self.model is None:
           try:
               from sentence_transformers import SentenceTransformer
               self.model = SentenceTransformer(self.model_name)
               logger.info(f"Embedding model yüklendi: {self.model_name}")
           except Exception as e:
               logger.error(f"Embedding model yükleme hatası: {e}")
               raise EmbeddingError(f"Model yükleme hatası: {str(e)}")
   
   def generate_embedding(self, text: str) -> List[float]:
       """Tek metin için embedding oluştur"""
       if not text or not text.strip():
           raise EmbeddingError("Boş metin için embedding oluşturulamaz")
       
       # Cache kontrolü
       content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
       cached_embedding = embedding_cache.get_embedding(content_hash)
       
       if cached_embedding:
           logger.debug(f"Embedding cache'den alındı: {content_hash[:8]}")
           return cached_embedding
       
       # Model yükle
       self.load_model()
       
       try:
           # Metin temizle
           clean_content = clean_text(text)
           if len(clean_content) > 8000:  # Token limiti
               clean_content = clean_content[:8000]
           
           # Embedding oluştur
           embedding = self.model.encode(clean_content, convert_to_tensor=False)
           embedding_list = embedding.tolist()
           
           # Cache'e kaydet
           embedding_cache.set_embedding(content_hash, embedding_list)
           
           logger.debug(f"Yeni embedding oluşturuldu: {content_hash[:8]}")
           return embedding_list
           
       except Exception as e:
           logger.error(f"Embedding oluşturma hatası: {e}")
           raise EmbeddingError(f"Embedding oluşturma hatası: {str(e)}")
   
   def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
       """Toplu embedding oluştur"""
       if not texts:
           return []
       
       # Cache kontrolü
       embeddings = []
       texts_to_process = []
       text_hashes = []
       
       for text in texts:
           if not text or not text.strip():
               embeddings.append([])
               continue
           
           content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
           cached_embedding = embedding_cache.get_embedding(content_hash)
           
           if cached_embedding:
               embeddings.append(cached_embedding)
           else:
               embeddings.append(None)  # Placeholder
               texts_to_process.append(clean_text(text)[:8000])
               text_hashes.append(content_hash)
       
       # Yeni embedding'leri oluştur
       if texts_to_process:
           self.load_model()
           
           try:
               new_embeddings = self.model.encode(texts_to_process, convert_to_tensor=False)
               
               # Cache'e kaydet ve sonuçları yerleştir
               cache_data = {}
               new_idx = 0
               
               for i, embedding in enumerate(embeddings):
                   if embedding is None:
                       new_embedding = new_embeddings[new_idx].tolist()
                       embeddings[i] = new_embedding
                       cache_data[text_hashes[new_idx]] = new_embedding
                       new_idx += 1
               
               # Toplu cache kaydet
               if cache_data:
                   embedding_cache.set_batch_embeddings(cache_data)
               
               logger.info(f"Toplu embedding oluşturuldu: {len(texts_to_process)} yeni, {len(texts) - len(texts_to_process)} cache")
               
           except Exception as e:
               logger.error(f"Toplu embedding hatası: {e}")
               raise EmbeddingError(f"Toplu embedding hatası: {str(e)}")
       
       return embeddings


# Global service instance
embedding_service = EmbeddingService()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_embeddings(self, document_id: str) -> Dict[str, Any]:
   """Döküman için embedding'leri işle"""
   try:
       logger.info(f"Döküman embedding işlemi başladı: {document_id}")
       
       # Döküman kontrol
       try:
           document = DocumentSource.objects.get(id=document_id)
       except DocumentSource.DoesNotExist:
           logger.error(f"Döküman bulunamadı: {document_id}")
           return {'success': False, 'error': 'Döküman bulunamadı'}
       
       # Durumu güncelle
       document.processing_status = 'processing'
       document.save(update_fields=['processing_status'])
       
       # Chunk'ları al
       chunks = KnowledgeChunk.objects.filter(
           source=document,
           embedding__isnull=True,
           is_active=True
       ).order_by('created_at')
       
       if not chunks.exists():
           logger.warning(f"İşlenecek chunk bulunamadı: {document_id}")
           document.processing_status = 'completed'
           document.processed_at = timezone.now()
           document.save(update_fields=['processing_status', 'processed_at'])
           return {'success': True, 'processed_chunks': 0}
       
       # Toplu işlem için grupla
       chunk_groups = []
       current_group = []
       
       for chunk in chunks:
           current_group.append(chunk)
           if len(current_group) >= embedding_service.batch_size:
               chunk_groups.append(current_group)
               current_group = []
       
       if current_group:
           chunk_groups.append(current_group)
       
       total_processed = 0
       failed_chunks = []
       
       # Grup grup işle
       for i, chunk_group in enumerate(chunk_groups):
           try:
               logger.info(f"Chunk grubu işleniyor: {i+1}/{len(chunk_groups)} ({len(chunk_group)} chunk)")
               
               # Metinleri hazırla
               texts = [chunk.content for chunk in chunk_group]
               
               # Embedding'leri oluştur
               embeddings = embedding_service.generate_batch_embeddings(texts)
               
               # Veritabanına kaydet
               with transaction.atomic():
                   for chunk, embedding in zip(chunk_group, embeddings):
                       if embedding:
                           chunk.embedding = embedding
                           chunk.embedding_model = embedding_service.model_name
                           chunk.save(update_fields=['embedding', 'embedding_model'])
                           total_processed += 1
                       else:
                           failed_chunks.append(str(chunk.id))
               
               # Progress tracking
               progress = ((i + 1) / len(chunk_groups)) * 100
               logger.info(f"İlerleme: %{progress:.1f} - {total_processed} chunk işlendi")
               
               # Kısa pause (rate limiting)
               time.sleep(0.1)
               
           except Exception as e:
               logger.error(f"Chunk grubu işleme hatası: {e}")
               failed_chunks.extend([str(chunk.id) for chunk in chunk_group])
               
               # Kritik hata ise dur
               if isinstance(e, (MemoryError, KeyboardInterrupt)):
                   raise
       
       # Sonuçları kaydet
       success_rate = total_processed / chunks.count() if chunks.count() > 0 else 0
       
       if success_rate > 0.8:  # %80'den fazla başarı
           document.processing_status = 'completed'
       else:
           document.processing_status = 'failed'
           document.processing_error = f"Düşük başarı oranı: %{success_rate*100:.1f}"
       
       document.processed_at = timezone.now()
       document.save(update_fields=['processing_status', 'processed_at', 'processing_error'])
       
       result = {
           'success': success_rate > 0.5,
           'document_id': document_id,
           'total_chunks': chunks.count(),
           'processed_chunks': total_processed,
           'failed_chunks': len(failed_chunks),
           'success_rate': success_rate,
           'processing_time': (timezone.now() - document.created_at).total_seconds()
       }
       
       logger.info(f"Döküman embedding tamamlandı: {document_id} - {total_processed}/{chunks.count()} başarılı")
       
       return result
       
   except Exception as exc:
       logger.error(f"Döküman embedding hatası: {exc}")
       
       # Retry logic
       if self.request.retries < self.max_retries:
           logger.info(f"Tekrar deneniyor: {self.request.retries + 1}/{self.max_retries}")
           raise self.retry(countdown=60 * (self.request.retries + 1))
       
       # Final failure
       try:
           document = DocumentSource.objects.get(id=document_id)
           document.processing_status = 'failed'
           document.processing_error = str(exc)[:500]
           document.save(update_fields=['processing_status', 'processing_error'])
       except:
           pass
       
       raise DocumentProcessingError(
           message=f"Döküman embedding işlemi başarısız: {str(exc)}",
           document_id=document_id,
           processing_stage="embedding_generation"
       )


@shared_task(bind=True, max_retries=2)
def update_chunk_embedding(self, chunk_id: str, force_update: bool = False) -> Dict[str, Any]:
   """Tekil chunk embedding güncelle"""
   try:
       # Chunk kontrol
       try:
           chunk = KnowledgeChunk.objects.get(id=chunk_id)
       except KnowledgeChunk.DoesNotExist:
           return {'success': False, 'error': 'Chunk bulunamadı'}
       
       # Zaten embedding varsa ve force değilse skip
       if chunk.embedding and not force_update:
           return {'success': True, 'message': 'Embedding zaten mevcut', 'skipped': True}
       
       # Embedding oluştur
       start_time = time.time()
       embedding = embedding_service.generate_embedding(chunk.content)
       processing_time = time.time() - start_time
       
       # Kaydet
       chunk.embedding = embedding
       chunk.embedding_model = embedding_service.model_name
       chunk.save(update_fields=['embedding', 'embedding_model', 'updated_at'])
       
       logger.info(f"Chunk embedding güncellendi: {chunk_id} ({processing_time:.2f}s)")
       
       return {
           'success': True,
           'chunk_id': chunk_id,
           'processing_time': processing_time,
           'embedding_size': len(embedding)
       }
       
   except Exception as exc:
       logger.error(f"Chunk embedding hatası: {exc}")
       
       if self.request.retries < self.max_retries:
           raise self.retry(countdown=30)
       
       raise EmbeddingError(f"Chunk embedding hatası: {str(exc)}")


@shared_task
def bulk_update_embeddings(
   document_ids: List[str] = None,
   chunk_ids: List[str] = None,
   force_update: bool = False
) -> Dict[str, Any]:
   """Toplu embedding güncelleme"""
   try:
       logger.info("Toplu embedding güncelleme başladı")
       start_time = time.time()
       
       tasks = []
       
       # Döküman bazlı işlemler
       if document_ids:
           for doc_id in document_ids:
               task = process_document_embeddings.delay(doc_id)
               tasks.append(task)
       
       # Chunk bazlı işlemler
       if chunk_ids:
           for chunk_id in chunk_ids:
               task = update_chunk_embedding.delay(chunk_id, force_update)
               tasks.append(task)
       
       # Tüm embedding eksik dökümanlar
       if not document_ids and not chunk_ids:
           pending_docs = DocumentSource.objects.filter(
               processing_status__in=['pending', 'failed'],
               is_active=True
           ).values_list('id', flat=True)
           
           for doc_id in pending_docs:
               task = process_document_embeddings.delay(str(doc_id))
               tasks.append(task)
       
       # Sonuçları bekle (optional - async için comment out edilebilir)
       results = []
       for task in tasks:
           try:
               result = task.get(timeout=600)  # 10 dakika timeout
               results.append(result)
           except Exception as e:
               logger.error(f"Task hatası: {e}")
               results.append({'success': False, 'error': str(e)})
       
       total_time = time.time() - start_time
       success_count = sum(1 for r in results if r.get('success', False))
       
       logger.info(f"Toplu embedding tamamlandı: {success_count}/{len(tasks)} başarılı ({total_time:.1f}s)")
       
       return {
           'success': True,
           'total_tasks': len(tasks),
           'successful_tasks': success_count,
           'failed_tasks': len(tasks) - success_count,
           'total_time': total_time,
           'results': results
       }
       
   except Exception as e:
       logger.error(f"Toplu embedding hatası: {e}")
       return {'success': False, 'error': str(e)}


@shared_task
def cleanup_failed_embeddings() -> Dict[str, Any]:
   """Başarısız embedding'leri temizle ve tekrar dene"""
   try:
       logger.info("Başarısız embedding'ler temizleniyor")
       
       # 24 saatten eski failed dökümanlar
       cutoff_time = timezone.now() - timedelta(hours=24)
       failed_docs = DocumentSource.objects.filter(
           processing_status='failed',
           updated_at__lt=cutoff_time,
           is_active=True
       )
       
       retry_count = 0
       
       for doc in failed_docs:
           # Embedding'leri temizle
           KnowledgeChunk.objects.filter(source=doc).update(
               embedding=None,
               embedding_model=None
           )
           
           # Durumu reset et
           doc.processing_status = 'pending'
           doc.processing_error = None
           doc.save(update_fields=['processing_status', 'processing_error'])
           
           # Yeniden işleme gönder
           process_document_embeddings.delay(str(doc.id))
           retry_count += 1
       
       logger.info(f"Başarısız embedding temizleme tamamlandı: {retry_count} döküman")
       
       return {
           'success': True,
           'retried_documents': retry_count,
           'cleanup_time': timezone.now().isoformat()
       }
       
   except Exception as e:
       logger.error(f"Embedding temizleme hatası: {e}")
       return {'success': False, 'error': str(e)}


@shared_task
def embedding_health_check() -> Dict[str, Any]:
   """Embedding sistemi sağlık kontrolü"""
   try:
       health_status = {
           'model_loaded': False,
           'cache_working': False,
           'database_connection': False,
           'sample_embedding': False,
           'overall_status': 'unhealthy'
       }
       
       # Model yükleme testi
       try:
           embedding_service.load_model()
           health_status['model_loaded'] = True
       except Exception as e:
           logger.error(f"Model yükleme hatası: {e}")
       
       # Cache testi
       try:
           test_hash = "test_hash"
           test_embedding = [0.1, 0.2, 0.3]
           embedding_cache.set_embedding(test_hash, test_embedding)
           retrieved = embedding_cache.get_embedding(test_hash)
           health_status['cache_working'] = retrieved == test_embedding
       except Exception as e:
           logger.error(f"Cache test hatası: {e}")
       
       # Veritabanı bağlantı testi
       try:
           with connection.cursor() as cursor:
               cursor.execute("SELECT 1")
           health_status['database_connection'] = True
       except Exception as e:
           logger.error(f"Veritabanı test hatası: {e}")
       
       # Örnek embedding testi
       if health_status['model_loaded']:
           try:
               test_text = "Bu bir test metnidir."
               embedding = embedding_service.generate_embedding(test_text)
               health_status['sample_embedding'] = len(embedding) > 0
           except Exception as e:
               logger.error(f"Örnek embedding hatası: {e}")
       
       # Genel durum
       all_checks = [
           health_status['model_loaded'],
           health_status['cache_working'],
           health_status['database_connection'],
           health_status['sample_embedding']
       ]
       
       if all(all_checks):
           health_status['overall_status'] = 'healthy'
       elif any(all_checks):
           health_status['overall_status'] = 'degraded'
       
       # İstatistikler ekle
       stats = get_embedding_statistics()
       health_status.update(stats)
       
       return health_status
       
   except Exception as e:
       logger.error(f"Sağlık kontrolü hatası: {e}")
       return {
           'overall_status': 'error',
           'error': str(e),
           'timestamp': timezone.now().isoformat()
       }


@shared_task
def embedding_statistics_update() -> Dict[str, Any]:
   """Embedding istatistiklerini güncelle"""
   try:
       stats = get_embedding_statistics()
       
       # Cache'e kaydet
       from ..utils.cache_utils import system_cache
       system_cache.set_system_config('embedding_stats', stats, timeout=3600)
       
       logger.info("Embedding istatistikleri güncellendi")
       return stats
       
   except Exception as e:
       logger.error(f"İstatistik güncelleme hatası: {e}")
       return {'error': str(e)}


def get_embedding_statistics() -> Dict[str, Any]:
   """Embedding sistem istatistikleri"""
   try:
       with connection.cursor() as cursor:
           # Toplam chunk sayısı
           cursor.execute("SELECT COUNT(*) FROM sapbot_knowledge_chunks WHERE is_active = true")
           total_chunks = cursor.fetchone()[0]
           
           # Embedding'li chunk sayısı
           cursor.execute("SELECT COUNT(*) FROM sapbot_knowledge_chunks WHERE embedding IS NOT NULL AND is_active = true")
           embedded_chunks = cursor.fetchone()[0]
           
           # Döküman durumları
           cursor.execute("""
               SELECT processing_status, COUNT(*) 
               FROM sapbot_document_sources 
               WHERE is_active = true 
               GROUP BY processing_status
           """)
           doc_status = dict(cursor.fetchall())
           
           # Ortalama embedding boyutu
           cursor.execute("""
               SELECT AVG(jsonb_array_length(embedding)) 
               FROM sapbot_knowledge_chunks 
               WHERE embedding IS NOT NULL AND is_active = true
           """)
           avg_embedding_size = cursor.fetchone()[0] or 0
           
           # Son 24 saatte işlenen
           cursor.execute("""
               SELECT COUNT(*) 
               FROM sapbot_knowledge_chunks 
               WHERE embedding IS NOT NULL 
               AND updated_at > NOW() - INTERVAL '24 hours'
               AND is_active = true
           """)
           recent_processed = cursor.fetchone()[0]
       
       completion_rate = (embedded_chunks / total_chunks * 100) if total_chunks > 0 else 0
       
       return {
           'total_chunks': total_chunks,
           'embedded_chunks': embedded_chunks,
           'pending_chunks': total_chunks - embedded_chunks,
           'completion_rate': round(completion_rate, 2),
           'document_status': doc_status,
           'avg_embedding_size': round(avg_embedding_size, 1) if avg_embedding_size else 0,
           'recent_24h_processed': recent_processed,
           'last_updated': timezone.now().isoformat()
       }
       
   except Exception as e:
       logger.error(f"İstatistik hesaplama hatası: {e}")
       return {
           'error': str(e),
           'last_updated': timezone.now().isoformat()
       }


# Periodic task helper
@shared_task
def schedule_embedding_maintenance():
   """Düzenli bakım görevleri"""
   try:
       # Sağlık kontrolü
       health_check = embedding_health_check.delay()
       
       # İstatistik güncelleme
       stats_update = embedding_statistics_update.delay()
       
       # Başarısız embedding'leri temizle (günde bir)
       cleanup = cleanup_failed_embeddings.delay()
       
       return {
           'health_check_task': health_check.id,
           'stats_update_task': stats_update.id,
           'cleanup_task': cleanup.id,
           'scheduled_at': timezone.now().isoformat()
       }
       
   except Exception as e:
       logger.error(f"Bakım görevi zamanlama hatası: {e}")
       return {'error': str(e)}


# Utility task
@shared_task
def reindex_embeddings_by_model(old_model: str, new_model: str) -> Dict[str, Any]:
   """Model değişikliği sonrası yeniden indeksleme"""
   try:
       logger.info(f"Model değişikliği: {old_model} -> {new_model}")
       
       # Eski model ile oluşturulmuş embedding'leri bul
       old_chunks = KnowledgeChunk.objects.filter(
           embedding_model=old_model,
           is_active=True
       ).values_list('id', flat=True)
       
       if not old_chunks:
           return {'success': True, 'message': 'Güncellenmesi gereken chunk bulunamadı'}
       
       # Yeni model ayarla
       embedding_service.model_name = new_model
       embedding_service.model = None  # Force reload
       
       # Toplu güncelleme başlat
       result = bulk_update_embeddings(
           chunk_ids=[str(chunk_id) for chunk_id in old_chunks],
           force_update=True
       )
       
       logger.info(f"Model değişikliği tamamlandı: {len(old_chunks)} chunk güncellendi")
       
       return {
           'success': True,
           'old_model': old_model,
           'new_model': new_model,
           'updated_chunks': len(old_chunks),
           'bulk_result': result
       }
       
   except Exception as e:
       logger.error(f"Model değişikliği hatası: {e}")
       return {'success': False, 'error': str(e)}