# backend/sapbot_api/services/document_processor.py

import logging
from typing import Dict, List, Optional, Any, Sum
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from django.db import models
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from ..models import DocumentSource, KnowledgeChunk
from ..utils.file_handlers import PDFProcessor, VideoProcessor, FileManager
from ..utils.text_processing import TextAnalyzer, TextChunker
from ..utils.cache_utils import embedding_cache
from ..utils.exceptions import (
   DocumentProcessingError,
   EmbeddingError,
   ValidationException
)
from ..utils.helpers import generate_hash, clean_text
from .embedding_service import EmbeddingService
from .search_service import SearchService

logger = logging.getLogger(__name__)


class DocumentProcessingService:
   """Döküman işleme ana servisi - asenkron ve performans odaklı"""
   
   def __init__(self):
       self.pdf_processor = PDFProcessor()
       self.video_processor = VideoProcessor()
       self.file_manager = FileManager()
       self.embedding_service = EmbeddingService()
       self.search_service = SearchService()
       self.max_workers = getattr(settings, 'DOCUMENT_PROCESSING_WORKERS', 4)
       
   def process_document(self, document_id: str) -> Dict[str, Any]:
       """Ana döküman işleme fonksiyonu"""
       try:
           # Document'ı veritabanından al
           document = DocumentSource.objects.get(id=document_id)
           
           # İşleme durumunu güncelle
           document.processing_status = 'processing'
           document.save(update_fields=['processing_status'])
           
           logger.info(f"Döküman işleme başladı: {document.title} ({document.id})")
           
           # Dosya tipine göre işle
           if document.document_type == 'pdf':
               result = self._process_pdf_document(document)
           elif document.document_type == 'video':
               result = self._process_video_document(document)
           elif document.document_type == 'manual':
               result = self._process_manual_document(document)
           else:
               raise DocumentProcessingError(
                   f"Desteklenmeyen döküman tipi: {document.document_type}",
                   document_id=str(document.id)
               )
           
           # İşleme başarılı
           document.processing_status = 'completed'
           document.processed_at = timezone.now()
           document.save(update_fields=['processing_status', 'processed_at'])
           
           logger.info(f"Döküman işleme tamamlandı: {document.title}")
           
           # Search index'i güncelle
           self._update_search_index(document)
           
           return {
               'success': True,
               'document_id': str(document.id),
               'chunks_created': result.get('chunks_created', 0),
               'processing_time': result.get('processing_time', 0),
               'total_content_length': result.get('total_content_length', 0)
           }
           
       except Exception as e:
           # Hata durumunda document'ı güncelle
           try:
               document.processing_status = 'failed'
               document.processing_error = str(e)
               document.save(update_fields=['processing_status', 'processing_error'])
           except:
               pass
           
           logger.error(f"Döküman işleme hatası: {e}", exc_info=True)
           raise DocumentProcessingError(
               f"Döküman işleme başarısız: {str(e)}",
               document_id=document_id,
               processing_stage="main_processing"
           )
   
   def _process_pdf_document(self, document: DocumentSource) -> Dict[str, Any]:
       """PDF döküman işleme"""
       start_time = datetime.now()
       
       try:
           # PDF'den metin çıkar
           file_path = document.file_path.path
           pdf_content = self.pdf_processor.extract_text(file_path)
           
           # Chunk'lara böl ve işle
           chunks_created = self._process_content_chunks(
               document=document,
               content_data=pdf_content['text_content'],
               source_type='pdf'
           )
           
           # Enhanced content (tablolar vb.) varsa ayrı işle
           if pdf_content.get('enhanced_content'):
               enhanced_chunks = self._process_enhanced_content(
                   document=document,
                   enhanced_content=pdf_content['enhanced_content']
               )
               chunks_created += enhanced_chunks
           
           processing_time = (datetime.now() - start_time).total_seconds()
           
           return {
               'chunks_created': chunks_created,
               'processing_time': processing_time,
               'total_content_length': pdf_content.get('total_characters', 0),
               'pages_processed': pdf_content.get('total_pages', 0)
           }
           
       except Exception as e:
           raise DocumentProcessingError(
               f"PDF işleme hatası: {str(e)}",
               document_id=str(document.id),
               processing_stage="pdf_extraction"
           )
   
   def _process_video_document(self, document: DocumentSource) -> Dict[str, Any]:
       """Video döküman işleme"""
       start_time = datetime.now()
       
       try:
           # Video'dan transkript çıkar
           file_path = document.file_path.path
           video_content = self.video_processor.extract_transcript(file_path)
           
           # Transkript segmentlerini chunk'lara dönüştür
           content_data = []
           for segment in video_content['segments']:
               content_data.append({
                   'page_number': None,
                   'text': segment['text'],
                   'char_count': len(segment['text']),
                   'timestamp_start': segment['start'],
                   'timestamp_end': segment['end'],
                   'confidence': segment.get('confidence', 1.0)
               })
           
           chunks_created = self._process_content_chunks(
               document=document,
               content_data=content_data,
               source_type='video'
           )
           
           processing_time = (datetime.now() - start_time).total_seconds()
           
           return {
               'chunks_created': chunks_created,
               'processing_time': processing_time,
               'total_content_length': len(video_content['full_text']),
               'duration': video_content.get('duration', 0)
           }
           
       except Exception as e:
           raise DocumentProcessingError(
               f"Video işleme hatası: {str(e)}",
               document_id=str(document.id),
               processing_stage="video_transcription"
           )
   
   def _process_manual_document(self, document: DocumentSource) -> Dict[str, Any]:
       """Manuel giriş döküman işleme"""
       start_time = datetime.now()
       
       try:
           # Metadata'dan içeriği al
           content = document.metadata.get('content', '')
           if not content:
               raise DocumentProcessingError(
                   "Manuel döküman için içerik bulunamadı",
                   document_id=str(document.id)
               )
           
           # Tek chunk olarak işle
           content_data = [{
               'page_number': 1,
               'text': content,
               'char_count': len(content)
           }]
           
           chunks_created = self._process_content_chunks(
               document=document,
               content_data=content_data,
               source_type='manual'
           )
           
           processing_time = (datetime.now() - start_time).total_seconds()
           
           return {
               'chunks_created': chunks_created,
               'processing_time': processing_time,
               'total_content_length': len(content)
           }
           
       except Exception as e:
           raise DocumentProcessingError(
               f"Manuel döküman işleme hatası: {str(e)}",
               document_id=str(document.id),
               processing_stage="manual_processing"
           )
   
   def _process_content_chunks(
       self, 
       document: DocumentSource, 
       content_data: List[Dict], 
       source_type: str
   ) -> int:
       """İçerik chunk'larını işle - paralel processing"""
       
       if not content_data:
           return 0
       
       chunks_created = 0
       
       # ThreadPoolExecutor ile paralel işleme
       with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
           # Her sayfa/segment için chunk'ları oluştur
           future_to_page = {}
           
           for page_content in content_data:
               if not page_content.get('text', '').strip():
                   continue
               
               future = executor.submit(
                   self._process_single_page_content,
                   document,
                   page_content,
                   source_type
               )
               future_to_page[future] = page_content
           
           # Sonuçları topla
           for future in future_to_page:
               try:
                   page_chunks = future.result(timeout=300)  # 5 dakika timeout
                   chunks_created += page_chunks
               except Exception as e:
                   page_info = future_to_page[future]
                   logger.error(
                       f"Sayfa işleme hatası - Döküman: {document.id}, "
                       f"Sayfa: {page_info.get('page_number', 'N/A')}, Hata: {e}"
                   )
       
       return chunks_created
   
   def _process_single_page_content(
       self, 
       document: DocumentSource, 
       page_content: Dict, 
       source_type: str
   ) -> int:
       """Tek sayfa içeriğini chunk'lara böl ve işle"""
       
       text = page_content['text']
       if not text or len(text.strip()) < 10:
           return 0
       
       # Metni temizle
       cleaned_text = clean_text(text)
       
       # Metin analizi
       analysis = TextAnalyzer.analyze_text(cleaned_text)
       
       # Chunk'lara böl - akıllı bölme
       chunk_size = self._determine_chunk_size(analysis.technical_level)
       chunks = TextChunker.intelligent_split(
           cleaned_text,
           max_chunk_size=chunk_size,
           overlap=200,
           preserve_paragraphs=True
       )
       
       chunks_created = 0
       
       for chunk in chunks:
           try:
               # Chunk için embedding oluştur
               embedding = self._generate_chunk_embedding(chunk.text)
               
               # KnowledgeChunk oluştur
               knowledge_chunk = KnowledgeChunk.objects.create(
                   source=document,
                   content=chunk.text,
                   content_length=chunk.char_count,
                   page_number=page_content.get('page_number'),
                   section_title=self._extract_section_title(chunk.text),
                   sap_module=analysis.sap_modules[0] if analysis.sap_modules else None,
                   technical_level=analysis.technical_level,
                   keywords=analysis.keywords[:10],  # İlk 10 keyword
                   embedding=embedding,
                   embedding_model=self.embedding_service.model_name,
                   relevance_score=1.0,  # Başlangıç değeri
                   is_verified=False
               )
               
               # Video için timestamp bilgisi ekle
               if source_type == 'video' and 'timestamp_start' in page_content:
                   knowledge_chunk.metadata = {
                       'timestamp_start': page_content['timestamp_start'],
                       'timestamp_end': page_content['timestamp_end'],
                       'confidence': page_content.get('confidence', 1.0)
                   }
                   knowledge_chunk.save(update_fields=['metadata'])
               
               chunks_created += 1
               
           except Exception as e:
               logger.error(f"Chunk oluşturma hatası: {e}")
               continue
       
       return chunks_created
   
   def _process_enhanced_content(
       self, 
       document: DocumentSource, 
       enhanced_content: List[Dict]
   ) -> int:
       """Gelişmiş içerik işleme (tablolar, resimler vb.)"""
       
       chunks_created = 0
       
       for page_data in enhanced_content:
           page_number = page_data.get('page_number', 1)
           
           # Tabloları işle
           for table in page_data.get('tables', []):
               table_text = table.get('text_representation', '')
               if table_text and len(table_text.strip()) > 20:
                   try:
                       # Tablo için özel chunk oluştur
                       embedding = self._generate_chunk_embedding(table_text)
                       
                       KnowledgeChunk.objects.create(
                           source=document,
                           content=f"[TABLO] {table_text}",
                           content_length=len(table_text),
                           page_number=page_number,
                           section_title="Tablo Verisi",
                           technical_level='admin',  # Tablolar genelde admin seviyesi
                           embedding=embedding,
                           embedding_model=self.embedding_service.model_name,
                           metadata={'content_type': 'table'}
                       )
                       
                       chunks_created += 1
                       
                   except Exception as e:
                       logger.error(f"Tablo chunk oluşturma hatası: {e}")
       
       return chunks_created
   
   def _generate_chunk_embedding(self, text: str) -> List[float]:
       """Chunk için embedding oluştur - cache'li"""
       try:
           # Cache kontrolü
           content_hash = generate_hash(text)
           cached_embedding = embedding_cache.get_embedding(content_hash)
           
           if cached_embedding:
               return cached_embedding
           
           # Yeni embedding oluştur
           embedding = self.embedding_service.generate_embedding(text)
           
           # Cache'e kaydet
           embedding_cache.set_embedding(content_hash, embedding)
           
           return embedding
           
       except Exception as e:
           logger.error(f"Embedding oluşturma hatası: {e}")
           raise EmbeddingError(
               f"Embedding oluşturulamadı: {str(e)}",
               content_hash=generate_hash(text)
           )
   
   def _determine_chunk_size(self, technical_level: str) -> int:
       """Teknik seviyeye göre chunk boyutu belirle"""
       sizes = {
           'user': 800,        # Son kullanıcı - küçük parçalar
           'admin': 1200,      # Yönetici - orta boyut
           'developer': 1600,  # Geliştirici - büyük parçalar
           'mixed': 1000       # Karışık - orta
       }
       return sizes.get(technical_level, 1000)
   
   def _extract_section_title(self, text: str) -> Optional[str]:
       """Metin içinden bölüm başlığını çıkar"""
       lines = text.split('\n')
       
       for line in lines[:5]:  # İlk 5 satırı kontrol et
           line = line.strip()
           if (len(line) < 100 and 
               len(line) > 5 and 
               not line.endswith('.') and
               any(word in line.lower() for word in ['bölüm', 'chapter', 'section', 'adım', 'step'])):
               return line
       
       return None
   
   def _update_search_index(self, document: DocumentSource):
       """Search index'ini güncelle"""
       try:
           # Bu dokümana ait chunk'ları search service'e bildir
           chunks = KnowledgeChunk.objects.filter(source=document, is_active=True)
           
           for chunk in chunks:
               self.search_service.index_chunk(chunk)
           
           logger.info(f"Search index güncellendi: {document.title}")
           
       except Exception as e:
           logger.error(f"Search index güncelleme hatası: {e}")
   
   def reprocess_document(self, document_id: str, force: bool = False) -> Dict[str, Any]:
       """Dökümanı yeniden işle"""
       try:
           document = DocumentSource.objects.get(id=document_id)
           
           # Force değilse ve document zaten işlenmişse skip
           if not force and document.processing_status == 'completed':
               return {
                   'success': True,
                   'message': 'Döküman zaten işlenmiş',
                   'skipped': True
               }
           
           # Mevcut chunk'ları sil
           deleted_count = KnowledgeChunk.objects.filter(source=document).delete()[0]
           logger.info(f"Silinen chunk sayısı: {deleted_count}")
           
           # Yeniden işle
           result = self.process_document(document_id)
           result['reprocessed'] = True
           result['deleted_chunks'] = deleted_count
           
           return result
           
       except DocumentSource.DoesNotExist:
           raise ValidationException(
               "Döküman bulunamadı",
               field="document_id",
               value=document_id
           )
   
   def batch_process_documents(self, document_ids: List[str]) -> Dict[str, Any]:
       """Toplu döküman işleme"""
       results = {
           'total': len(document_ids),
           'processed': 0,
           'failed': 0,
           'details': []
       }
       
       for doc_id in document_ids:
           try:
               result = self.process_document(doc_id)
               results['processed'] += 1
               results['details'].append({
                   'document_id': doc_id,
                   'status': 'success',
                   'chunks_created': result.get('chunks_created', 0)
               })
               
           except Exception as e:
               results['failed'] += 1
               results['details'].append({
                   'document_id': doc_id,
                   'status': 'error',
                   'error': str(e)
               })
               logger.error(f"Batch işleme hatası - Doc ID: {doc_id}, Hata: {e}")
       
       return results
   
   def get_processing_stats(self) -> Dict[str, Any]:
       """İşleme istatistiklerini al"""
       from django.db.models import Count, Avg
       
       stats = DocumentSource.objects.aggregate(
           total_documents=Count('id'),
           completed=Count('id', filter=models.Q(processing_status='completed')),
           processing=Count('id', filter=models.Q(processing_status='processing')),
           failed=Count('id', filter=models.Q(processing_status='failed')),
           pending=Count('id', filter=models.Q(processing_status='pending'))
       )
       
       # Chunk istatistikleri
       chunk_stats = KnowledgeChunk.objects.aggregate(
           total_chunks=Count('id'),
           avg_chunk_size=Avg('content_length'),
           total_content_length=Sum('content_length')
       )
       
       stats.update(chunk_stats)
       
       return stats
   
   def optimize_chunk_relevance_scores(self) -> Dict[str, Any]:
       """Chunk relevance skorlarını optimize et"""
       logger.info("Chunk relevance skorları optimize ediliyor...")
       
       updated_count = 0
       
       # Kullanım sayısına göre skorları güncelle
       chunks = KnowledgeChunk.objects.filter(is_active=True)
       
       for chunk in chunks:
           try:
               # Kullanım bazlı skor
               usage_score = min(chunk.usage_count / 10.0, 1.0)
               
               # İçerik kalitesi skoru
               quality_score = self._calculate_content_quality_score(chunk.content)
               
               # SAP modül uyumu skoru
               module_score = 1.0 if chunk.sap_module else 0.8
               
               # Genel relevance skoru
               new_score = (usage_score * 0.4 + quality_score * 0.4 + module_score * 0.2)
               
               if abs(chunk.relevance_score - new_score) > 0.1:
                   chunk.relevance_score = new_score
                   chunk.save(update_fields=['relevance_score'])
                   updated_count += 1
                   
           except Exception as e:
               logger.error(f"Chunk skor güncelleme hatası: {e}")
       
       logger.info(f"Güncellenen chunk sayısı: {updated_count}")
       
       return {
           'updated_chunks': updated_count,
           'total_chunks': chunks.count()
       }
   
   def _calculate_content_quality_score(self, content: str) -> float:
       """İçerik kalitesi skorunu hesapla"""
       if not content:
           return 0.0
       
       score = 0.5  # Base score
       
       # Uzunluk skoru
       length = len(content)
       if 100 <= length <= 1500:
           score += 0.2
       elif length > 1500:
           score += 0.1
       
       # SAP terminoloji varlığı
       sap_terms = ['sap', 'erp', 'hana', 'business one', 'mali', 'muhasebe', 'fatura']
       term_count = sum(1 for term in sap_terms if term in content.lower())
       score += min(term_count * 0.05, 0.2)
       
       # Yapılandırılmış içerik varlığı
       if any(indicator in content.lower() for indicator in ['adım', 'step', '1.', '2.', 'öncelikle']):
           score += 0.1
       
       return min(score, 1.0)


# Celery Tasks
@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
   """Asenkron döküman işleme task'ı"""
   try:
       processor = DocumentProcessingService()
       result = processor.process_document(document_id)
       
       logger.info(f"Celery task tamamlandı - Doc ID: {document_id}")
       return result
       
   except Exception as e:
       logger.error(f"Celery task hatası - Doc ID: {document_id}, Hata: {e}")
       
       # Retry logic
       if self.request.retries < self.max_retries:
           # Exponential backoff
           countdown = 2 ** self.request.retries
           raise self.retry(countdown=countdown, exc=e)
       
       # Max retry aşıldı, document'ı failed olarak işaretle
       try:
           document = DocumentSource.objects.get(id=document_id)
           document.processing_status = 'failed'
           document.processing_error = str(e)
           document.save(update_fields=['processing_status', 'processing_error'])
       except:
           pass
       
       raise e


@shared_task
def batch_process_documents_task(document_ids: List[str]):
   """Toplu döküman işleme task'ı"""
   processor = DocumentProcessingService()
   return processor.batch_process_documents(document_ids)


@shared_task
def optimize_chunk_scores_task():
   """Chunk skorlarını optimize etme task'ı"""
   processor = DocumentProcessingService()
   return processor.optimize_chunk_relevance_scores()


@shared_task
def cleanup_failed_documents_task():
   """Başarısız dökümanları temizleme task'ı"""
   from datetime import timedelta
   
   # 24 saatten eski failed dökümanları sil
   cutoff_date = timezone.now() - timedelta(hours=24)
   
   failed_docs = DocumentSource.objects.filter(
       processing_status='failed',
       updated_at__lt=cutoff_date
   )
   
   deleted_count = 0
   for doc in failed_docs:
       try:
           # Chunk'ları sil
           KnowledgeChunk.objects.filter(source=doc).delete()
           
           # Dosyayı sil
           if doc.file_path:
               file_manager = FileManager()
               file_manager.delete_file(doc.file_path.name)
           
           # Document'ı sil
           doc.delete()
           deleted_count += 1
           
       except Exception as e:
           logger.error(f"Failed document silme hatası: {e}")
   
   logger.info(f"Temizlenen failed document sayısı: {deleted_count}")
   return {'deleted_count': deleted_count}


# Health check fonksiyonları
def check_document_processing_health() -> Dict[str, Any]:
   """Döküman işleme sistem sağlığı kontrolü"""
   health_data = {
       'status': 'healthy',
       'checks': {}
   }
   
   try:
       # Processing queue kontrolü
       processing_count = DocumentSource.objects.filter(
           processing_status='processing'
       ).count()
       
       # Stuck documents kontrolü (2 saatten uzun processing'de)
       from datetime import timedelta
       stuck_threshold = timezone.now() - timedelta(hours=2)
       stuck_count = DocumentSource.objects.filter(
           processing_status='processing',
           updated_at__lt=stuck_threshold
       ).count()
       
       health_data['checks'] = {
           'processing_queue_size': processing_count,
           'stuck_documents': stuck_count,
           'embedding_service': 'healthy',  # Embedding service kontrolü eklenebilir
           'file_storage': 'healthy'  # File storage kontrolü eklenebilir
       }
       
       # Kritik durumlar
       if stuck_count > 0:
           health_data['status'] = 'warning'
       
       if processing_count > 10:  # Çok fazla pending
           health_data['status'] = 'warning'
           
   except Exception as e:
       health_data['status'] = 'error'
       health_data['error'] = str(e)
   
   return health_data
