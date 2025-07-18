# backend/sapbot_api/services/search_service.py
"""
SAPBot API Semantic Search Service

Bu modül vector-based semantic search, relevance ranking ve
SAP B1 özelinde optimize edilmiş arama fonksiyonlarını içerir.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.utils import timezone

import json

from ..models import KnowledgeChunk, QueryAnalytics
from ..utils.cache_utils import search_cache, embedding_cache
from ..utils.text_processing import (
   TextAnalyzer, 
   SAPTerminologyAnalyzer,
   normalize_text_for_search
)
from ..utils.exceptions import SearchError, ValidationException
from ..utils.helpers import generate_hash
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SemanticSearchService:
   """Semantic search ana servisi"""
   
   def __init__(self):
       self.embedding_service = EmbeddingService()
       self.similarity_threshold = getattr(settings, 'SEMANTIC_SEARCH_THRESHOLD', 0.7)
       self.max_results = getattr(settings, 'MAX_SEARCH_RESULTS', 50)
       self.cache_timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 1800)  # 30 dakika
   
   async def search(
       self,
       query: str,
       user_type: str = 'user',
       filters: Optional[Dict[str, Any]] = None,
       limit: int = 10,
       min_relevance: float = 0.5
   ) -> Dict[str, Any]:
       """Ana arama fonksiyonu"""
       try:
           start_time = timezone.now()
           
           # Query normalleştir ve analiz et
           normalized_query = normalize_text_for_search(query)
           analysis = TextAnalyzer.analyze_text(query)
           
           # Cache kontrolü
           cache_key = self._generate_cache_key(normalized_query, filters, user_type, limit)
           cached_results = search_cache.get(cache_key)
           
           if cached_results:
               logger.info(f"Search cache hit for query: {query[:50]}...")
               return cached_results
           
           # Query embedding oluştur
           query_embedding = await self._get_query_embedding(normalized_query)
           
           # Parallel olarak hem vector search hem de keyword search yap
           tasks = [
               self._vector_search(query_embedding, filters, limit * 2, min_relevance),
               self._keyword_search(normalized_query, filters, limit),
               self._sap_specific_search(query, analysis, filters, limit)
           ]
           
           vector_results, keyword_results, sap_results = await asyncio.gather(*tasks)
           
           # Sonuçları birleştir ve rank et
           combined_results = self._combine_and_rank_results(
               vector_results, 
               keyword_results, 
               sap_results,
               query,
               analysis,
               user_type
           )
           
           # Final filtering ve limiting
           final_results = self._filter_and_limit_results(
               combined_results, 
               filters, 
               limit, 
               min_relevance
           )
           
           # Response formatla
           response = {
               'query': query,
               'query_analysis': {
                   'language': analysis.language,
                   'sap_modules': analysis.sap_modules,
                   'technical_level': analysis.technical_level,
                   'intent': analysis.intent,
                   'confidence': analysis.confidence
               },
               'results': final_results,
               'total_found': len(final_results),
               'search_time': (timezone.now() - start_time).total_seconds(),
               'cached': False
           }
           
           # Cache'e kaydet
           search_cache.set(cache_key, response, self.cache_timeout)
           
           # Analytics kaydet
           self._log_search_analytics(query, analysis, len(final_results), user_type)
           
           return response
           
       except Exception as e:
           logger.error(f"Search error for query '{query}': {str(e)}")
           raise SearchError(
               message=f"Arama sırasında hata oluştu: {str(e)}",
               query=query
           )
   
   async def _get_query_embedding(self, query: str) -> List[float]:
       """Query embedding'i al (cache'li)"""
       query_hash = generate_hash(query)
       
       # Cache'den kontrol et
       cached_embedding = embedding_cache.get_embedding(query_hash)
       if cached_embedding:
           return cached_embedding
       
       # Yeni embedding oluştur
       embedding = await asyncio.get_event_loop().run_in_executor(
           None, 
           self.embedding_service.generate_embedding, 
           query
       )
       
       # Cache'e kaydet
       embedding_cache.set_embedding(query_hash, embedding)
       
       return embedding
   
   async def _vector_search(
       self,
       query_embedding: List[float],
       filters: Dict[str, Any],
       limit: int,
       min_relevance: float
   ) -> List[Dict[str, Any]]:
       """Vector similarity search"""
       try:
           # PostgreSQL vector similarity query
           from django.db import connection
           
           filter_conditions = []
           filter_params = []
           
           # Filtre koşullarını oluştur
           if filters:
               if filters.get('sap_module'):
                   filter_conditions.append("sap_module = %s")
                   filter_params.append(filters['sap_module'])
               
               if filters.get('technical_level'):
                   filter_conditions.append("technical_level = %s")
                   filter_params.append(filters['technical_level'])
               
               if filters.get('language'):
                   filter_conditions.append("source.language = %s")
                   filter_params.append(filters['language'])
           
           # Base query
           where_clause = "WHERE kc.is_active = true"
           if filter_conditions:
               where_clause += " AND " + " AND ".join(filter_conditions)
           
           sql = f"""
           SELECT 
               kc.id,
               kc.content,
               kc.content_hash,
               kc.sap_module,
               kc.technical_level,
               kc.page_number,
               kc.section_title,
               kc.usage_count,
               kc.relevance_score,
               ds.title as source_title,
               ds.document_type,
               ds.language,
               (kc.embedding <-> %s::vector) as distance,
               1 - (kc.embedding <-> %s::vector) as similarity
           FROM sapbot_knowledge_chunks kc
           JOIN sapbot_document_sources ds ON kc.source_id = ds.id
           {where_clause}
           AND kc.embedding IS NOT NULL
           ORDER BY kc.embedding <-> %s::vector
           LIMIT %s
           """
           
           params = [query_embedding, query_embedding, query_embedding, limit] + filter_params
           
           with connection.cursor() as cursor:
               cursor.execute(sql, params)
               results = cursor.fetchall()
           
           # Sonuçları formatla
           formatted_results = []
           for row in results:
               similarity = float(row[13])
               
               if similarity >= min_relevance:
                   formatted_results.append({
                       'id': str(row[0]),
                       'content': row[1],
                       'content_hash': row[2],
                       'sap_module': row[3],
                       'technical_level': row[4],
                       'page_number': row[5],
                       'section_title': row[6],
                       'usage_count': row[7],
                       'base_relevance_score': float(row[8]),
                       'source': {
                           'title': row[9],
                           'document_type': row[10],
                           'language': row[11]
                       },
                       'similarity_score': similarity,
                       'search_type': 'vector'
                   })
           
           logger.info(f"Vector search found {len(formatted_results)} results")
           return formatted_results
           
       except Exception as e:
           logger.error(f"Vector search error: {str(e)}")
           return []
   
   async def _keyword_search(
       self,
       query: str,
       filters: Dict[str, Any],
       limit: int
   ) -> List[Dict[str, Any]]:
       """Traditional keyword search"""
       try:
           # Django ORM ile full-text search
           queryset = KnowledgeChunk.objects.select_related('source').filter(
               is_active=True,
               source__is_active=True
           )
           
           # Filtreler
           if filters:
               if filters.get('sap_module'):
                   queryset = queryset.filter(sap_module=filters['sap_module'])
               
               if filters.get('technical_level'):
                   queryset = queryset.filter(technical_level=filters['technical_level'])
               
               if filters.get('language'):
                   queryset = queryset.filter(source__language=filters['language'])
           
           # Full-text search (PostgreSQL)
           search_vector = models.F('content')
           queryset = queryset.extra(
               select={
                   'rank': "ts_rank_cd(to_tsvector('turkish', content), plainto_tsquery('turkish', %s))"
               },
               select_params=[query],
               where=[
                   "to_tsvector('turkish', content) @@ plainto_tsquery('turkish', %s)"
               ],
               params=[query],
               order_by=['-rank', '-usage_count']
           )[:limit]
           
           # Sonuçları formatla
           results = []
           for chunk in queryset:
               results.append({
                   'id': str(chunk.id),
                   'content': chunk.content,
                   'content_hash': chunk.content_hash,
                   'sap_module': chunk.sap_module,
                   'technical_level': chunk.technical_level,
                   'page_number': chunk.page_number,
                   'section_title': chunk.section_title,
                   'usage_count': chunk.usage_count,
                   'base_relevance_score': chunk.relevance_score,
                   'source': {
                       'title': chunk.source.title,
                       'document_type': chunk.source.document_type,
                       'language': chunk.source.language
                   },
                   'keyword_rank': getattr(chunk, 'rank', 0.0),
                   'search_type': 'keyword'
               })
           
           logger.info(f"Keyword search found {len(results)} results")
           return results
           
       except Exception as e:
           logger.error(f"Keyword search error: {str(e)}")
           return []
   
   async def _sap_specific_search(
       self,
       query: str,
       analysis: Any,
       filters: Dict[str, Any],
       limit: int
   ) -> List[Dict[str, Any]]:
       """SAP-specific search (transaction codes, document numbers, etc.)"""
       try:
           results = []
           
           # SAP transaction code arama
           tcode_pattern = r'\b[A-Z]{2,4}[0-9]{1,3}[A-Z]?\b'
           import re
           tcodes = re.findall(tcode_pattern, query.upper())
           
           if tcodes:
               for tcode in tcodes:
                   tcode_results = await self._search_by_transaction_code(tcode, filters, limit // 2)
                   results.extend(tcode_results)
           
           # SAP modül bazlı arama
           if analysis.sap_modules:
               for sap_module in analysis.sap_modules[:2]:  # İlk 2 modül
                   module_results = await self._search_by_sap_module(
                       query, sap_module, filters, limit // 2
                   )
                   results.extend(module_results)
           
           # Döküman numarası arama
           doc_pattern = r'\b[0-9]{8,10}\b'
           doc_numbers = re.findall(doc_pattern, query)
           
           if doc_numbers:
               for doc_num in doc_numbers:
                   doc_results = await self._search_by_document_number(doc_num, filters, limit // 2)
                   results.extend(doc_results)
           
           logger.info(f"SAP-specific search found {len(results)} results")
           return results
           
       except Exception as e:
           logger.error(f"SAP-specific search error: {str(e)}")
           return []
   
   async def _search_by_transaction_code(
       self,
       tcode: str,
       filters: Dict[str, Any],
       limit: int
   ) -> List[Dict[str, Any]]:
       """Transaction code bazlı arama"""
       try:
           queryset = KnowledgeChunk.objects.select_related('source').filter(
               is_active=True,
               source__is_active=True,
               content__icontains=tcode
           )
           
           # Filtreler
           if filters:
               if filters.get('sap_module'):
                   queryset = queryset.filter(sap_module=filters['sap_module'])
               
               if filters.get('technical_level'):
                   queryset = queryset.filter(technical_level=filters['technical_level'])
           
           results = []
           for chunk in queryset[:limit]:
               results.append({
                   'id': str(chunk.id),
                   'content': chunk.content,
                   'content_hash': chunk.content_hash,
                   'sap_module': chunk.sap_module,
                   'technical_level': chunk.technical_level,
                   'page_number': chunk.page_number,
                   'section_title': chunk.section_title,
                   'usage_count': chunk.usage_count,
                   'base_relevance_score': chunk.relevance_score,
                   'source': {
                       'title': chunk.source.title,
                       'document_type': chunk.source.document_type,
                       'language': chunk.source.language
                   },
                   'match_type': 'transaction_code',
                   'matched_tcode': tcode,
                   'search_type': 'sap_specific'
               })
           
           return results
           
       except Exception as e:
           logger.error(f"Transaction code search error: {str(e)}")
           return []
   
   async def _search_by_sap_module(
       self,
       query: str,
       sap_module: str,
       filters: Dict[str, Any],
       limit: int
   ) -> List[Dict[str, Any]]:
       """SAP modül bazlı arama"""
       try:
           # Modül-specific terminoloji ile arama
           module_terms = SAPTerminologyAnalyzer.SAP_MODULES.get(sap_module, {})
           search_terms = module_terms.get('turkish', []) + module_terms.get('english', [])
           
           results = []
           for term in search_terms[:5]:  # İlk 5 terim
               if term.lower() in query.lower():
                   term_results = KnowledgeChunk.objects.select_related('source').filter(
                       is_active=True,
                       source__is_active=True,
                       sap_module=sap_module,
                       content__icontains=term
                   ).order_by('-relevance_score', '-usage_count')[:limit // 5]
                   
                   for chunk in term_results:
                       results.append({
                           'id': str(chunk.id),
                           'content': chunk.content,
                           'content_hash': chunk.content_hash,
                           'sap_module': chunk.sap_module,
                           'technical_level': chunk.technical_level,
                           'page_number': chunk.page_number,
                           'section_title': chunk.section_title,
                           'usage_count': chunk.usage_count,
                           'base_relevance_score': chunk.relevance_score,
                           'source': {
                               'title': chunk.source.title,
                               'document_type': chunk.source.document_type,
                               'language': chunk.source.language
                           },
                           'match_type': 'sap_module',
                           'matched_module': sap_module,
                           'matched_term': term,
                           'search_type': 'sap_specific'
                       })
           
           return results
           
       except Exception as e:
           logger.error(f"SAP module search error: {str(e)}")
           return []
   
   async def _search_by_document_number(
       self,
       doc_number: str,
       filters: Dict[str, Any],
       limit: int
   ) -> List[Dict[str, Any]]:
       """Döküman numarası bazlı arama"""
       try:
           queryset = KnowledgeChunk.objects.select_related('source').filter(
               is_active=True,
               source__is_active=True,
               content__icontains=doc_number
           ).order_by('-relevance_score')[:limit]
           
           results = []
           for chunk in queryset:
               results.append({
                   'id': str(chunk.id),
                   'content': chunk.content,
                   'content_hash': chunk.content_hash,
                   'sap_module': chunk.sap_module,
                   'technical_level': chunk.technical_level,
                   'page_number': chunk.page_number,
                   'section_title': chunk.section_title,
                   'usage_count': chunk.usage_count,
                   'base_relevance_score': chunk.relevance_score,
                   'source': {
                       'title': chunk.source.title,
                       'document_type': chunk.source.document_type,
                       'language': chunk.source.language
                   },
                   'match_type': 'document_number',
                   'matched_doc_number': doc_number,
                   'search_type': 'sap_specific'
               })
           
           return results
           
       except Exception as e:
           logger.error(f"Document number search error: {str(e)}")
           return []
   
   def _combine_and_rank_results(
       self,
       vector_results: List[Dict],
       keyword_results: List[Dict],
       sap_results: List[Dict],
       query: str,
       analysis: Any,
       user_type: str
   ) -> List[Dict[str, Any]]:
       """Sonuçları birleştir ve ranking yap"""
       try:
           # Tüm sonuçları birleştir
           all_results = {}
           
           # Vector sonuçlarını ekle
           for result in vector_results:
               chunk_id = result['id']
               if chunk_id not in all_results:
                   all_results[chunk_id] = result.copy()
                   all_results[chunk_id]['scores'] = {}
               
               all_results[chunk_id]['scores']['vector'] = result['similarity_score']
           
           # Keyword sonuçlarını ekle
           for result in keyword_results:
               chunk_id = result['id']
               if chunk_id not in all_results:
                   all_results[chunk_id] = result.copy()
                   all_results[chunk_id]['scores'] = {}
               
               all_results[chunk_id]['scores']['keyword'] = result.get('keyword_rank', 0.0)
           
           # SAP-specific sonuçlarını ekle
           for result in sap_results:
               chunk_id = result['id']
               if chunk_id not in all_results:
                   all_results[chunk_id] = result.copy()
                   all_results[chunk_id]['scores'] = {}
               
               all_results[chunk_id]['scores']['sap_specific'] = 1.0  # Yüksek puan
               all_results[chunk_id]['match_type'] = result.get('match_type', 'unknown')
           
           # Final scoring ve ranking
           final_results = []
           for chunk_id, result in all_results.items():
               final_score = self._calculate_final_score(result, query, analysis, user_type)
               result['final_relevance_score'] = final_score
               final_results.append(result)
           
           # Score'a göre sırala
           final_results.sort(key=lambda x: x['final_relevance_score'], reverse=True)
           
           return final_results
           
       except Exception as e:
           logger.error(f"Result combination error: {str(e)}")
           return []
   
   def _calculate_final_score(
       self,
       result: Dict[str, Any],
       query: str,
       analysis: Any,
       user_type: str
   ) -> float:
       """Final relevance score hesapla"""
       try:
           scores = result.get('scores', {})
           base_score = result.get('base_relevance_score', 1.0)
           
           # Başlangıç skoru
           final_score = base_score * 0.3
           
           # Vector similarity
           if 'vector' in scores:
               final_score += scores['vector'] * 0.4
           
           # Keyword rank
           if 'keyword' in scores:
               keyword_normalized = min(scores['keyword'] / 1.0, 1.0)  # Normalize
               final_score += keyword_normalized * 0.2
           
           # SAP-specific bonus
           if 'sap_specific' in scores:
               final_score += scores['sap_specific'] * 0.1
           
           # Bonus faktörler
           
           # SAP modül uyumu
           if analysis.sap_modules and result.get('sap_module') in analysis.sap_modules:
               final_score *= 1.2
           
           # Teknik seviye uyumu
           if result.get('technical_level') == analysis.technical_level:
               final_score *= 1.1
           
           # User type uyumu
           user_type_bonus = {
               'user': {'user': 1.1, 'admin': 0.9, 'developer': 0.8},
               'technical': {'user': 0.9, 'admin': 1.1, 'developer': 1.0},
               'admin': {'user': 0.8, 'admin': 1.2, 'developer': 1.1}
           }
           
           result_tech_level = result.get('technical_level', 'user')
           if user_type in user_type_bonus and result_tech_level in user_type_bonus[user_type]:
               final_score *= user_type_bonus[user_type][result_tech_level]
           
           # Usage count bonus (popülerlik)
           usage_bonus = min(result.get('usage_count', 0) / 100.0, 0.1)
           final_score += usage_bonus
           
           # Content freshness (yeni dökümanlar)
           if hasattr(result.get('source', {}), 'created_at'):
               # Son 30 gün içinde oluşturulan dökümanlar bonus alır
               now = timezone.now()
               created_at = result['source'].get('created_at', now)
               if isinstance(created_at, str):
                   from dateutil.parser import parse
                   created_at = parse(created_at)
               
               days_old = (now - created_at).days
               if days_old <= 30:
                   freshness_bonus = (30 - days_old) / 30 * 0.05
                   final_score += freshness_bonus
           
           # Intent uyumu
           intent_keywords = {
               'how_to': ['nasıl', 'adım', 'step', 'guide'],
               'error_solving': ['hata', 'error', 'sorun', 'problem'],
               'configuration': ['ayar', 'setting', 'config'],
               'explanation': ['nedir', 'what', 'açıkla', 'explain']
           }
           
           if analysis.intent in intent_keywords:
               content_lower = result.get('content', '').lower()
               for keyword in intent_keywords[analysis.intent]:
                   if keyword in content_lower:
                       final_score *= 1.05
                       break
           
           # Score'u 0-1 arasında normalize et
           final_score = min(max(final_score, 0.0), 1.0)
           
           return final_score
           
       except Exception as e:
           logger.error(f"Final score calculation error: {str(e)}")
           return 0.5
   
   def _filter_and_limit_results(
       self,
       results: List[Dict[str, Any]],
       filters: Dict[str, Any],
       limit: int,
       min_relevance: float
   ) -> List[Dict[str, Any]]:
       """Son filtreleme ve limiting"""
       try:
           # Minimum relevance filter
           filtered_results = [
               result for result in results 
               if result.get('final_relevance_score', 0.0) >= min_relevance
           ]
           
           # Duplicate removal (content hash bazlı)
           seen_hashes = set()
           unique_results = []
           
           for result in filtered_results:
               content_hash = result.get('content_hash')
               if content_hash and content_hash not in seen_hashes:
                   seen_hashes.add(content_hash)
                   unique_results.append(result)
           
           # Limit uygula
           return unique_results[:limit]
           
       except Exception as e:
           logger.error(f"Filter and limit error: {str(e)}")
           return results[:limit]
   
   def _generate_cache_key(
       self,
       query: str,
       filters: Dict[str, Any],
       user_type: str,
       limit: int
   ) -> str:
       """Cache key oluştur"""
       key_parts = [
           'search',
           generate_hash(query)[:16],
           user_type,
           str(limit)
       ]
       
       if filters:
           filter_str = json.dumps(filters, sort_keys=True)
           key_parts.append(generate_hash(filter_str)[:8])
       
       return ':'.join(key_parts)
   
   def _log_search_analytics(
       self,
       query: str,
       analysis: Any,
       result_count: int,
       user_type: str
   ):
       """Arama analytics'ini kaydet"""
       try:
           QueryAnalytics.objects.create(
               query=query,
               query_hash=generate_hash(query),
               query_length=len(query),
               user_type=user_type,
               sap_module_detected=analysis.sap_modules[0] if analysis.sap_modules else None,
               intent_detected=analysis.intent,
               confidence_score=analysis.confidence,
               response_generated=result_count > 0,
               sources_used_count=result_count,
               language_detected=analysis.language,
               metadata={
                   'search_type': 'semantic',
                   'result_count': result_count,
                   'technical_level': analysis.technical_level
               }
           )
       except Exception as e:
           logger.error(f"Analytics logging error: {str(e)}")


class SearchSuggestionService:
   """Arama önerisi servisi"""
   
   def __init__(self):
       self.cache_timeout = 3600  # 1 saat
   
   def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
       """Arama önerileri al"""
       try:
           cache_key = f"search_suggestions:{generate_hash(partial_query)[:12]}"
           cached_suggestions = cache.get(cache_key)
           
           if cached_suggestions:
               return cached_suggestions
           
           suggestions = []
           
           # Popüler sorgular
           popular_queries = self._get_popular_queries(partial_query, limit)
           suggestions.extend(popular_queries)
           
           # SAP terminolojisi
           sap_suggestions = self._get_sap_terminology_suggestions(partial_query, limit)
           suggestions.extend(sap_suggestions)
           
           # Content-based suggestions
           content_suggestions = self._get_content_based_suggestions(partial_query, limit)
           suggestions.extend(content_suggestions)
           
           # Deduplicate ve limit
           unique_suggestions = list(dict.fromkeys(suggestions))[:limit]
           
           # Cache'e kaydet
           cache.set(cache_key, unique_suggestions, self.cache_timeout)
           
           return unique_suggestions
           
       except Exception as e:
           logger.error(f"Suggestion generation error: {str(e)}")
           return []
   
   def _get_popular_queries(self, partial_query: str, limit: int) -> List[str]:
       """Popüler sorgulardan öneriler"""
       try:
           # Son 30 gün içindeki popüler sorgular
           cutoff_date = timezone.now() - timedelta(days=30)
           
           popular = QueryAnalytics.objects.filter(
               created_at__gte=cutoff_date,
               query__icontains=partial_query,
               response_generated=True
           ).values('query').annotate(
               count=models.Count('query')
           ).order_by('-count')[:limit]
           
           return [item['query'] for item in popular]
           
       except Exception as e:
           logger.error(f"Popular queries error: {str(e)}")
           return []
   
   def _get_sap_terminology_suggestions(self, partial_query: str, limit: int) -> List[str]:
       """SAP terminolojisinden öneriler"""
       try:
           suggestions = []
           partial_lower = partial_query.lower()
           
           # Tüm SAP modül terminolojilerini kontrol et
           for module, terms in SAPTerminologyAnalyzer.SAP_MODULES.items():
               for term in terms.get('turkish', []) + terms.get('english', []):
                   if partial_lower in term.lower() and term not in suggestions:
                       suggestions.append(term)
                       if len(suggestions) >= limit:
                           break
               
               if len(suggestions) >= limit:
                   break
           
           return suggestions
           
       except Exception as e:
           logger.error(f"SAP terminology suggestions error: {str(e)}")
           return []
   
   def _get_content_based_suggestions(self, partial_query: str, limit: int) -> List[str]:
       """İçerik bazlı öneriler"""
       try:
           # Section title'lardan öneriler
           sections = KnowledgeChunk.objects.filter(
               is_active=True,
               section_title__icontains=partial_query
           ).values_list('section_title', flat=True).distinct()[:limit]
           return [section for section in sections if section]
           
       except Exception as e:
           logger.error(f"Content-based suggestions error: {str(e)}")
           return []


class SearchResultEnhancer:
   """Arama sonuçlarını zenginleştirme servisi"""
   
   def __init__(self):
       self.embedding_service = EmbeddingService()
   
   def enhance_results(
       self,
       results: List[Dict[str, Any]],
       query: str,
       user_context: Optional[Dict[str, Any]] = None
   ) -> List[Dict[str, Any]]:
       """Arama sonuçlarını zenginleştir"""
       try:
           enhanced_results = []
           
           for result in results:
               enhanced_result = result.copy()
               
               # Highlight ekleme
               enhanced_result['highlighted_content'] = self._highlight_content(
                   result.get('content', ''), query
               )
               
               # İlgili chunks ekleme
               enhanced_result['related_chunks'] = self._find_related_chunks(
                   result, query, limit=3
               )
               
               # Kullanıcı için personalization
               if user_context:
                   enhanced_result['personalized_score'] = self._calculate_personalized_score(
                       result, user_context
                   )
               
               # Quick actions ekleme
               enhanced_result['quick_actions'] = self._generate_quick_actions(result, query)
               
               enhanced_results.append(enhanced_result)
           
           return enhanced_results
           
       except Exception as e:
           logger.error(f"Result enhancement error: {str(e)}")
           return results
   
   def _highlight_content(self, content: str, query: str) -> str:
       """İçerikte query terms'leri highlight et"""
       try:
           import re
           
           # Query'yi kelimelerine ayır
           query_words = query.lower().split()
           highlighted_content = content
           
           for word in query_words:
               if len(word) > 2:  # Çok kısa kelimeler için highlight yapma
                   pattern = re.compile(re.escape(word), re.IGNORECASE)
                   highlighted_content = pattern.sub(
                       f'<mark>{word}</mark>', 
                       highlighted_content
                   )
           
           return highlighted_content
           
       except Exception as e:
           logger.error(f"Content highlighting error: {str(e)}")
           return content
   
   def _find_related_chunks(
       self,
       result: Dict[str, Any],
       query: str,
       limit: int = 3
   ) -> List[Dict[str, Any]]:
       """İlgili chunk'ları bul"""
       try:
           chunk_id = result['id']
           sap_module = result.get('sap_module')
           source_title = result.get('source', {}).get('title', '')
           
           # Aynı SAP modülünden benzer chunks
           related = KnowledgeChunk.objects.filter(
               is_active=True,
               sap_module=sap_module
           ).exclude(
               id=chunk_id
           ).select_related('source')
           
           # Aynı dökümanından chunks
           if source_title:
               related = related.filter(source__title=source_title)
           
           related_chunks = []
           for chunk in related[:limit]:
               related_chunks.append({
                   'id': str(chunk.id),
                   'title': chunk.section_title or 'Bölüm',
                   'content_preview': chunk.content[:150] + '...',
                   'page_number': chunk.page_number,
                   'relevance_score': chunk.relevance_score
               })
           
           return related_chunks
           
       except Exception as e:
           logger.error(f"Related chunks error: {str(e)}")
           return []
   
   def _calculate_personalized_score(
       self,
       result: Dict[str, Any],
       user_context: Dict[str, Any]
   ) -> float:
       """Kullanıcı için kişiselleştirilmiş skor"""
       try:
           base_score = result.get('final_relevance_score', 0.5)
           
           # Kullanıcının sık kullandığı SAP modülleri
           user_modules = user_context.get('frequent_sap_modules', [])
           if result.get('sap_module') in user_modules:
               base_score += 0.1
           
           # Kullanıcının tercih ettiği teknik seviye
           user_tech_level = user_context.get('preferred_tech_level', 'user')
           if result.get('technical_level') == user_tech_level:
               base_score += 0.05
           
           # Kullanıcının daha önce benzer konularda yaptığı aramalar
           user_search_history = user_context.get('search_history_topics', [])
           result_topics = result.get('keywords', [])
           
           common_topics = set(user_search_history) & set(result_topics)
           if common_topics:
               base_score += len(common_topics) * 0.02
           
           return min(base_score, 1.0)
           
       except Exception as e:
           logger.error(f"Personalized score error: {str(e)}")
           return result.get('final_relevance_score', 0.5)
   
   def _generate_quick_actions(
       self,
       result: Dict[str, Any],
       query: str
   ) -> List[Dict[str, str]]:
       """Quick action'lar oluştur"""
       try:
           actions = []
           
           # SAP transaction code varsa
           content = result.get('content', '')
           import re
           
           tcodes = re.findall(r'\b[A-Z]{2,4}[0-9]{1,3}[A-Z]?\b', content)
           if tcodes:
               actions.append({
                   'type': 'transaction',
                   'label': f'Go to {tcodes[0]}',
                   'action': f'open_transaction:{tcodes[0]}'
               })
           
           # Döküman açma
           if result.get('source'):
               actions.append({
                   'type': 'document',
                   'label': 'Open Full Document',
                   'action': f"open_document:{result['source'].get('id', '')}"
               })
           
           # Benzer sonuçlar
           actions.append({
               'type': 'search',
               'label': 'Find Similar',
               'action': f"search_similar:{result['id']}"
           })
           
           # Sayfa gösterme
           if result.get('page_number'):
               actions.append({
                   'type': 'page',
                   'label': f"Go to Page {result['page_number']}",
                   'action': f"goto_page:{result.get('source', {}).get('id', '')}:{result['page_number']}"
               })
           
           return actions
           
       except Exception as e:
           logger.error(f"Quick actions error: {str(e)}")
           return []


class SearchAnalyticsService:
   """Arama analytics servisi"""
   
   def get_search_analytics(
       self,
       start_date: Optional[datetime] = None,
       end_date: Optional[datetime] = None,
       groupby: str = 'day'
   ) -> Dict[str, Any]:
       """Arama analytics verilerini al"""
       try:
           if not start_date:
               start_date = timezone.now() - timedelta(days=30)
           if not end_date:
               end_date = timezone.now()
           
           queryset = QueryAnalytics.objects.filter(
               created_at__range=[start_date, end_date]
           )
           
           # Temel istatistikler
           total_queries = queryset.count()
           successful_queries = queryset.filter(response_generated=True).count()
           unique_users = queryset.values('session_id').distinct().count()
           
           # SAP modül dağılımı
           sap_module_distribution = list(
               queryset.exclude(sap_module_detected__isnull=True)
               .values('sap_module_detected')
               .annotate(count=models.Count('sap_module_detected'))
               .order_by('-count')[:10]
           )
           
           # Intent dağılımı
           intent_distribution = list(
               queryset.exclude(intent_detected__isnull=True)
               .values('intent_detected')
               .annotate(count=models.Count('intent_detected'))
               .order_by('-count')
           )
           
           # Kullanıcı tipi dağılımı
           user_type_distribution = list(
               queryset.values('user_type')
               .annotate(count=models.Count('user_type'))
               .order_by('-count')
           )
           
           # Popüler sorgular
           popular_queries = list(
               queryset.filter(response_generated=True)
               .values('query')
               .annotate(count=models.Count('query'))
               .order_by('-count')[:20]
           )
           
           # Zaman bazlı trend
           if groupby == 'hour':
               time_trends = self._get_hourly_trends(queryset)
           elif groupby == 'day':
               time_trends = self._get_daily_trends(queryset)
           elif groupby == 'week':
               time_trends = self._get_weekly_trends(queryset)
           else:
               time_trends = self._get_daily_trends(queryset)
           
           return {
               'summary': {
                   'total_queries': total_queries,
                   'successful_queries': successful_queries,
                   'success_rate': successful_queries / total_queries if total_queries > 0 else 0,
                   'unique_users': unique_users,
                   'avg_queries_per_user': total_queries / unique_users if unique_users > 0 else 0
               },
               'distributions': {
                   'sap_modules': sap_module_distribution,
                   'intents': intent_distribution,
                   'user_types': user_type_distribution
               },
               'popular_queries': popular_queries,
               'time_trends': time_trends,
               'period': {
                   'start_date': start_date.isoformat(),
                   'end_date': end_date.isoformat(),
                   'groupby': groupby
               }
           }
           
       except Exception as e:
           logger.error(f"Search analytics error: {str(e)}")
           return {}
   
   def _get_daily_trends(self, queryset) -> List[Dict[str, Any]]:
       """Günlük trendler"""
       try:
           from django.db.models import Count
           from django.db.models.functions import TruncDate
           
           daily_data = queryset.annotate(
               date=TruncDate('created_at')
           ).values('date').annotate(
               total_queries=Count('id'),
               successful_queries=Count('id', filter=models.Q(response_generated=True))
           ).order_by('date')
           
           return [
               {
                   'date': item['date'].isoformat(),
                   'total_queries': item['total_queries'],
                   'successful_queries': item['successful_queries'],
                   'success_rate': item['successful_queries'] / item['total_queries'] if item['total_queries'] > 0 else 0
               }
               for item in daily_data
           ]
           
       except Exception as e:
           logger.error(f"Daily trends error: {str(e)}")
           return []
   
   def _get_hourly_trends(self, queryset) -> List[Dict[str, Any]]:
       """Saatlik trendler"""
       try:
           from django.db.models import Count
           from django.db.models.functions import TruncHour
           
           hourly_data = queryset.annotate(
               hour=TruncHour('created_at')
           ).values('hour').annotate(
               total_queries=Count('id'),
               successful_queries=Count('id', filter=models.Q(response_generated=True))
           ).order_by('hour')
           
           return [
               {
                   'hour': item['hour'].isoformat(),
                   'total_queries': item['total_queries'],
                   'successful_queries': item['successful_queries']
               }
               for item in hourly_data
           ]
           
       except Exception as e:
           logger.error(f"Hourly trends error: {str(e)}")
           return []
   
   def _get_weekly_trends(self, queryset) -> List[Dict[str, Any]]:
       """Haftalık trendler"""
       try:
           from django.db.models import Count
           from django.db.models.functions import TruncWeek
           
           weekly_data = queryset.annotate(
               week=TruncWeek('created_at')
           ).values('week').annotate(
               total_queries=Count('id'),
               successful_queries=Count('id', filter=models.Q(response_generated=True))
           ).order_by('week')
           
           return [
               {
                   'week': item['week'].isoformat(),
                   'total_queries': item['total_queries'],
                   'successful_queries': item['successful_queries']
               }
               for item in weekly_data
           ]
           
       except Exception as e:
           logger.error(f"Weekly trends error: {str(e)}")
           return []


# Service singletons
semantic_search_service = SemanticSearchService()
search_suggestion_service = SearchSuggestionService()
search_result_enhancer = SearchResultEnhancer()
search_analytics_service = SearchAnalyticsService()


# Utility functions
async def search_knowledge(
   query: str,
   user_type: str = 'user',
   filters: Optional[Dict[str, Any]] = None,
   limit: int = 10,
   min_relevance: float = 0.5,
   enhance_results: bool = True,
   user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
   """Ana arama utility fonksiyonu"""
   
   # Temel arama
   search_results = await semantic_search_service.search(
       query=query,
       user_type=user_type,
       filters=filters or {},
       limit=limit,
       min_relevance=min_relevance
   )
   
   # Sonuçları zenginleştir
   if enhance_results and search_results.get('results'):
       search_results['results'] = search_result_enhancer.enhance_results(
           search_results['results'],
           query,
           user_context
       )
   
   return search_results


def get_search_suggestions(partial_query: str, limit: int = 5) -> List[str]:
   """Arama önerileri utility fonksiyonu"""
   return search_suggestion_service.get_suggestions(partial_query, limit)


def get_search_analytics(
   start_date: Optional[datetime] = None,
   end_date: Optional[datetime] = None,
   groupby: str = 'day'
) -> Dict[str, Any]:
   """Arama analytics utility fonksiyonu"""
   return search_analytics_service.get_search_analytics(start_date, end_date, groupby)


async def search_by_chunk_similarity(
   chunk_id: str,
   limit: int = 10,
   min_similarity: float = 0.7
) -> List[Dict[str, Any]]:
   """Belirli bir chunk'a benzer chunks bul"""
   try:
       # Chunk'ı al
       chunk = KnowledgeChunk.objects.select_related('source').get(
           id=chunk_id,
           is_active=True
       )
       
       if not chunk.embedding:
           raise SearchError("Chunk embedding bulunamadı")
       
       # Benzer chunk'ları bul
       from django.db import connection
       
       sql = """
       SELECT 
           kc.id,
           kc.content,
           kc.sap_module,
           kc.technical_level,
           kc.section_title,
           ds.title as source_title,
           1 - (kc.embedding <-> %s::vector) as similarity
       FROM sapbot_knowledge_chunks kc
       JOIN sapbot_document_sources ds ON kc.source_id = ds.id
       WHERE kc.is_active = true 
       AND kc.id != %s
       AND kc.embedding IS NOT NULL
       ORDER BY kc.embedding <-> %s::vector
       LIMIT %s
       """
       
       with connection.cursor() as cursor:
           cursor.execute(sql, [chunk.embedding, chunk_id, chunk.embedding, limit])
           results = cursor.fetchall()
       
       # Sonuçları formatla
       similar_chunks = []
       for row in results:
           similarity = float(row[6])
           if similarity >= min_similarity:
               similar_chunks.append({
                   'id': str(row[0]),
                   'content': row[1][:300] + '...',
                   'sap_module': row[2],
                   'technical_level': row[3],
                   'section_title': row[4],
                   'source_title': row[5],
                   'similarity_score': similarity
               })
       
       return similar_chunks
       
   except Exception as e:
       logger.error(f"Chunk similarity search error: {str(e)}")
       raise SearchError(f"Benzer chunk arama hatası: {str(e)}")


async def bulk_reindex_chunks(
   chunk_ids: Optional[List[str]] = None,
   sap_module: Optional[str] = None,
   batch_size: int = 100
) -> Dict[str, Any]:
   """Chunk'ları toplu olarak yeniden indexle"""
   try:
       # Chunk'ları filtrele
       queryset = KnowledgeChunk.objects.filter(is_active=True)
       
       if chunk_ids:
           queryset = queryset.filter(id__in=chunk_ids)
       
       if sap_module:
           queryset = queryset.filter(sap_module=sap_module)
       
       total_chunks = queryset.count()
       processed_chunks = 0
       failed_chunks = 0
       
       # Batch'ler halinde işle
       embedding_service = EmbeddingService()
       
       for i in range(0, total_chunks, batch_size):
           batch = queryset[i:i + batch_size]
           
           for chunk in batch:
               try:
                   # Yeni embedding oluştur
                   new_embedding = await asyncio.get_event_loop().run_in_executor(
                       None,
                       embedding_service.generate_embedding,
                       chunk.content
                   )
                   
                   # Güncelle
                   chunk.embedding = new_embedding
                   chunk.save(update_fields=['embedding'])
                   
                   processed_chunks += 1
                   
               except Exception as e:
                   logger.error(f"Chunk {chunk.id} reindex error: {str(e)}")
                   failed_chunks += 1
       
       return {
           'total_chunks': total_chunks,
           'processed_chunks': processed_chunks,
           'failed_chunks': failed_chunks,
           'success_rate': processed_chunks / total_chunks if total_chunks > 0 else 0
       }
       
   except Exception as e:
       logger.error(f"Bulk reindex error: {str(e)}")
       raise SearchError(f"Toplu reindex hatası: {str(e)}")


# Performance monitoring
class SearchPerformanceMonitor:
   """Arama performansı izleme"""
   
   @staticmethod
   def log_search_performance(
       query: str,
       search_time: float,
       result_count: int,
       search_type: str = 'semantic'
   ):
       """Arama performansını logla"""
       try:
           from ..models import PerformanceMetrics
           
           PerformanceMetrics.objects.create(
               component='search',
               metric_name=f'{search_type}_search_time',
               value=search_time,
               unit='seconds',
               metadata={
                   'query_length': len(query),
                   'result_count': result_count,
                   'search_type': search_type
               }
           )
           
       except Exception as e:
           logger.error(f"Performance logging error: {str(e)}")
   
   @staticmethod
   def get_performance_stats(days: int = 7) -> Dict[str, Any]:
       """Performans istatistikleri al"""
       try:
           from ..models import PerformanceMetrics
           from django.db.models import Avg, Count, Min, Max
           
           cutoff_date = timezone.now() - timedelta(days=days)
           
           search_metrics = PerformanceMetrics.objects.filter(
               component='search',
               timestamp__gte=cutoff_date
           ).aggregate(
               avg_response_time=Avg('value'),
               min_response_time=Min('value'),
               max_response_time=Max('value'),
               total_searches=Count('id')
           )
           
           return {
               'avg_response_time': search_metrics['avg_response_time'] or 0,
               'min_response_time': search_metrics['min_response_time'] or 0,
               'max_response_time': search_metrics['max_response_time'] or 0,
               'total_searches': search_metrics['total_searches'],
               'period_days': days
           }
           
       except Exception as e:
           logger.error(f"Performance stats error: {str(e)}")
           return {}


# Health check
async def search_service_health_check() -> Dict[str, Any]:
   """Search service sağlık kontrolü"""
   try:
       start_time = timezone.now()
       
       # Test arama yap
       test_query = "SAP test"
       test_results = await semantic_search_service.search(
           query=test_query,
           limit=1
       )
       
       response_time = (timezone.now() - start_time).total_seconds()
       
       # Database bağlantısı kontrolü
       chunk_count = KnowledgeChunk.objects.filter(is_active=True).count()
       
       # Embedding service kontrolü
       embedding_service = EmbeddingService()
       test_embedding = embedding_service.generate_embedding("test")
       
       return {
           'status': 'healthy',
           'response_time': response_time,
           'database_connection': True,
           'active_chunks': chunk_count,
           'embedding_service': len(test_embedding) > 0,
           'test_search_results': len(test_results.get('results', [])),
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as e:
       logger.error(f"Search service health check failed: {str(e)}")
       return {
           'status': 'unhealthy',
           'error': str(e),
           'timestamp': timezone.now().isoformat()
       }


