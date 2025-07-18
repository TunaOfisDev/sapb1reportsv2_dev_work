# backend/sapbot_api/services/embedding_service.py
"""
SAPBot API Embedding Service

Bu servis, metin içeriklerini vector embeddings'e dönüştürür ve cache'ler.
Çok dilli (TR/EN) SAP dokümantasyonu için optimize edilmiştir.
"""

import hashlib
import logging
import time
from typing import List, Dict, Optional, Union, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from sentence_transformers import SentenceTransformer
from openai import OpenAI
import tiktoken
from django.conf import settings
from django.core.cache import cache

from ..utils.cache_utils import EmbeddingCacheManager, embedding_cache
from ..utils.exceptions import EmbeddingError, ExternalServiceError, ConfigurationError
from ..utils.text_processing import TextAnalyzer, clean_text, detect_language
from ..utils.helpers import generate_hash, time_ago

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
   """Embedding sonucu"""
   embedding: List[float]
   model_used: str
   dimension: int
   processing_time: float
   token_count: Optional[int] = None
   cost_estimate: Optional[float] = None
   cache_hit: bool = False
   content_hash: str = ""


@dataclass
class BatchEmbeddingResult:
   """Toplu embedding sonucu"""
   embeddings: List[List[float]]
   results: List[EmbeddingResult]
   total_processing_time: float
   cache_hit_rate: float
   failed_count: int
   success_count: int


class EmbeddingModel:
   """Embedding modeli wrapper'ı"""
   
   def __init__(self, model_name: str, dimension: int, max_tokens: int = 512):
       self.model_name = model_name
       self.dimension = dimension
       self.max_tokens = max_tokens
       self._model = None
       self._tokenizer = None
   
   @property
   def model(self):
       if self._model is None:
           self._load_model()
       return self._model
   
   def _load_model(self):
       """Model yükleme - lazy loading"""
       try:
           if self.model_name.startswith('openai/'):
               # OpenAI modeli
               self._model = OpenAI(api_key=settings.OPENAI_API_KEY)
               self._tokenizer = tiktoken.get_encoding("cl100k_base")
           else:
               # Sentence Transformers modeli
               self._model = SentenceTransformer(self.model_name)
               
           logger.info(f"Embedding modeli yüklendi: {self.model_name}")
           
       except Exception as e:
           logger.error(f"Model yükleme hatası ({self.model_name}): {e}")
           raise ConfigurationError(f"Embedding modeli yüklenemedi: {self.model_name}")
   
   def encode(self, texts: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
       """Metin encode etme"""
       if self.model_name.startswith('openai/'):
           return self._encode_openai(texts, **kwargs)
       else:
           return self._encode_sentence_transformer(texts, **kwargs)
   
   def _encode_openai(self, texts: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
       """OpenAI ile encoding"""
       try:
           if isinstance(texts, str):
               texts = [texts]
           
           # Token kontrolü
           processed_texts = []
           for text in texts:
               tokens = self._tokenizer.encode(text)
               if len(tokens) > self.max_tokens:
                   # Token limitini aşanları kes
                   truncated_tokens = tokens[:self.max_tokens]
                   text = self._tokenizer.decode(truncated_tokens)
               processed_texts.append(text)
           
           # OpenAI API çağrısı
           response = self._model.embeddings.create(
               input=processed_texts,
               model=self.model_name.replace('openai/', '')
           )
           
           embeddings = [data.embedding for data in response.data]
           return embeddings[0] if len(embeddings) == 1 else embeddings
           
       except Exception as e:
           logger.error(f"OpenAI embedding hatası: {e}")
           raise ExternalServiceError(f"OpenAI embedding hatası: {str(e)}", service_name="OpenAI")
   
   def _encode_sentence_transformer(self, texts: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
       """Sentence Transformers ile encoding"""
       try:
           embeddings = self.model.encode(texts, **kwargs)
           
           if isinstance(texts, str):
               return embeddings.tolist()
           else:
               return [emb.tolist() for emb in embeddings]
               
       except Exception as e:
           logger.error(f"Sentence Transformer embedding hatası: {e}")
           raise EmbeddingError(f"Embedding oluşturma hatası: {str(e)}")


class EmbeddingService:
   """Ana Embedding Servisi"""
   
   def __init__(self):
       self.cache_manager = EmbeddingCacheManager()
       self.models = self._initialize_models()
       self.default_model = self._get_default_model()
       
       # Performance tracking
       self._total_requests = 0
       self._total_cache_hits = 0
       self._total_processing_time = 0.0
   
   def _initialize_models(self) -> Dict[str, EmbeddingModel]:
       """Modelleri başlat"""
       models = {}
       
       # Çok dilli model (varsayılan)
       models['multilingual'] = EmbeddingModel(
           model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
           dimension=384,
           max_tokens=512
       )
       
       # Türkçe odaklı model
       models['turkish'] = EmbeddingModel(
           model_name='emrecan/bert-base-turkish-cased-mean-nli-stsb-tr',
           dimension=768,
           max_tokens=512
       )
       
       # OpenAI modeli (opsiyonel)
       if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
           models['openai_small'] = EmbeddingModel(
               model_name='openai/text-embedding-3-small',
               dimension=1536,
               max_tokens=8192
           )
           
           models['openai_large'] = EmbeddingModel(
               model_name='openai/text-embedding-3-large',
               dimension=3072,
               max_tokens=8192
           )
       
       logger.info(f"Embedding modelleri hazırlandı: {list(models.keys())}")
       return models
   
   def _get_default_model(self) -> str:
       """Varsayılan model seç"""
       default = getattr(settings, 'SAPBOT_DEFAULT_EMBEDDING_MODEL', 'multilingual')
       
       if default not in self.models:
           logger.warning(f"Varsayılan model bulunamadı: {default}, multilingual kullanılacak")
           default = 'multilingual'
       
       return default
   
   def generate_embedding(
       self, 
       content: str, 
       model_name: Optional[str] = None,
       use_cache: bool = True,
       chunk_long_text: bool = True
   ) -> EmbeddingResult:
       """Tek bir içerik için embedding oluştur"""
       start_time = time.time()
       self._total_requests += 1
       
       if not content or not content.strip():
           raise EmbeddingError("Boş içerik için embedding oluşturulamaz")
       
       # Model seç
       model_name = model_name or self.default_model
       if model_name not in self.models:
           raise EmbeddingError(f"Bilinmeyen model: {model_name}")
       
       model = self.models[model_name]
       
       # İçeriği temizle
       cleaned_content = clean_text(content)
       content_hash = self._generate_content_hash(cleaned_content)
       
       # Cache kontrol
       if use_cache:
           cached_embedding = self.cache_manager.get_embedding(content_hash)
           if cached_embedding:
               self._total_cache_hits += 1
               processing_time = time.time() - start_time
               
               return EmbeddingResult(
                   embedding=cached_embedding,
                   model_used=model_name,
                   dimension=model.dimension,
                   processing_time=processing_time,
                   cache_hit=True,
                   content_hash=content_hash
               )
       
       # Uzun metinleri böl
       if chunk_long_text and len(cleaned_content) > model.max_tokens * 3:  # Rough token estimate
           return self._generate_chunked_embedding(cleaned_content, model_name, content_hash)
       
       try:
           # Embedding oluştur
           embedding = model.encode(cleaned_content)
           
           processing_time = time.time() - start_time
           self._total_processing_time += processing_time
           
           # Token sayısı hesapla (varsa)
           token_count = self._estimate_token_count(cleaned_content, model_name)
           
           # Maliyet hesapla (OpenAI için)
           cost_estimate = self._calculate_cost(token_count, model_name)
           
           result = EmbeddingResult(
               embedding=embedding,
               model_used=model_name,
               dimension=model.dimension,
               processing_time=processing_time,
               token_count=token_count,
               cost_estimate=cost_estimate,
               cache_hit=False,
               content_hash=content_hash
           )
           
           # Cache'e kaydet
           if use_cache:
               self.cache_manager.set_embedding(content_hash, embedding)
           
           return result
           
       except Exception as e:
           logger.error(f"Embedding oluşturma hatası: {e}")
           raise EmbeddingError(f"Embedding oluşturma hatası: {str(e)}", content_hash=content_hash)
   
   def generate_batch_embeddings(
       self,
       contents: List[str],
       model_name: Optional[str] = None,
       use_cache: bool = True,
       batch_size: int = 32,
       max_workers: int = 4
   ) -> BatchEmbeddingResult:
       """Toplu embedding oluşturma"""
       start_time = time.time()
       
       if not contents:
           raise EmbeddingError("Boş içerik listesi")
       
       model_name = model_name or self.default_model
       results = []
       embeddings = []
       failed_count = 0
       cache_hits = 0
       
       # İçerikleri temizle ve hash'le
       processed_contents = []
       content_hashes = []
       
       for content in contents:
           cleaned = clean_text(content) if content else ""
           if cleaned:
               processed_contents.append(cleaned)
               content_hashes.append(self._generate_content_hash(cleaned))
           else:
               processed_contents.append("")
               content_hashes.append("")
       
       # Cache'den al
       cached_embeddings = {}
       if use_cache:
           cached_embeddings = self.cache_manager.get_batch_embeddings(content_hashes)
           cache_hits = len(cached_embeddings)
       
       # Cache'de olmayan içerikleri işle
       to_process = []
       to_process_indices = []
       
       for i, (content, content_hash) in enumerate(zip(processed_contents, content_hashes)):
           if content_hash in cached_embeddings:
               # Cache hit
               result = EmbeddingResult(
                   embedding=cached_embeddings[content_hash],
                   model_used=model_name,
                   dimension=self.models[model_name].dimension,
                   processing_time=0.0,
                   cache_hit=True,
                   content_hash=content_hash
               )
               results.append(result)
               embeddings.append(cached_embeddings[content_hash])
           else:
               # İşlenmesi gerekiyor
               to_process.append(content)
               to_process_indices.append(i)
               results.append(None)  # Placeholder
               embeddings.append(None)  # Placeholder
       
       # Batch'lerde işle
       if to_process:
           batch_results = self._process_batches(
               to_process, 
               model_name, 
               batch_size, 
               max_workers
           )
           
           # Sonuçları yerleştir
           new_embeddings_to_cache = {}
           
           for i, batch_result in enumerate(batch_results):
               original_index = to_process_indices[i]
               
               if batch_result is not None:
                   results[original_index] = batch_result
                   embeddings[original_index] = batch_result.embedding
                   
                   # Cache için sakla
                   if use_cache:
                       new_embeddings_to_cache[batch_result.content_hash] = batch_result.embedding
               else:
                   failed_count += 1
                   # Başarısız olanlar için boş embedding
                   results[original_index] = EmbeddingResult(
                       embedding=[0.0] * self.models[model_name].dimension,
                       model_used=model_name,
                       dimension=self.models[model_name].dimension,
                       processing_time=0.0,
                       cache_hit=False,
                       content_hash=content_hashes[original_index]
                   )
                   embeddings[original_index] = [0.0] * self.models[model_name].dimension
           
           # Yeni embeddings'leri cache'e toplu kaydet
           if new_embeddings_to_cache:
               self.cache_manager.set_batch_embeddings(new_embeddings_to_cache)
       
       total_time = time.time() - start_time
       success_count = len(contents) - failed_count
       cache_hit_rate = cache_hits / len(contents) if contents else 0
       
       return BatchEmbeddingResult(
           embeddings=embeddings,
           results=results,
           total_processing_time=total_time,
           cache_hit_rate=cache_hit_rate,
           failed_count=failed_count,
           success_count=success_count
       )
   
   def _process_batches(
       self,
       contents: List[str],
       model_name: str,
       batch_size: int,
       max_workers: int
   ) -> List[Optional[EmbeddingResult]]:
       """Batch'leri paralel işle"""
       all_results = [None] * len(contents)
       
       # Batch'lere böl
       batches = [contents[i:i + batch_size] for i in range(0, len(contents), batch_size)]
       
       def process_batch(batch_data):
           batch, start_idx = batch_data
           try:
               model = self.models[model_name]
               embeddings = model.encode(batch)
               
               batch_results = []
               for i, (content, embedding) in enumerate(zip(batch, embeddings)):
                   content_hash = self._generate_content_hash(content)
                   
                   result = EmbeddingResult(
                       embedding=embedding,
                       model_used=model_name,
                       dimension=model.dimension,
                       processing_time=0.0,  # Batch için individual time yok
                       cache_hit=False,
                       content_hash=content_hash
                   )
                   batch_results.append((start_idx + i, result))
               
               return batch_results
               
           except Exception as e:
               logger.error(f"Batch işleme hatası: {e}")
               return [(start_idx + i, None) for i in range(len(batch))]
       
       # Paralel işleme
       with ThreadPoolExecutor(max_workers=max_workers) as executor:
           batch_data = [(batch, i * batch_size) for i, batch in enumerate(batches)]
           futures = [executor.submit(process_batch, data) for data in batch_data]
           
           for future in as_completed(futures):
               try:
                   batch_results = future.result()
                   for idx, result in batch_results:
                       all_results[idx] = result
               except Exception as e:
                   logger.error(f"Batch future hatası: {e}")
       
       return all_results
   
   def _generate_chunked_embedding(
       self, 
       content: str, 
       model_name: str, 
       content_hash: str
   ) -> EmbeddingResult:
       """Uzun metinler için chunk'lara bölerek embedding"""
       from ..utils.text_processing import TextChunker
       
       start_time = time.time()
       
       # Metni chunk'lara böl
       chunks = TextChunker.intelligent_split(
           content, 
           max_chunk_size=1000,  # Model'e göre ayarlanabilir
           overlap=100
       )
       
       if not chunks:
           raise EmbeddingError("Metin chunk'lara bölünemedi")
       
       # Her chunk için embedding oluştur
       chunk_embeddings = []
       model = self.models[model_name]
       
       for chunk in chunks:
           try:
               embedding = model.encode(chunk.text)
               chunk_embeddings.append(embedding)
           except Exception as e:
               logger.warning(f"Chunk embedding hatası: {e}")
               # Sıfır embedding ekle
               chunk_embeddings.append([0.0] * model.dimension)
       
       # Ortalama embedding hesapla
       if chunk_embeddings:
           avg_embedding = np.mean(chunk_embeddings, axis=0).tolist()
       else:
           avg_embedding = [0.0] * model.dimension
       
       processing_time = time.time() - start_time
       
       return EmbeddingResult(
           embedding=avg_embedding,
           model_used=model_name,
           dimension=model.dimension,
           processing_time=processing_time,
           cache_hit=False,
           content_hash=content_hash
       )
   
   def _generate_content_hash(self, content: str) -> str:
       """İçerik hash'i oluştur"""
       return hashlib.sha256(content.encode('utf-8')).hexdigest()
   
   def _estimate_token_count(self, content: str, model_name: str) -> Optional[int]:
       """Token sayısını tahmin et"""
       if model_name.startswith('openai'):
           try:
               model = self.models[model_name]
               if model._tokenizer:
                   return len(model._tokenizer.encode(content))
           except:
               pass
       
       # Basit tahmin: 1 token ≈ 4 karakter
       return len(content) // 4
   
   def _calculate_cost(self, token_count: Optional[int], model_name: str) -> Optional[float]:
       """Maliyet hesapla (OpenAI için)"""
       if not token_count or not model_name.startswith('openai'):
           return None
       
       # OpenAI fiyatları (2024 fiyatları, güncellenebilir)
       pricing = {
           'openai/text-embedding-3-small': 0.00002,  # per 1K tokens
           'openai/text-embedding-3-large': 0.00013,  # per 1K tokens
       }
       
       rate = pricing.get(model_name, 0.0)
       return (token_count / 1000) * rate
   
   def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
       """Model bilgilerini al"""
       if model_name:
           if model_name not in self.models:
               raise EmbeddingError(f"Bilinmeyen model: {model_name}")
           
           model = self.models[model_name]
           return {
               'model_name': model_name,
               'dimension': model.dimension,
               'max_tokens': model.max_tokens,
               'is_loaded': model._model is not None
           }
       else:
           return {
               'available_models': list(self.models.keys()),
               'default_model': self.default_model,
               'models': {
                   name: {
                       'dimension': model.dimension,
                       'max_tokens': model.max_tokens,
                       'is_loaded': model._model is not None
                   }
                   for name, model in self.models.items()
               }
           }
   
   def get_performance_stats(self) -> Dict[str, Any]:
       """Performans istatistikleri"""
       cache_hit_rate = (self._total_cache_hits / self._total_requests * 100) if self._total_requests > 0 else 0
       avg_processing_time = (self._total_processing_time / self._total_requests) if self._total_requests > 0 else 0
       
       return {
           'total_requests': self._total_requests,
           'total_cache_hits': self._total_cache_hits,
           'cache_hit_rate': f"{cache_hit_rate:.2f}%",
           'total_processing_time': f"{self._total_processing_time:.2f}s",
           'avg_processing_time': f"{avg_processing_time:.3f}s",
           'models_loaded': sum(1 for model in self.models.values() if model._model is not None)
       }
   
   def similarity_search(
       self,
       query_embedding: List[float],
       candidate_embeddings: List[List[float]],
       top_k: int = 10,
       threshold: float = 0.7
   ) -> List[Tuple[int, float]]:
       """Cosine similarity ile arama"""
       if not query_embedding or not candidate_embeddings:
           return []
       
       try:
           # NumPy array'e çevir
           query_vec = np.array(query_embedding)
           candidate_vecs = np.array(candidate_embeddings)
           
           # Normalize et
           query_norm = query_vec / np.linalg.norm(query_vec)
           candidate_norms = candidate_vecs / np.linalg.norm(candidate_vecs, axis=1, keepdims=True)
           
           # Cosine similarity hesapla
           similarities = np.dot(candidate_norms, query_norm)
           
           # Threshold uygula
           valid_indices = np.where(similarities >= threshold)[0]
           valid_similarities = similarities[valid_indices]
           
           # Sırala ve top_k al
           sorted_indices = np.argsort(valid_similarities)[::-1][:top_k]
           
           results = [
               (int(valid_indices[i]), float(valid_similarities[i]))
               for i in sorted_indices
           ]
           
           return results
           
       except Exception as e:
           logger.error(f"Similarity search hatası: {e}")
           return []
   
   def clear_cache(self, content_hash: Optional[str] = None):
       """Cache temizle"""
       if content_hash:
           self.cache_manager.delete(f"embedding:{content_hash}")
       else:
           self.cache_manager.clear_pattern("embedding:*")
       
       logger.info("Embedding cache temizlendi")
   
   def warmup_models(self):
       """Modelleri önceden yükle"""
       logger.info("Embedding modelleri ön yükleme başlıyor...")
       
       test_content = "SAP Business One test embedding"
       
       for model_name in self.models.keys():
           try:
               start_time = time.time()
               self.generate_embedding(test_content, model_name=model_name, use_cache=False)
               load_time = time.time() - start_time
               logger.info(f"Model yüklendi: {model_name} ({load_time:.2f}s)")
           except Exception as e:
               logger.error(f"Model yükleme hatası ({model_name}): {e}")
       
       logger.info("Model ön yükleme tamamlandı")


# Singleton instance
embedding_service = EmbeddingService()


# Utility functions
def generate_embedding(content: str, model_name: Optional[str] = None) -> List[float]:
   """Hızlı embedding oluşturma"""
   result = embedding_service.generate_embedding(content, model_name)
   return result.embedding


def generate_batch_embeddings(contents: List[str], model_name: Optional[str] = None) -> List[List[float]]:
   """Hızlı toplu embedding oluşturma"""
   result = embedding_service.generate_batch_embeddings(contents, model_name)
   return result.embeddings


def search_similar_content(
   query: str, 
   candidate_contents: List[str], 
   top_k: int = 10
) -> List[Tuple[int, str, float]]:
   """Benzer içerik arama"""
   # Query embedding
   query_result = embedding_service.generate_embedding(query)
   
   # Candidate embeddings
   candidate_results = embedding_service.generate_batch_embeddings(candidate_contents)
   
   # Similarity search
   similarities = embedding_service.similarity_search(
       query_result.embedding,
       candidate_results.embeddings,
       top_k=top_k
   )
   
   # Sonuçları formatla
   results = [
       (idx, candidate_contents[idx], score)
       for idx, score in similarities
   ]
   
   return results


def calculate_text_similarity(text1: str, text2: str) -> float:
   """İki metin arasındaki benzerlik"""
   results = embedding_service.generate_batch_embeddings([text1, text2])
   
   if len(results.embeddings) != 2:
       return 0.0
   
   similarities = embedding_service.similarity_search(
       results.embeddings[0],
       [results.embeddings[1]],
       top_k=1
   )
   
   return similarities[0][1] if similarities else 0.0


# Celery task helper
def async_generate_embeddings(content_ids: List[str], model_name: Optional[str] = None):
   """Asenkron embedding oluşturma - Celery task için"""
   from ..models import KnowledgeChunk
   
   try:
       chunks = KnowledgeChunk.objects.filter(id__in=content_ids, embedding__isnull=True)
       contents = [chunk.content for chunk in chunks]
       
       if not contents:
           logger.info("Embedding oluşturulacak içerik bulunamadı")
           return
       
       logger.info(f"{len(contents)} chunk için embedding oluşturuluyor...")
       
       # Batch embedding oluştur
       results = embedding_service.generate_batch_embeddings(contents, model_name)
       
       # Veritabanına kaydet
       for chunk, result in zip(chunks, results.results):
           if result and result.embedding:
               chunk.embedding = result.embedding
               chunk.embedding_model = result.model_used
               chunk.save(update_fields=['embedding', 'embedding_model'])
       
       logger.info(f"Embedding oluşturma tamamlandı. Başarılı: {results.success_count}, Başarısız: {results.failed_count}")
       
       return {
           'success_count': results.success_count,
           'failed_count': results.failed_count,
           'cache_hit_rate': results.cache_hit_rate,
           'total_time': results.total_processing_time
       }
       
   except Exception as e:
       logger.error(f"Asenkron embedding hatası: {e}")
       raise
