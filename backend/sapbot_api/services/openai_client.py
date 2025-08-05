# backend/sapbot_api/services/openai_client.py
"""
OpenAI API Client Service

OpenAI GPT modelleri ile etkileşim için client sınıfı
"""

import openai
import logging
import time
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass
from django.conf import settings
from django.core.cache import cache

from ..utils.exceptions import (
    OpenAIError, 
    RateLimitError, 
    QuotaExceededError,
    ExternalServiceError
)
from ..utils.cache_utils import embedding_cache
from ..utils.helpers import generate_hash

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """Chat yanıt modeli"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    response_time: float
    cached: bool = False


@dataclass
class EmbeddingResponse:
    """Embedding yanıt modeli"""
    embedding: List[float]
    model: str
    usage: Dict[str, int]
    response_time: float
    cached: bool = False


class OpenAIClient:
    """OpenAI API client sınıfı"""
    
    def __init__(self):
        """OpenAI client'ı başlat"""
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.organization = getattr(settings, 'OPENAI_ORGANIZATION', None)
        self.chat_model = getattr(settings, 'OPENAI_CHAT_MODEL', 'gpt-4-turbo-preview')
        self.embedding_model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        self.max_retries = getattr(settings, 'OPENAI_MAX_RETRIES', 3)
        self.timeout = getattr(settings, 'OPENAI_TIMEOUT', 30)
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY setting gerekli")
        
        # OpenAI client'ı konfigüre et
        openai.api_key = self.api_key
        if self.organization:
            openai.organization = self.organization
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        stream: bool = False,
        user_id: str = None
    ) -> ChatResponse:
        """Chat completion isteği"""
        
        model = model or self.chat_model
        start_time = time.time()
        
        # Cache key oluştur
        cache_key = self._generate_chat_cache_key(messages, model, temperature, max_tokens)
        
        # Cache kontrol et
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Chat response cache'den alındı: {cache_key}")
            cached_response['cached'] = True
            return ChatResponse(**cached_response)
        
        try:
            # OpenAI API çağrısı
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                user=user_id,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if stream:
                return self._handle_streaming_response(response, model, response_time)
            else:
                return self._handle_standard_response(
                    response, model, response_time, cache_key
                )
                
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI rate limit hatası: {e}")
            raise RateLimitError("OpenAI API rate limit aşıldı")
            
        except openai.error.QuotaExceededError as e:
            logger.error(f"OpenAI quota hatası: {e}")
            raise QuotaExceededError("OpenAI API kotası aşıldı")
            
        except openai.error.InvalidRequestError as e:
            logger.error(f"OpenAI geçersiz istek: {e}")
            raise OpenAIError(f"Geçersiz istek: {str(e)}")
            
        except openai.error.AuthenticationError as e:
            logger.error(f"OpenAI kimlik doğrulama hatası: {e}")
            raise OpenAIError("OpenAI kimlik doğrulama hatası")
            
        except openai.error.APIError as e:
            logger.error(f"OpenAI API hatası: {e}")
            raise ExternalServiceError("OpenAI", str(e))
            
        except Exception as e:
            logger.error(f"Beklenmeyen OpenAI hatası: {e}")
            raise OpenAIError(f"Beklenmeyen hata: {str(e)}")
    
    def create_embedding(
        self,
        text: str,
        model: str = None,
        user_id: str = None
    ) -> EmbeddingResponse:
        """Text embedding oluştur"""
        
        model = model or self.embedding_model
        start_time = time.time()
        
        # Content hash oluştur
        content_hash = generate_hash(f"{text}_{model}")
        
        # Cache kontrol et
        cached_embedding = embedding_cache.get_embedding(content_hash)
        if cached_embedding:
            logger.info(f"Embedding cache'den alındı: {content_hash[:8]}")
            return EmbeddingResponse(
                embedding=cached_embedding,
                model=model,
                usage={'prompt_tokens': len(text.split())},
                response_time=time.time() - start_time,
                cached=True
            )
        
        try:
            # Text'i temizle ve uzunluk kontrol et
            cleaned_text = self._prepare_text_for_embedding(text)
            
            # OpenAI API çağrısı
            response = openai.Embedding.create(
                input=cleaned_text,
                model=model,
                user=user_id,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            embedding = response['data'][0]['embedding']
            
            # Cache'e kaydet
            embedding_cache.set_embedding(content_hash, embedding)
            
            # Usage bilgilerini logla
            usage = response.get('usage', {})
            logger.info(f"Embedding oluşturuldu - Model: {model}, Tokens: {usage.get('total_tokens', 0)}")
            
            return EmbeddingResponse(
                embedding=embedding,
                model=model,
                usage=usage,
                response_time=response_time,
                cached=False
            )
            
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI embedding rate limit: {e}")
            raise RateLimitError("OpenAI embedding rate limit aşıldı")
            
        except openai.error.QuotaExceededError as e:
            logger.error(f"OpenAI embedding quota: {e}")
            raise QuotaExceededError("OpenAI embedding kotası aşıldı")
            
        except Exception as e:
            logger.error(f"Embedding hatası: {e}")
            raise OpenAIError(f"Embedding oluşturma hatası: {str(e)}")
    
    def create_embeddings_batch(
        self,
        texts: List[str],
        model: str = None,
        batch_size: int = 100
    ) -> List[EmbeddingResponse]:
        """Toplu embedding oluştur"""
        
        model = model or self.embedding_model
        results = []
        
        # Batch'lere böl
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                try:
                    embedding_response = self.create_embedding(text, model)
                    batch_results.append(embedding_response)
                except Exception as e:
                    logger.error(f"Batch embedding hatası: {e}")
                    # Hata durumunda boş embedding ekle
                    batch_results.append(EmbeddingResponse(
                        embedding=[],
                        model=model,
                        usage={},
                        response_time=0.0,
                        cached=False
                    ))
            
            results.extend(batch_results)
            
            # Rate limiting için kısa bekleme
            if i + batch_size < len(texts):
                time.sleep(0.1)
        
        return results
    
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        user_id: str = None
    ) -> Generator[str, None, None]:
        """Streaming chat completion"""
        
        model = model or self.chat_model
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                user=user_id,
                timeout=self.timeout
            )
            
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        yield delta['content']
                        
        except Exception as e:
            logger.error(f"Streaming chat hatası: {e}")
            raise OpenAIError(f"Streaming chat hatası: {str(e)}")
    
    def _handle_standard_response(
        self,
        response: Dict[str, Any],
        model: str,
        response_time: float,
        cache_key: str
    ) -> ChatResponse:
        """Standart chat response'unu handle et"""
        
        choice = response['choices'][0]
        content = choice['message']['content']
        usage = response.get('usage', {})
        finish_reason = choice.get('finish_reason', 'unknown')
        
        # Response'u cache'le (5 dakika)
        cache_data = {
            'content': content,
            'model': model,
            'usage': usage,
            'finish_reason': finish_reason,
            'response_time': response_time
        }
        cache.set(cache_key, cache_data, 300)
        
        # Usage bilgilerini logla
        logger.info(f"Chat completion - Model: {model}, Tokens: {usage.get('total_tokens', 0)}")
        
        return ChatResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason=finish_reason,
            response_time=response_time,
            cached=False
        )
    
    def _handle_streaming_response(
        self,
        response: Any,
        model: str,
        response_time: float
    ) -> ChatResponse:
        """Streaming response'unu handle et"""
        
        content_parts = []
        usage = {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0}
        
        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    content_parts.append(delta['content'])
        
        content = ''.join(content_parts)
        
        return ChatResponse(
            content=content,
            model=model,
            usage=usage,
            finish_reason='stop',
            response_time=response_time,
            cached=False
        )
    
    def _generate_chat_cache_key(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chat için cache key oluştur"""
        
        # Sadece son 3 mesajı cache key'e dahil et
        relevant_messages = messages[-3:] if len(messages) > 3 else messages
        
        key_data = {
            'messages': relevant_messages,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        import json
        key_string = json.dumps(key_data, sort_keys=True)
        return f"chat_{generate_hash(key_string)[:12]}"
    
    def _prepare_text_for_embedding(self, text: str) -> str:
        """Embedding için text'i hazırla"""
        
        # Text'i temizle
        cleaned_text = text.strip()
        
        # Çok uzun text'leri kes (8000 karakter)
        if len(cleaned_text) > 8000:
            cleaned_text = cleaned_text[:8000] + "..."
            logger.warning("Text embedding için kısaltıldı")
        
        # Boş text kontrolü
        if not cleaned_text:
            cleaned_text = "Empty content"
        
        return cleaned_text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Kullanılan model bilgilerini döndür"""
        return {
            'chat_model': self.chat_model,
            'embedding_model': self.embedding_model,
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }
    
    def test_connection(self) -> bool:
        """OpenAI bağlantısını test et"""
        try:
            # Basit bir test isteği
            response = openai.Model.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI bağlantı testi başarısız: {e}")
            return False


# Singleton instance
_openai_client = None

def get_openai_client() -> OpenAIClient:
    """OpenAI client singleton'ı al"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI() # type: ignore
    return _openai_client