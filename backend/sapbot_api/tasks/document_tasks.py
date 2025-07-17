# backend/sapbot_api/tasks/document_tasks.py
import time
import traceback
from typing import Dict, List, Any, Optional, Tuple
from datetime import  timedelta
from celery import shared_task, Task

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.files.storage import default_storage
import logging

from sapbot_api.models import DocumentSource, KnowledgeChunk
from sapbot_api.utils.file_handlers import (
    PDFProcessor, VideoProcessor, FileManager
)
from sapbot_api.utils.text_processing import (
    TextAnalyzer, TextChunker
)
from sapbot_api.utils.exceptions import (
    DocumentProcessingError, EmbeddingError
)
from sapbot_api.utils.cache_utils import embedding_cache
from sapbot_api.utils.helpers import clean_text, generate_hash

logger = logging.getLogger(__name__)


class DocumentProcessingTask(Task):
    """Döküman işleme için özel task sınıfı"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Task başarısız olduğunda çalışır"""
        document_id = args[0] if args else kwargs.get('document_id')
        
        if document_id:
            try:
                doc = DocumentSource.objects.get(id=document_id)
                doc.processing_status = 'failed'
                doc.processing_error = str(exc)[:1000]  # İlk 1000 karakter
                doc.save(update_fields=['processing_status', 'processing_error'])
                
                logger.error(f"Document processing failed for {document_id}: {exc}")
                
            except DocumentSource.DoesNotExist:
                logger.error(f"Document {document_id} not found during failure handling")
        
        # Slack/email notification gönder
        self.send_failure_notification(document_id, exc, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Task başarılı olduğunda çalışır"""
        document_id = args[0] if args else kwargs.get('document_id')
        logger.info(f"Document processing completed successfully for {document_id}")
    
    def send_failure_notification(self, document_id: str, exception: Exception, einfo):
        """Başarısızlık bildirimi gönder"""
        try:
            # Slack webhook (opsiyonel)
            slack_webhook = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            if slack_webhook:
                import requests
                
                payload = {
                    "text": f"🚨 SAPBot Document Processing Failed",
                    "attachments": [{
                        "color": "danger",
                        "fields": [
                            {"title": "Document ID", "value": str(document_id), "short": True},
                            {"title": "Error", "value": str(exception)[:200], "short": False},
                            {"title": "Time", "value": timezone.now().strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                        ]
                    }]
                }
                
                requests.post(slack_webhook, json=payload, timeout=5)
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


@shared_task(bind=True, base=DocumentProcessingTask)
def process_document(self, document_id: str) -> Dict[str, Any]:
    """
    Ana döküman işleme task'ı
    
    Args:
        document_id: İşlenecek dökümanın ID'si
        
    Returns:
        Dict[str, Any]: İşleme sonucu
    """
    start_time = time.time()
    
    try:
        # Dökümanı al
        try:
            document = DocumentSource.objects.get(id=document_id)
        except DocumentSource.DoesNotExist:
            raise DocumentProcessingError(f"Document not found: {document_id}")
        
        # Durumu güncelle
        document.processing_status = 'processing'
        document.save(update_fields=['processing_status'])
        
        logger.info(f"Starting document processing: {document.title} ({document.document_type})")
        
        # Dosya kontrolü
        if not document.file_path or not default_storage.exists(document.file_path.name):
            raise DocumentProcessingError("File not found or accessible")
        
        # İşleme tipine göre dal
        if document.document_type == 'pdf':
            result = process_pdf_document.delay(document_id)
        elif document.document_type == 'video':
            result = process_video_document.delay(document_id)
        elif document.document_type == 'manual':
            result = process_manual_document.delay(document_id)
        else:
            raise DocumentProcessingError(f"Unsupported document type: {document.document_type}")
        
        # Child task'ın tamamlanmasını bekle
        final_result = result.get(timeout=1800)  # 30 dakika timeout
        
        # Final durumu güncelle
        document.refresh_from_db()
        if document.processing_status != 'failed':
            document.processing_status = 'completed'
            document.processed_at = timezone.now()
            document.save(update_fields=['processing_status', 'processed_at'])
        
        processing_time = time.time() - start_time
        
        logger.info(f"Document processing completed: {document_id} in {processing_time:.2f}s")
        
        return {
            'document_id': document_id,
            'status': 'completed',
            'processing_time': processing_time,
            'chunks_created': final_result.get('chunks_created', 0),
            'message': 'Document processed successfully'
        }
        
    except Exception as e:
        logger.error(f"Document processing error: {e}\n{traceback.format_exc()}")
        raise DocumentProcessingError(f"Processing failed: {str(e)}")


@shared_task(bind=True, base=DocumentProcessingTask)
def process_pdf_document(self, document_id: str) -> Dict[str, Any]:
    """
    PDF döküman işleme
    
    Args:
        document_id: PDF dökümanın ID'si
        
    Returns:
        Dict[str, Any]: İşleme sonucu
    """
    try:
        document = DocumentSource.objects.get(id=document_id)
        processor = PDFProcessor()
        file_manager = FileManager()
        
        # Dosya yolunu al
        file_path = document.file_path.path
        
        logger.info(f"Processing PDF: {document.title}")
        
        # PDF'den metin çıkar
        extraction_result = processor.extract_text(file_path)
        
        if not extraction_result['text_content']:
            raise DocumentProcessingError("No text content extracted from PDF")
        
        # Metin analizi ve chunk'lara bölme
        chunks_created = 0
        
        with transaction.atomic():
            # Mevcut chunk'ları temizle
            KnowledgeChunk.objects.filter(source=document).delete()
            
            for page_data in extraction_result['text_content']:
                page_number = page_data['page_number']
                page_text = page_data['text']
                
                if len(page_text.strip()) < 50:  # Çok kısa sayfa, skip
                    continue
                
                # Sayfayı chunk'lara böl
                page_chunks = create_chunks_from_text(
                    text=page_text,
                    source=document,
                    page_number=page_number,
                    section_title=extract_section_title(page_text)
                )
                
                chunks_created += len(page_chunks)
        
        # OCR varsa işle (opsiyonel)
        if hasattr(processor, 'extract_images_with_ocr'):
            try:
                ocr_results = processor.extract_images_with_ocr(file_path)
                if ocr_results:
                    logger.info(f"OCR extracted {len(ocr_results)} image texts")
            except Exception as e:
                logger.warning(f"OCR processing failed: {e}")
        
        return {
            'document_id': document_id,
            'chunks_created': chunks_created,
            'total_pages': extraction_result['total_pages'],
            'total_characters': extraction_result['total_characters'],
            'metadata': extraction_result['metadata']
        }
        
    except Exception as e:
        logger.error(f"PDF processing error: {e}")
        raise DocumentProcessingError(f"PDF processing failed: {str(e)}")


@shared_task(bind=True, base=DocumentProcessingTask)
def process_video_document(self, document_id: str) -> Dict[str, Any]:
    """
    Video döküman işleme (transkript çıkarma)
    
    Args:
        document_id: Video dökümanın ID'si
        
    Returns:
        Dict[str, Any]: İşleme sonucu
    """
    try:
        document = DocumentSource.objects.get(id=document_id)
        processor = VideoProcessor()
        
        file_path = document.file_path.path
        
        logger.info(f"Processing video: {document.title}")
        
        # Video'dan transkript çıkar
        transcript_result = processor.extract_transcript(file_path)
        
        if not transcript_result['full_text'].strip():
            raise DocumentProcessingError("No transcript could be extracted from video")
        
        chunks_created = 0
        
        with transaction.atomic():
            # Mevcut chunk'ları temizle
            KnowledgeChunk.objects.filter(source=document).delete()
            
            # Segmentleri chunk'lara dönüştür
            for i, segment in enumerate(transcript_result['segments']):
                if len(segment['text'].strip()) < 20:  # Çok kısa segment
                    continue
                
                # Timestamp bilgisi ile chunk oluştur
                chunk_text = f"[{format_timestamp(segment['start'])} - {format_timestamp(segment['end'])}]\n{segment['text']}"
                
                chunk_data = create_single_chunk(
                    text=chunk_text,
                    source=document,
                    page_number=None,
                    section_title=f"Segment {i+1}",
                    additional_metadata={
                        'start_time': segment['start'],
                        'end_time': segment['end'],
                        'confidence': segment.get('confidence', 0.0)
                    }
                )
                
                if chunk_data:
                    chunks_created += 1
            
            # Tam transkript'i de bir chunk olarak ekle
            full_transcript_chunk = create_single_chunk(
                text=transcript_result['full_text'],
                source=document,
                page_number=1,
                section_title="Full Transcript"
            )
            
            if full_transcript_chunk:
                chunks_created += 1
        
        return {
            'document_id': document_id,
            'chunks_created': chunks_created,
            'duration': transcript_result['duration'],
            'segments_count': len(transcript_result['segments']),
            'language': transcript_result.get('language', 'tr'),
            'video_info': transcript_result['video_info']
        }
        
    except Exception as e:
        logger.error(f"Video processing error: {e}")
        raise DocumentProcessingError(f"Video processing failed: {str(e)}")


@shared_task(bind=True, base=DocumentProcessingTask)
def process_manual_document(self, document_id: str) -> Dict[str, Any]:
    """
    Manuel döküman işleme (önceden girilmiş metin)
    
    Args:
        document_id: Manuel dökümanın ID'si
        
    Returns:
        Dict[str, Any]: İşleme sonucu
    """
    try:
        document = DocumentSource.objects.get(id=document_id)
        
        # Manuel döküman için metadata'dan metin al
        manual_text = document.metadata.get('content', '')
        
        if not manual_text or len(manual_text.strip()) < 10:
            raise DocumentProcessingError("No manual content found or content too short")
        
        logger.info(f"Processing manual document: {document.title}")
        
        chunks_created = 0
        
        with transaction.atomic():
            # Mevcut chunk'ları temizle
            KnowledgeChunk.objects.filter(source=document).delete()
            
            # Metni chunk'lara böl
            chunks = create_chunks_from_text(
                text=manual_text,
                source=document,
                page_number=1,
                section_title=document.title
            )
            
            chunks_created = len(chunks)
        
        return {
            'document_id': document_id,
            'chunks_created': chunks_created,
            'total_characters': len(manual_text),
            'processing_type': 'manual'
        }
        
    except Exception as e:
        logger.error(f"Manual document processing error: {e}")
        raise DocumentProcessingError(f"Manual processing failed: {str(e)}")


@shared_task(bind=True)
def generate_embeddings_for_chunk(self, chunk_id: str) -> Dict[str, Any]:
    """
    Tek chunk için embedding oluştur
    
    Args:
        chunk_id: Chunk ID'si
        
    Returns:
        Dict[str, Any]: Embedding sonucu
    """
    try:
        chunk = KnowledgeChunk.objects.get(id=chunk_id)
        
        # Cache'den kontrol et
        content_hash = chunk.content_hash
        cached_embedding = embedding_cache.get_embedding(content_hash)
        
        if cached_embedding:
            chunk.embedding = cached_embedding
            chunk.embedding_model = "cached"
            chunk.save(update_fields=['embedding', 'embedding_model'])
            
            return {
                'chunk_id': chunk_id,
                'status': 'cached',
                'embedding_dimension': len(cached_embedding)
            }
        
        # Yeni embedding oluştur
        try:
            from sentence_transformers import SentenceTransformer
            model_name = getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            model = SentenceTransformer(model_name)
            embedding_method = 'sentence_transformers'
        except ImportError:
            logger.warning("sentence-transformers not installed, using OpenAI embeddings")
            embedding_method = 'openai'
        
        # Temiz metin hazırla
        clean_content = clean_text(chunk.content)
        
        # Embedding oluştur
        if embedding_method == 'sentence_transformers':
            embedding = model.encode(clean_content)
            embedding_list = embedding.tolist()
            model_used = model_name
        else:
            # OpenAI embeddings alternatifi
            embedding_list, model_used = generate_openai_embedding(clean_content)
        
        # Chunk'ı güncelle
        chunk.embedding = embedding_list
        chunk.embedding_model = model_used
        chunk.save(update_fields=['embedding', 'embedding_model'])
        
        # Cache'e kaydet
        embedding_cache.set_embedding(content_hash, embedding_list)
        
        logger.info(f"Generated embedding for chunk {chunk_id}")
        
        return {
            'chunk_id': chunk_id,
            'status': 'generated',
            'embedding_dimension': len(embedding_list),
            'model_used': model_used
        }
        
    except Exception as e:
        logger.error(f"Embedding generation error for chunk {chunk_id}: {e}")
        raise EmbeddingError(f"Embedding generation failed: {str(e)}")


@shared_task(bind=True)
def batch_generate_embeddings(self, document_id: str) -> Dict[str, Any]:
    """
    Dökümanın tüm chunk'ları için toplu embedding oluştur
    
    Args:
        document_id: Döküman ID'si
        
    Returns:
        Dict[str, Any]: Toplu embedding sonucu
    """
    try:
        document = DocumentSource.objects.get(id=document_id)
        chunks = KnowledgeChunk.objects.filter(
            source=document,
            embedding__isnull=True
        )
        
        if not chunks.exists():
            return {
                'document_id': document_id,
                'status': 'no_chunks_to_process',
                'processed_count': 0
            }
        
        logger.info(f"Generating embeddings for {chunks.count()} chunks")
        
        # Embedding method'unu belirle
        try:
            from sentence_transformers import SentenceTransformer
            model_name = getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            model = SentenceTransformer(model_name)
            embedding_method = 'sentence_transformers'
        except ImportError:
            logger.warning("sentence-transformers not installed, using OpenAI embeddings")
            embedding_method = 'openai'
            model = None
            model_name = 'openai-text-embedding-ada-002'
        
        # Batch processing için chunk'ları grupla
        batch_size = 32 if embedding_method == 'sentence_transformers' else 10  # OpenAI için daha küçük batch
        processed_count = 0
        failed_count = 0
        
        for i in range(0, chunks.count(), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            try:
                # Batch metinleri hazırla
                batch_texts = []
                batch_chunk_ids = []
                
                for chunk in batch_chunks:
                    # Cache kontrolü
                    cached_embedding = embedding_cache.get_embedding(chunk.content_hash)
                    if cached_embedding:
                        chunk.embedding = cached_embedding
                        chunk.embedding_model = "cached"
                        chunk.save(update_fields=['embedding', 'embedding_model'])
                        processed_count += 1
                        continue
                    
                    clean_content = clean_text(chunk.content)
                    batch_texts.append(clean_content)
                    batch_chunk_ids.append(chunk.id)
                
                if batch_texts:
                    # Batch embedding oluştur
                    if embedding_method == 'sentence_transformers':
                        embeddings = model.encode(batch_texts)
                    else:
                        # OpenAI batch processing
                        embeddings = []
                        for text in batch_texts:
                            embedding, _ = generate_openai_embedding(text)
                            embeddings.append(embedding)
                    
                    # Sonuçları kaydet
                    for j, chunk_id in enumerate(batch_chunk_ids):
                        try:
                            chunk = KnowledgeChunk.objects.get(id=chunk_id)
                            
                            if embedding_method == 'sentence_transformers':
                                embedding_list = embeddings[j].tolist()
                            else:
                                embedding_list = embeddings[j]
                            
                            chunk.embedding = embedding_list
                            chunk.embedding_model = model_name
                            chunk.save(update_fields=['embedding', 'embedding_model'])
                            
                            # Cache'e kaydet
                            embedding_cache.set_embedding(chunk.content_hash, embedding_list)
                            
                            processed_count += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to save embedding for chunk {chunk_id}: {e}")
                            failed_count += 1
                
                # Progress update
                if processed_count % 50 == 0:
                    logger.info(f"Processed {processed_count} embeddings...")
                    
            except Exception as e:
                logger.error(f"Batch embedding error: {e}")
                failed_count += len(batch_chunks)
        
        return {
            'document_id': document_id,
            'status': 'completed',
            'processed_count': processed_count,
            'failed_count': failed_count,
            'model_used': model_name
        }
        
    except Exception as e:
        logger.error(f"Batch embedding generation error: {e}")
        raise EmbeddingError(f"Batch embedding failed: {str(e)}")


@shared_task
def cleanup_failed_documents():
    """Başarısız dökümanları temizle"""
    try:
        # 24 saatten uzun süredir processing durumunda kalanlar
        stale_cutoff = timezone.now() - timedelta(hours=24)
        stale_docs = DocumentSource.objects.filter(
            processing_status='processing',
            updated_at__lt=stale_cutoff
        )
        
        stale_count = 0
        for doc in stale_docs:
            doc.processing_status = 'failed'
            doc.processing_error = 'Processing timeout (>24h)'
            doc.save(update_fields=['processing_status', 'processing_error'])
            stale_count += 1
        
        # 7 günden eski başarısız dökümanları sil
        failed_cutoff = timezone.now() - timedelta(days=7)
        old_failed = DocumentSource.objects.filter(
            processing_status='failed',
            updated_at__lt=failed_cutoff
        )
        
        deleted_count = 0
        for doc in old_failed:
            # İlişkili chunk'ları da sil
            KnowledgeChunk.objects.filter(source=doc).delete()
            
            # Dosyayı fiziksel olarak sil
            if doc.file_path and default_storage.exists(doc.file_path.name):
                default_storage.delete(doc.file_path.name)
            
            doc.delete()
            deleted_count += 1
        
        logger.info(f"Cleanup completed: {stale_count} stale, {deleted_count} deleted")
        
        return {
            'stale_marked_as_failed': stale_count,
            'old_failed_deleted': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return {'error': str(e)}


@shared_task
def reprocess_document(document_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Dökümanı yeniden işle
    
    Args:
        document_id: Döküman ID'si
        force: Zorla yeniden işle (completed olanları da)
        
    Returns:
        Dict[str, Any]: Yeniden işleme sonucu
    """
    try:
        document = DocumentSource.objects.get(id=document_id)
        
        # Force değilse ve completed ise skip
        if not force and document.processing_status == 'completed':
            return {
                'document_id': document_id,
                'status': 'skipped',
                'message': 'Document already processed (use force=True to reprocess)'
            }
        
        # Mevcut chunk'ları temizle
        KnowledgeChunk.objects.filter(source=document).delete()
        
        # Durumu sıfırla
        document.processing_status = 'pending'
        document.processing_error = None
        document.processed_at = None
        document.save(update_fields=['processing_status', 'processing_error', 'processed_at'])
        
        # Yeniden işle
        result = process_document.delay(document_id)
        
        return {
            'document_id': document_id,
            'status': 'reprocessing_started',
            'task_id': result.id
        }
        
    except DocumentSource.DoesNotExist:
        raise DocumentProcessingError(f"Document not found: {document_id}")
    except Exception as e:
        logger.error(f"Reprocess error: {e}")
        raise DocumentProcessingError(f"Reprocess failed: {str(e)}")


# Helper functions

def generate_openai_embedding(text: str) -> Tuple[List[float], str]:
    """
    OpenAI API ile embedding oluştur
    
    Args:
        text: Embedding oluşturulacak metin
        
    Returns:
        Tuple[List[float], str]: (embedding, model_name)
    """
    try:
        import openai
        from django.conf import settings
        
        # OpenAI client setup
        openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if not openai.api_key:
            raise EmbeddingError("OpenAI API key not configured")
        
        # Metin uzunluğunu kontrol et (OpenAI limit: ~8000 token)
        if len(text) > 30000:  # Yaklaşık 8000 token
            text = text[:30000]
        
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        
        embedding = response.data[0].embedding
        model_name = "openai-text-embedding-ada-002"
        
        return embedding, model_name
        
    except ImportError:
        raise EmbeddingError("OpenAI library not installed. Run: pip install openai")
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        raise EmbeddingError(f"OpenAI embedding failed: {str(e)}")


def get_simple_embedding(text: str) -> Tuple[List[float], str]:
    """
    Basit TF-IDF embedding alternatifi (fallback)
    
    Args:
        text: Embedding oluşturulacak metin
        
    Returns:
        Tuple[List[float], str]: (embedding, model_name)
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        
        # Basit TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=384,  # sentence-transformers ile uyumlu dimension
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Tek metin için corpus oluştur (dummy text'ler ekle)
        corpus = [
            text,
            "sample text for fitting",
            "another sample text",
            "sap business one sample"
        ]
        
        # Fit ve transform
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # İlk dökümanın embedding'ini al
        embedding_sparse = tfidf_matrix[0]
        embedding_dense = embedding_sparse.toarray().flatten()
        
        # Normalize et
        norm = np.linalg.norm(embedding_dense)
        if norm > 0:
            embedding_dense = embedding_dense / norm
        
        return embedding_dense.tolist(), "tfidf-simple"
        
    except ImportError:
        raise EmbeddingError("scikit-learn not installed for TF-IDF fallback")
    except Exception as e:
        logger.error(f"TF-IDF embedding error: {e}")
        raise EmbeddingError(f"TF-IDF embedding failed: {str(e)}")


def create_chunks_from_text(
    text: str, 
    source: DocumentSource, 
    page_number: Optional[int] = None,
    section_title: Optional[str] = None,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[KnowledgeChunk]:
    """Metinden chunk'lar oluştur"""
    
    # Metin analizi
    analysis = TextAnalyzer.analyze_text(text)
    
    # Chunk'lara böl
    chunker = TextChunker()
    chunk_results = chunker.intelligent_split(
        text=text,
        max_chunk_size=chunk_size,
        overlap=overlap,
        preserve_paragraphs=True
    )
    
    chunks = []
    
    for chunk_result in chunk_results:
        chunk_text = chunk_result.text
        
        # Çok kısa chunk'ları skip et
        if len(chunk_text.strip()) < 50:
            continue
        
        chunk = create_single_chunk(
            text=chunk_text,
            source=source,
            page_number=page_number,
            section_title=section_title,
            analysis=analysis
        )
        
        if chunk:
            chunks.append(chunk)
    
    return chunks


def create_single_chunk(
    text: str,
    source: DocumentSource,
    page_number: Optional[int] = None,
    section_title: Optional[str] = None,
    analysis: Optional[Any] = None,
    additional_metadata: Optional[Dict] = None
) -> Optional[KnowledgeChunk]:
    """Tek chunk oluştur"""
    
    try:
        # Metin analizi (yoksa yap)
        if not analysis:
            analysis = TextAnalyzer.analyze_text(text)
        
        # İçerik hash'i
        content_hash = generate_hash(text)
        
        # Duplicate kontrolü
        if KnowledgeChunk.objects.filter(content_hash=content_hash).exists():
            logger.debug(f"Duplicate chunk skipped: {content_hash[:8]}")
            return None
        
        # SAP modül tespiti
        sap_module = None
        if analysis.sap_modules:
            sap_module = analysis.sap_modules[0]  # İlk modül
        
        # Anahtar kelimeler
        keywords = analysis.keywords[:10]  # İlk 10 kelime
        
        # Metadata hazırla
        metadata = {
            'language': analysis.language,
            'word_count': analysis.word_count,
            'char_count': analysis.char_count,
            'confidence': analysis.confidence
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Chunk oluştur
        chunk = KnowledgeChunk.objects.create(
            source=source,
            content=text,
            content_hash=content_hash,
            content_length=len(text),
            page_number=page_number,
            section_title=section_title,
            sap_module=sap_module,
            technical_level=analysis.technical_level,
            keywords=keywords,
            relevance_score=1.0,  # Default
        )
        
        # Embedding'i asenkron oluştur
        generate_embeddings_for_chunk.delay(str(chunk.id))
        
        return chunk
        
    except Exception as e:
        logger.error(f"Chunk creation error: {e}")
        return None


def extract_section_title(text: str) -> Optional[str]:
    """Metinden bölüm başlığı çıkar"""
    lines = text.split('\n')
    
    for line in lines[:5]:  # İlk 5 satırı kontrol et
        line = line.strip()
        
        # Başlık pattern'ları
        if (len(line) < 100 and 
            len(line) > 5 and
            any(keyword in line.lower() for keyword in ['bölüm', 'chapter', 'section', 'adım'])):
            return line
    
    return None


def format_timestamp(seconds: float) -> str:
    """Saniyeyi HH:MM:SS formatına çevir"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


# Monitoring ve health check tasks

@shared_task
def document_processing_health_check() -> Dict[str, Any]:
    """Döküman işleme sistemi sağlık kontrolü"""
    try:
        # İstatistikler
        total_docs = DocumentSource.objects.count()
        pending_docs = DocumentSource.objects.filter(processing_status='pending').count()
        processing_docs = DocumentSource.objects.filter(processing_status='processing').count()
        completed_docs = DocumentSource.objects.filter(processing_status='completed').count()
        failed_docs = DocumentSource.objects.filter(processing_status='failed').count()
        
        # Son 24 saatteki aktivite
        last_24h = timezone.now() - timedelta(hours=24)
        recent_processed = DocumentSource.objects.filter(
            processed_at__gte=last_24h
        ).count()
        
        # Chunk istatistikleri
        total_chunks = KnowledgeChunk.objects.count()
        chunks_with_embeddings = KnowledgeChunk.objects.filter(
            embedding__isnull=False
        ).count()
        
        # Sağlık durumu
        health_status = "healthy"
        issues = []
        
        if pending_docs > 50:
            health_status = "warning"
            issues.append(f"High pending queue: {pending_docs} documents")
        
        if processing_docs > 10:
            health_status = "warning"
            issues.append(f"Many documents processing: {processing_docs}")
        
        if failed_docs > (total_docs * 0.1):  # %10'dan fazla başarısız
            health_status = "critical"
            issues.append(f"High failure rate: {failed_docs}/{total_docs}")
        
        embedding_coverage = (chunks_with_embeddings / total_chunks * 100) if total_chunks > 0 else 100
        if embedding_coverage < 90:
            health_status = "warning"
            issues.append(f"Low embedding coverage: {embedding_coverage:.1f}%")
        
        return {
            'status': health_status,
            'issues': issues,
            'statistics': {
                'total_documents': total_docs,
                'pending': pending_docs,
                'processing': processing_docs,
                'completed': completed_docs,
                'failed': failed_docs,
                'recent_processed_24h': recent_processed,
                'total_chunks': total_chunks,
                'chunks_with_embeddings': chunks_with_embeddings,
                'embedding_coverage_percent': round(embedding_coverage, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            'status': 'critical',
            'issues': [f"Health check failed: {str(e)}"],
            'statistics': {}
        }