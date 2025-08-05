# backend/sapbot_api/services/chat_service.py
"""
SAPBot Chat Service - RAG destekli SAP Business One AI Chat Sistemi

Bu servis, kullanıcı sorularını işleyerek SAP B1 dokümantasyonundan
en uygun bilgileri bulur ve GPT-4 ile Türkçe yanıtlar üretir.

Core Features:
- RAG (Retrieval-Augmented Generation) pipeline
- SAP B1 terminoloji analizi
- Intent detection ve context management
- Multi-level user support (user/technical/admin)
- Turkish/English content processing
"""
import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from django.db import models
import openai
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from ..models import (
    ChatConversation, ChatMessage, KnowledgeChunk, 
    QueryAnalytics, UserProfile
)
from ..utils.cache_utils import chat_cache
from ..utils.text_processing import (
    TextAnalyzer, SAPTerminologyAnalyzer
    
)
from ..utils.validators import ChatMessageValidator
from ..utils.exceptions import (
    ChatError, ValidationException, OpenAIError
)
from .search_service import SearchService
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

@dataclass
class ChatContext:
    """Chat bağlamı veri yapısı"""
    user_message: str
    session_id: str
    user_type: str
    user_profile: Optional[UserProfile]
    conversation: Optional[ChatConversation]
    previous_messages: List[Dict[str, Any]]
    detected_language: str
    sap_module: Optional[str]
    technical_level: str
    intent: str
    confidence_score: float


@dataclass  
class RAGResult:
    """RAG işlem sonucu"""
    response_text: str
    sources: List[Dict[str, Any]]
    context_used: str
    response_time: float
    tokens_used: int
    confidence_score: float
    intent_detected: str
    sap_module_detected: Optional[str]


class ContextManager:
    """Konuşma bağlamı yöneticisi"""
    
    def __init__(self):
        self.max_context_length = 4000
        self.max_previous_messages = 5
    
    def prepare_context(
        self, 
        query: str, 
        session_id: str,
        user_type: str = 'user',
        user_profile: Optional[UserProfile] = None
    ) -> ChatContext:
        """Chat bağlamını hazırla"""
        try:
            # Konuşma geçmişini al
            conversation = self._get_or_create_conversation(session_id, user_type, user_profile)
            previous_messages = self._get_previous_messages(conversation)
            
            # Metin analizi
            analysis = TextAnalyzer.analyze_text(query)
            
            # Kullanıcı profiline göre SAP modül tespiti
            detected_sap_module = self._determine_sap_module(analysis, user_profile)
            
            return ChatContext(
                user_message=query,
                session_id=session_id,
                user_type=user_type,
                user_profile=user_profile,
                conversation=conversation,
                previous_messages=previous_messages,
                detected_language=analysis.language,
                sap_module=detected_sap_module,
                technical_level=analysis.technical_level,
                intent=analysis.intent,
                confidence_score=analysis.confidence
            )
            
        except Exception as e:
            logger.error(f"Context hazırlama hatası: {e}")
            raise ChatError(
                message="Chat bağlamı hazırlanamadı",
                session_id=session_id
            )
    
    def _get_or_create_conversation(
        self, 
        session_id: str, 
        user_type: str,
        user_profile: Optional[UserProfile]
    ) -> ChatConversation:
        """Konuşmayı al veya oluştur"""
        try:
            conversation = ChatConversation.objects.filter(
                session_id=session_id,
                is_active=True
            ).first()
            
            if not conversation:
                conversation = ChatConversation.objects.create(
                    session_id=session_id,
                    user_type=user_type,
                    user=user_profile.user if user_profile else None,
                    metadata={'created_by_service': True}
                )
            
            return conversation
            
        except Exception as e:
            logger.error(f"Konuşma oluşturma hatası: {e}")
            raise
    
    def _get_previous_messages(self, conversation: ChatConversation) -> List[Dict[str, Any]]:
        """Önceki mesajları al"""
        try:
            # Cache'den kontrol et
            cached_messages = chat_cache.get_chat_history(
                conversation.session_id, 
                limit=self.max_previous_messages
            )
            
            if cached_messages:
                return cached_messages
            
            # Database'den al
            messages = ChatMessage.objects.filter(
                conversation=conversation,
                is_active=True
            ).order_by('-created_at')[:self.max_previous_messages]
            
            message_list = []
            for msg in messages:
                message_list.append({
                    'type': msg.message_type,
                    'content': msg.content[:500],  # İlk 500 karakter
                    'timestamp': msg.created_at.isoformat(),
                    'intent': msg.intent_detected
                })
            
            # Cache'e kaydet
            chat_cache.add_chat_message(conversation.session_id, {
                'previous_messages': message_list
            })
            
            return message_list
            
        except Exception as e:
            logger.error(f"Önceki mesajları alma hatası: {e}")
            return []
    
    def _determine_sap_module(
        self, 
        analysis, 
        user_profile: Optional[UserProfile]
    ) -> Optional[str]:
        """SAP modülünü belirle"""
        # Önce metin analizinden modül tespiti
        if analysis.sap_modules:
            detected_module = analysis.sap_modules[0]
            
            # Kullanıcı profilinde bu modüle erişimi var mı?
            if user_profile and user_profile.sap_modules:
                if detected_module in user_profile.sap_modules:
                    return detected_module
            else:
                return detected_module
        
        # Kullanıcı profilinden varsayılan modül
        if user_profile and user_profile.sap_modules:
            return user_profile.sap_modules[0]
        
        return None


class ResponseGenerator:
    """Yanıt üretim motoru"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 1500)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.3)
    
    def generate_response(
        self, 
        context: ChatContext, 
        retrieved_sources: List[Dict[str, Any]]
    ) -> RAGResult:
        """Ana yanıt üretim fonksiyonu"""
        start_time = datetime.now()
        
        try:
            # Prompt hazırla
            system_prompt = self._build_system_prompt(context)
            user_prompt = self._build_user_prompt(context, retrieved_sources)
            
            # OpenAI API çağrısı
            response = self._call_openai_api(system_prompt, user_prompt)
            
            # Yanıt süresi hesapla
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Yanıtı işle
            processed_response = self._process_openai_response(response)
            
            return RAGResult(
                response_text=processed_response['text'],
                sources=retrieved_sources,
                context_used=self._summarize_context(retrieved_sources),
                response_time=response_time,
                tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else 0,
                confidence_score=context.confidence_score,
                intent_detected=context.intent,
                sap_module_detected=context.sap_module
            )
            
        except Exception as e:
            logger.error(f"Yanıt üretim hatası: {e}")
            self._handle_openai_error(e)
    
    def _build_system_prompt(self, context: ChatContext) -> str:
        """Sistem prompt'u oluştur"""
        base_prompt = """Sen SAP Business One HANA ERP sistemi konusunda uzman bir AI asistanısın. 
Türkçe SAP B1 kullanıcılarına yardım ediyorsun.

GÖREVIN:
- SAP Business One sorularını net, anlaşılır şekilde yanıtla
- Verilen kaynak dokümanlara dayanarak doğru bilgi ver
- Türkçe yanıt ver (kaynak İngilizce olsa bile)
- Adım adım açıklamalar yap
- Teknik terimleri açıkla

KURALLAR:
- Sadece verilen kaynaklardaki bilgileri kullan
- Bilmediğin konularda "Bu konuda yeterli bilgim yok" de
- SAP transaction kodlarını belirt (örn: VA01, ME21N)
- Örnekler ver
- Güvenlik ve best practice'leri unutma"""
        
        # Kullanıcı tipine göre özelleştir
        if context.user_type == 'technical':
            base_prompt += "\n\nKullanıcı TEKNIK personel - detaylı konfigürasyon bilgileri verebilirsin."
        elif context.user_type == 'admin':
            base_prompt += "\n\nKullanıcı YÖNETİCİ - sistem yönetimi ve güvenlik konularını dahil et."
        else:
            base_prompt += "\n\nKullanıcı SON KULLANICI - basit, anlaşılır açıklamalar yap."
        
        # SAP modülüne göre özelleştir
        if context.sap_module:
            module_names = {
                'FI': 'Mali Muhasebe', 'MM': 'Malzeme Yönetimi', 
                'SD': 'Satış ve Dağıtım', 'CRM': 'Müşteri İlişkileri'
            }
            module_name = module_names.get(context.sap_module, context.sap_module)
            base_prompt += f"\n\nÖzellikle {module_name} ({context.sap_module}) modülü konularına odaklan."
        
        return base_prompt
    
    def _build_user_prompt(
        self, 
        context: ChatContext, 
        sources: List[Dict[str, Any]]
    ) -> str:
        """Kullanıcı prompt'u oluştur"""
        prompt_parts = []
        
        # Kaynak bilgileri
        if sources:
            prompt_parts.append("=== KAYNAK BİLGİLER ===")
            for i, source in enumerate(sources[:5], 1):
                prompt_parts.append(f"\nKaynak {i}:")
                prompt_parts.append(f"Döküman: {source.get('source_title', 'Bilinmiyor')}")
                if source.get('page_number'):
                    prompt_parts.append(f"Sayfa: {source['page_number']}")
                if source.get('section_title'):
                    prompt_parts.append(f"Bölüm: {source['section_title']}")
                prompt_parts.append(f"İçerik: {source.get('content', '')[:800]}")
                prompt_parts.append("---")
        
        # Konuşma geçmişi
        if context.previous_messages:
            prompt_parts.append("\n=== ÖNCEKİ KONUŞMA ===")
            for msg in context.previous_messages[-3:]:  # Son 3 mesaj
                role = "Kullanıcı" if msg['type'] == 'user' else "Asistan"
                prompt_parts.append(f"{role}: {msg['content'][:200]}")
        
        # Mevcut soru
        prompt_parts.append(f"\n=== GÜNCEL SORU ===")
        prompt_parts.append(f"Kullanıcı Sorusu: {context.user_message}")
        
        # Analiz bilgileri
        if context.intent:
            prompt_parts.append(f"Tespit Edilen Niyet: {context.intent}")
        
        prompt_parts.append(f"\n=== TALİMAT ===")
        prompt_parts.append("Yukarıdaki kaynak bilgileri kullanarak soruyu yanıtla. ")
        prompt_parts.append("Yanıtını Türkçe yaz ve kaynaklara referans ver.")
        
        return "\n".join(prompt_parts)
    
    def _call_openai_api(self, system_prompt: str, user_prompt: str) -> Any:
        """OpenAI API çağrısı"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit: {e}")
            raise OpenAIError("OpenAI API rate limit aşıldı", error_type="rate_limit")
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI auth error: {e}")
            raise OpenAIError("OpenAI API authentication hatası", error_type="auth_error")
        except Exception as e:
            logger.error(f"OpenAI API hatası: {e}")
            raise OpenAIError(f"OpenAI API hatası: {str(e)}")
    
    def _process_openai_response(self, response: Any) -> Dict[str, Any]:
        """OpenAI yanıtını işle"""
        try:
            response_text = response.choices[0].message.content
            
            # Yanıtı temizle
            cleaned_text = self._clean_response_text(response_text)
            
            return {
                'text': cleaned_text,
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            logger.error(f"Yanıt işleme hatası: {e}")
            raise ChatError("Yanıt işlenemedi")
    
    def _clean_response_text(self, text: str) -> str:
        """Yanıt metnini temizle"""
        if not text:
            return "Üzgünüm, yanıt oluşturamadım."
        
        # Gereksiz boşlukları temizle
        text = ' '.join(text.split())
        
        # Markdown formatlarını düzelt
        text = text.replace('**', '')  # Bold işaretlerini kaldır
        
        # Uzunluk kontrolü
        if len(text) > 3000:
            text = text[:2950] + "..."
        
        return text.strip()
    
    def _summarize_context(self, sources: List[Dict[str, Any]]) -> str:
        """Kullanılan bağlamı özetle"""
        if not sources:
            return "Genel bilgi"
        
        doc_titles = []
        for source in sources:
            title = source.get('source_title', 'Bilinmeyen Döküman')
            if title not in doc_titles:
                doc_titles.append(title)
        
        return ', '.join(doc_titles[:3])
    
    def _handle_openai_error(self, error: Exception) -> None:
        """OpenAI hatalarını işle"""
        if "rate_limit" in str(error).lower():
            raise OpenAIError("API kullanım limiti aşıldı", error_type="rate_limit")
        elif "insufficient_quota" in str(error).lower():
            raise OpenAIError("API kotası yetersiz", error_type="quota_exceeded")
        elif "invalid_api_key" in str(error).lower():
            raise OpenAIError("Geçersiz API anahtarı", error_type="auth_error")
        else:
            raise OpenAIError(f"OpenAI API hatası: {str(error)}")


class RAGChatbotService:
    """Ana RAG Chatbot servisi"""
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.search_service = SearchService()
        self.embedding_service = EmbeddingService()
        self.response_generator = ResponseGenerator()
        self.validator = ChatMessageValidator()
    
    def process_message(
        self, 
        message: str, 
        session_id: str,
        user_type: str = 'user',
        user_profile: Optional[UserProfile] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """Ana mesaj işleme fonksiyonu"""
        try:
            # Validasyon
            validated_data = self.validator.validate_message_content(message)
            validated_session = self.validator.validate_session_id(session_id)
            validated_user_type = self.validator.validate_user_type(user_type)
            
            # Cache kontrolü
            response_cache_key = self._generate_cache_key(
                validated_data, validated_session, validated_user_type
            )
            
            cached_response = chat_cache.get_response_cache(response_cache_key)
            if cached_response:
                logger.info(f"Cache'den yanıt döndürüldü: {session_id}")
                return self._deserialize_rag_result(cached_response)
            
            # 1. Context hazırlama
            context = self.context_manager.prepare_context(
                validated_data, 
                validated_session, 
                validated_user_type,
                user_profile
            )
            
            # 2. Kaynak arama
            search_results = self._retrieve_relevant_sources(context)
            
            # 3. Yanıt üretme
            rag_result = self.response_generator.generate_response(context, search_results)
            
            # 4. Veritabanına kaydetme
            with transaction.atomic():
                self._save_chat_interaction(context, rag_result, metadata)
            
            # 5. Analytics kaydetme
            self._log_analytics(context, rag_result)
            
            # 6. Cache'e kaydetme
            chat_cache.set_response_cache(
                response_cache_key, 
                self._serialize_rag_result(rag_result),
                timeout=1800  # 30 dakika
            )
            
            return rag_result
            
        except ValidationException as e:
            logger.warning(f"Validasyon hatası: {e}")
            raise
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {e}")
            raise ChatError(
                message="Mesaj işlenemedi",
                session_id=session_id,
                message_id=None
            )
    
    def _retrieve_relevant_sources(self, context: ChatContext) -> List[Dict[str, Any]]:
        """İlgili kaynakları bul"""
        try:
            search_filters = {
                'sap_module': context.sap_module,
                'technical_level': context.technical_level,
                'language': context.detected_language
            }
            
            # Semantic search
            search_results = self.search_service.semantic_search(
                query=context.user_message,
                filters=search_filters,
                limit=5,
                min_relevance=0.7
            )
            
            # Kullanıcı tipine göre filtreleme
            filtered_results = self._filter_by_user_permissions(
                search_results, 
                context.user_profile
            )
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Kaynak arama hatası: {e}")
            # Hata durumunda boş liste döndür
            return []
    
    def _filter_by_user_permissions(
        self, 
        search_results: List[Dict[str, Any]], 
        user_profile: Optional[UserProfile]
    ) -> List[Dict[str, Any]]:
        """Kullanıcı yetkilerine göre sonuçları filtrele"""
        if not user_profile or not hasattr(user_profile, 'sap_modules'):
            return search_results
        
        allowed_modules = user_profile.sap_modules or []
        
        filtered_results = []
        for result in search_results:
            chunk_module = result.get('sap_module')
            if not chunk_module or chunk_module in allowed_modules:
                filtered_results.append(result)
        
        return filtered_results
    
    def _save_chat_interaction(
        self, 
        context: ChatContext, 
        rag_result: RAGResult,
        metadata: Optional[Dict[str, Any]]
    ) -> None:
        """Chat etkileşimini veritabanına kaydet"""
        try:
            # Kullanıcı mesajını kaydet
            user_message = ChatMessage.objects.create(
                conversation=context.conversation,
                message_type='user',
                content=context.user_message,
                intent_detected=context.intent,
                confidence_score=context.confidence_score,
                metadata=metadata or {}
            )
            
            # Asistan yanıtını kaydet
            assistant_message = ChatMessage.objects.create(
                conversation=context.conversation,
                message_type='assistant',
                content=rag_result.response_text,
                response_time=rag_result.response_time,
                token_count=rag_result.tokens_used,
                model_used=self.response_generator.model,
                intent_detected=rag_result.intent_detected,
                confidence_score=rag_result.confidence_score,
                metadata={
                    'sap_module_detected': rag_result.sap_module_detected,
                    'sources_count': len(rag_result.sources),
                    'context_used': rag_result.context_used
                }
            )
            
            # Kullanılan kaynakları bağla
            if rag_result.sources:
                source_chunks = KnowledgeChunk.objects.filter(
                    id__in=[s.get('id') for s in rag_result.sources if s.get('id')]
                )
                assistant_message.sources_used.set(source_chunks)
                
                # Kullanım sayılarını artır
                for chunk in source_chunks:
                    chunk.increment_usage()
            
            # Cache'e ekle
            chat_cache.add_chat_message(context.session_id, {
                'type': 'user',
                'content': context.user_message,
                'timestamp': user_message.created_at.isoformat()
            })
            
            chat_cache.add_chat_message(context.session_id, {
                'type': 'assistant', 
                'content': rag_result.response_text,
                'timestamp': assistant_message.created_at.isoformat(),
                'sources': len(rag_result.sources)
            })
            
        except Exception as e:
            logger.error(f"Chat kaydetme hatası: {e}")
            raise
    
    def _log_analytics(self, context: ChatContext, rag_result: RAGResult) -> None:
        """Analytics verilerini kaydet"""
        try:
            QueryAnalytics.objects.create(
                user=context.user_profile.user if context.user_profile else None,
                session_id=context.session_id,
                query=context.user_message,
                query_hash=hashlib.sha256(context.user_message.encode()).hexdigest(),
                user_type=context.user_type,
                sap_module_detected=context.sap_module,
                intent_detected=context.intent,
                confidence_score=context.confidence_score,
                response_generated=True,
                response_time=rag_result.response_time,
                sources_used_count=len(rag_result.sources),
                tokens_used=rag_result.tokens_used,
                language_detected=context.detected_language,
                metadata={
                    'technical_level': context.technical_level,
                    'has_previous_context': len(context.previous_messages) > 0,
                    'sources_found': len(rag_result.sources) > 0
                }
            )
            
        except Exception as e:
            logger.error(f"Analytics kaydetme hatası: {e}")
            # Analytics hatası ana işlemi durdurmaz
    
    def _generate_cache_key(self, message: str, session_id: str, user_type: str) -> str:
        """Cache anahtarı oluştur"""
        cache_string = f"{message}:{session_id}:{user_type}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _serialize_rag_result(self, rag_result: RAGResult) -> Dict[str, Any]:
        """RAG sonucunu serialize et"""
        return {
            'response_text': rag_result.response_text,
            'sources': rag_result.sources,
            'context_used': rag_result.context_used,
            'response_time': rag_result.response_time,
            'tokens_used': rag_result.tokens_used,
            'confidence_score': rag_result.confidence_score,
            'intent_detected': rag_result.intent_detected,
            'sap_module_detected': rag_result.sap_module_detected,
            'cached_at': timezone.now().isoformat()
        }
    
    def _deserialize_rag_result(self, cached_data: Dict[str, Any]) -> RAGResult:
        """Cache'den RAG sonucunu deserialize et"""
        return RAGResult(
            response_text=cached_data['response_text'],
            sources=cached_data['sources'],
            context_used=cached_data['context_used'], 
            response_time=cached_data['response_time'],
            tokens_used=cached_data['tokens_used'],
            confidence_score=cached_data['confidence_score'],
            intent_detected=cached_data['intent_detected'],
            sap_module_detected=cached_data['sap_module_detected']
        )
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Konuşma geçmişini al"""
        try:
            # Cache'den kontrol et
            cached_history = chat_cache.get_chat_history(session_id, limit)
            if cached_history:
                return cached_history
            
            # Database'den al
            conversation = ChatConversation.objects.filter(
                session_id=session_id,
                is_active=True
            ).first()
            
            if not conversation:
                return []
            
            messages = ChatMessage.objects.filter(
                conversation=conversation,
                is_active=True
            ).order_by('created_at')[:limit]
            
            history = []
            for msg in messages:
                history.append({
                    'id': str(msg.id),
                    'type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'response_time': msg.response_time,
                    'sources_count': msg.sources_used.count(),
                    'intent': msg.intent_detected
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Konuşma geçmişi alma hatası: {e}")
            return []
    
    def clear_conversation(self, session_id: str) -> bool:
        """Konuşmayı temizle"""
        try:
            with transaction.atomic():
                conversation = ChatConversation.objects.filter(
                    session_id=session_id,
                    is_active=True
                ).first()
                
                if conversation:
                    # Mesajları soft delete
                    ChatMessage.objects.filter(
                        conversation=conversation
                    ).update(is_active=False)
                    
                    # Konuşmayı arşivle
                    conversation.is_archived = True
                    conversation.save()
            
            # Cache'i temizle
            cache_key = f"chat_history:{session_id}"
            cache.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Konuşma temizleme hatası: {e}")
            return False
    
    def get_chat_analytics(self, session_id: str) -> Dict[str, Any]:
        """Chat analytics verilerini al"""
        try:
            conversation = ChatConversation.objects.filter(
                session_id=session_id,
                is_active=True
            ).first()
            
            if not conversation:
                return {}
            
            from django.db import models
            
            analytics = QueryAnalytics.objects.filter(
                session_id=session_id
            ).aggregate(
                total_queries=models.Count('id'),
                avg_response_time=models.Avg('response_time'),
                avg_confidence=models.Avg('confidence_score'),
                total_tokens=models.Sum('tokens_used'),
                success_rate=models.Avg(
                    models.Case(
                        models.When(response_generated=True, then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                )
            )
            
            # En çok kullanılan SAP modülleri
            top_modules = QueryAnalytics.objects.filter(
                session_id=session_id
            ).values('sap_module_detected').annotate(
                count=models.Count('id')
            ).order_by('-count')[:5]
            
            # Intent dağılımı
            intent_distribution = QueryAnalytics.objects.filter(
                session_id=session_id
            ).values('intent_detected').annotate(
                count=models.Count('id')
            ).order_by('-count')
            
            return {
                'conversation_stats': {
                    'message_count': conversation.message_count,
                    'duration_minutes': conversation.duration_minutes,
                    'created_at': conversation.created_at.isoformat(),
                    'last_activity': conversation.last_activity.isoformat()
                },
                'query_analytics': analytics,
                'top_sap_modules': list(top_modules),
                'intent_distribution': list(intent_distribution),
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Chat analytics alma hatası: {e}")
            return {}


class ChatHealthChecker:
    """Chat servis sağlık kontrol sınıfı"""
    
    def __init__(self):
        self.chat_service = RAGChatbotService()
    
    def health_check(self) -> Dict[str, Any]:
        """Servis sağlık kontrolü"""
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {},
            'metrics': {}
        }
        
        try:
            # Database bağlantısı
            health_status['checks']['database'] = self._check_database()
            
            # OpenAI API bağlantısı
            health_status['checks']['openai_api'] = self._check_openai_api()
            
            # Cache sistemi
            health_status['checks']['cache'] = self._check_cache()
            
            # Search service
            health_status['checks']['search_service'] = self._check_search_service()
            
            # Embedding service
            health_status['checks']['embedding_service'] = self._check_embedding_service()
            
            # Genel metrikler
            health_status['metrics'] = self._get_service_metrics()
            
            # Genel durumu belirle
            failed_checks = [k for k, v in health_status['checks'].items() if v != 'healthy']
            if failed_checks:
                health_status['status'] = 'warning' if len(failed_checks) < 3 else 'critical'
                health_status['failed_components'] = failed_checks
            
        except Exception as e:
            health_status['status'] = 'critical'
            health_status['error'] = str(e)
            logger.error(f"Health check hatası: {e}")
        
        return health_status
    
    def _check_database(self) -> str:
        """Database sağlık kontrolü"""
        try:
            # Basit sorgu ile test et
            ChatConversation.objects.count()
            return 'healthy'
        except Exception as e:
            logger.error(f"Database health check hatası: {e}")
            return 'critical'
    
    def _check_openai_api(self) -> str:
        """OpenAI API sağlık kontrolü"""
        try:
            response_generator = ResponseGenerator()
            # Basit test çağrısı
            test_response = response_generator.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return 'healthy' if test_response else 'warning'
        except Exception as e:
            logger.error(f"OpenAI API health check hatası: {e}")
            return 'critical'
    
    def _check_cache(self) -> str:
        """Cache sistem kontrolü"""
        try:
            test_key = "health_check_test"
            cache.set(test_key, "test_value", 60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            return 'healthy' if retrieved_value == "test_value" else 'warning'
        except Exception as e:
            logger.error(f"Cache health check hatası: {e}")
            return 'warning'
    
    def _check_search_service(self) -> str:
        """Search service kontrolü"""
        try:
            search_service = SearchService()
            # Test arama
            results = search_service.semantic_search("test query", limit=1)
            return 'healthy'
        except Exception as e:
            logger.error(f"Search service health check hatası: {e}")
            return 'warning'
    
    def _check_embedding_service(self) -> str:
        """Embedding service kontrolü"""
        try:
            embedding_service = EmbeddingService()
            # Test embedding
            embedding = embedding_service.generate_embedding("test text")
            return 'healthy' if embedding else 'warning'
        except Exception as e:
            logger.error(f"Embedding service health check hatası: {e}")
            return 'warning'
    
    def _get_service_metrics(self) -> Dict[str, Any]:
        """Servis metriklerini al"""
        try:
            from datetime import timedelta
            
            # Son 24 saat içindeki istatistikler
            yesterday = timezone.now() - timedelta(days=1)
            
            recent_analytics = QueryAnalytics.objects.filter(
                created_at__gte=yesterday
            ).aggregate(
                total_queries=models.Count('id'),
                avg_response_time=models.Avg('response_time'),
                success_rate=models.Avg(
                    models.Case(
                        models.When(response_generated=True, then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                ),
                total_tokens=models.Sum('tokens_used')
            )
            
            # Aktif konuşma sayısı
            active_conversations = ChatConversation.objects.filter(
                is_active=True,
                last_activity__gte=yesterday
            ).count()
            
            # Cache hit rate (yaklaşık)
            cache_stats = chat_cache.get_cache_stats() if hasattr(chat_cache, 'get_cache_stats') else {}
            
            return {
                'last_24h_queries': recent_analytics['total_queries'] or 0,
                'avg_response_time': round(recent_analytics['avg_response_time'] or 0, 2),
                'success_rate': round((recent_analytics['success_rate'] or 0) * 100, 2),
                'total_tokens_used': recent_analytics['total_tokens'] or 0,
                'active_conversations': active_conversations,
                'cache_stats': cache_stats
            }
            
        except Exception as e:
            logger.error(f"Metrics alma hatası: {e}")
            return {}


class ChatServiceManager:
    """Chat servis yönetici sınıfı - Facade pattern"""
    
    def __init__(self):
        self.chat_service = RAGChatbotService()
        self.health_checker = ChatHealthChecker()
    
    async def process_message_async(
        self, 
        message: str, 
        session_id: str,
        user_type: str = 'user',
        user_profile: Optional[UserProfile] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """Asenkron mesaj işleme"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.chat_service.process_message,
            message, session_id, user_type, user_profile, metadata
        )
    
    def batch_process_messages(
        self, 
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Toplu mesaj işleme"""
        results = []
        
        for msg_data in messages:
            try:
                result = self.chat_service.process_message(
                    message=msg_data['message'],
                    session_id=msg_data['session_id'],
                    user_type=msg_data.get('user_type', 'user'),
                    user_profile=msg_data.get('user_profile'),
                    metadata=msg_data.get('metadata')
                )
                
                results.append({
                    'success': True,
                    'session_id': msg_data['session_id'],
                    'result': self.chat_service._serialize_rag_result(result)
                })
                
            except Exception as e:
                logger.error(f"Batch mesaj işleme hatası: {e}")
                results.append({
                    'success': False,
                    'session_id': msg_data['session_id'],
                    'error': str(e)
                })
        
        return results
    
    def get_service_status(self) -> Dict[str, Any]:
        """Servis durumunu al"""
        return self.health_checker.health_check()
    
    def cleanup_old_conversations(self, days_old: int = 30) -> Dict[str, int]:
        """Eski konuşmaları temizle"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            
            # Eski konuşmaları arşivle
            old_conversations = ChatConversation.objects.filter(
                last_activity__lt=cutoff_date,
                is_archived=False
            )
            
            archived_count = old_conversations.update(is_archived=True)
            
            # Çok eski mesajları soft delete
            very_old_date = timezone.now() - timedelta(days=days_old * 2)
            deleted_messages = ChatMessage.objects.filter(
                created_at__lt=very_old_date,
                is_active=True
            ).update(is_active=False)
            
            # Cache temizliği
            cache_keys_deleted = 0
            try:
                # Chat cache anahtarlarını temizle
                if hasattr(cache, 'delete_pattern'):
                    cache_keys_deleted = cache.delete_pattern("chat_history:*")
            except Exception as e:
                logger.warning(f"Cache temizlik hatası: {e}")
            
            logger.info(f"Cleanup tamamlandı: {archived_count} konuşma arşivlendi, {deleted_messages} mesaj silindi")
            
            return {
                'archived_conversations': archived_count,
                'deleted_messages': deleted_messages,
                'cache_keys_deleted': cache_keys_deleted
            }
            
        except Exception as e:
            logger.error(f"Cleanup hatası: {e}")
            return {'error': str(e)}
    
    def export_conversation(self, session_id: str, format: str = 'json') -> Dict[str, Any]:
        """Konuşmayı dışa aktar"""
        try:
            conversation = ChatConversation.objects.filter(
                session_id=session_id,
                is_active=True
            ).first()
            
            if not conversation:
                return {'error': 'Konuşma bulunamadı'}
            
            messages = ChatMessage.objects.filter(
                conversation=conversation,
                is_active=True
            ).order_by('created_at')
            
            export_data = {
                'conversation_id': str(conversation.id),
                'session_id': session_id,
                'user_type': conversation.user_type,
                'created_at': conversation.created_at.isoformat(),
                'message_count': messages.count(),
                'messages': []
            }
            
            for msg in messages:
                msg_data = {
                    'id': str(msg.id),
                    'type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'response_time': msg.response_time,
                    'intent': msg.intent_detected,
                    'confidence': msg.confidence_score
                }
                
                if msg.sources_used.exists():
                    msg_data['sources'] = [
                        {
                            'title': source.source.title,
                            'page': source.page_number,
                            'section': source.section_title
                        }
                        for source in msg.sources_used.all()
                    ]
                
                export_data['messages'].append(msg_data)
            
            return {
                'success': True,
                'format': format,
                'data': export_data,
                'exported_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Export hatası: {e}")
            return {'error': str(e)}


# Utility functions
def create_chat_service() -> RAGChatbotService:
    """Chat servisi factory fonksiyonu"""
    return RAGChatbotService()


def validate_chat_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chat isteği doğrulama"""
    validator = ChatMessageValidator()
    
    required_fields = ['message', 'session_id']
    for field in required_fields:
        if field not in data:
            raise ValidationException(f"Gerekli alan eksik: {field}", field=field)
    
    return {
        'message': validator.validate_message_content(data['message']),
        'session_id': validator.validate_session_id(data['session_id']),
        'user_type': validator.validate_user_type(data.get('user_type', 'user')),
        'context': validator.validate_context(data.get('context', {}))
    }


def get_chat_suggestions(query: str, user_type: str = 'user') -> List[str]:
    """Chat önerilerini al"""
    suggestions = []
    
    # SAP modül bazlı öneriler
    sap_suggestions = {
        'FI': [
            "Satış faturası nasıl kesilir?",
            "Muhasebe kaydı nasıl yapılır?",
            "Mali rapor nasıl alınır?",
            "Hesap planı nasıl oluşturulur?"
        ],
        'MM': [
            "Satın alma siparişi nasıl oluşturulur?",
            "Stok raporu nasıl alınır?",
            "Malzeme kartı nasıl tanımlanır?",
            "Tedarikçi nasıl eklenir?"
        ],
        'SD': [
            "Satış teklifi nasıl hazırlanır?",
            "Müşteri kartı nasıl oluşturulur?",
            "Sevkiyat nasıl yapılır?",
            "Fiyat listesi nasıl güncellenir?"
        ]
    }
    
    # Query'den SAP modülü tespit et
    detected_module = SAPTerminologyAnalyzer.get_primary_sap_module(query)
    
    if detected_module and detected_module in sap_suggestions:
        suggestions.extend(sap_suggestions[detected_module])
    else:
        # Genel öneriler
        suggestions.extend([
            "SAP Business One nedir?",
            "Sistem nasıl kullanılır?",
            "Yardım dökümanları nerede?",
            "Sistem ayarları nasıl değiştirilir?"
        ])
    
    # Kullanıcı tipine göre özelleştir
    if user_type == 'technical':
        suggestions.extend([
            "Veritabanı konfigürasyonu",
            "API entegrasyonu",
            "Sistem performansı"
        ])
    
    return suggestions[:5]  # En fazla 5 öneri


# Global service instance (singleton pattern)
_chat_service_instance = None

def get_chat_service() -> RAGChatbotService:
    """Global chat service instance'ını al"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = RAGChatbotService()
    return _chat_service_instance


# Service health monitoring
def monitor_chat_service():
    """Chat servis monitoring - Celery task için"""
    try:
        health_checker = ChatHealthChecker()
        health_status = health_checker.health_check()
        
        if health_status['status'] != 'healthy':
            logger.warning(f"Chat service health warning: {health_status}")
            
            # Critical durumlarda alert gönder
            if health_status['status'] == 'critical':
                # Alert sistemi entegrasyonu burada olacak
                pass
        
        return health_status
        
    except Exception as e:
        logger.error(f"Chat service monitoring hatası: {e}")
        return {'status': 'critical', 'error': str(e)}