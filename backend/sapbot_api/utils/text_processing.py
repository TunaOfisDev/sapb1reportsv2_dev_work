# backend/sapbot_api/utils/text_processing.py
"""
SAPBot API Text Processing Utilities

Bu modül metin işleme, dil tespiti, NLP ve SAP terminoloji
analizi fonksiyonlarını içerir.
"""

import re
import string
import unicodedata
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from collections import Counter, defaultdict
from dataclasses import dataclass
import logging

from django.conf import settings
from .helpers import clean_text, extract_keywords

logger = logging.getLogger(__name__)


@dataclass
class TextAnalysisResult:
    """Metin analiz sonucu"""
    language: str
    word_count: int
    char_count: int
    sentence_count: int
    paragraph_count: int
    sap_modules: List[str]
    technical_level: str
    intent: str
    confidence: float
    keywords: List[str]
    entities: List[Dict[str, Any]]


@dataclass
class ChunkResult:
    """Metin bölme sonucu"""
    text: str
    start_pos: int
    end_pos: int
    word_count: int
    char_count: int
    chunk_index: int
    section_title: Optional[str] = None
    page_number: Optional[int] = None


class LanguageDetector:
    """Dil tespit sınıfı - Türkçe/İngilizce odaklı"""
    
    TURKISH_CHARS = set('çğıöşüÇĞIİÖŞÜ')
    
    TURKISH_WORDS = {
        've', 'bir', 'bu', 'şu', 'o', 'için', 'ile', 'de', 'da', 'ki',
        'gibi', 'kadar', 'çok', 'az', 'en', 'daha', 'çünkü', 'ama',
        'fakat', 'ancak', 'ya', 'yada', 'veya', 'hem', 'ne', 'hiç',
        'her', 'bazı', 'kimi', 'hangi', 'nasıl', 'neden', 'nerede',
        'şimdi', 'sonra', 'önce', 'olan', 'olur', 'oldu', 'var', 'yok',
        'ise', 'eğer', 'tüm', 'bütün', 'kendi', 'böyle', 'şöyle',
        'işte', 'artık', 'hala', 'henüz', 'zaten', 'belki', 'mutlaka'
    }
    
    ENGLISH_WORDS = {
        'the', 'and', 'for', 'with', 'this', 'that', 'have', 'from',
        'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time',
        'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make',
        'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were',
        'what', 'your', 'work', 'life', 'only', 'can', 'will', 'about',
        'if', 'up', 'out', 'so', 'get', 'all', 'would', 'there'
    }
    
    @classmethod
    def detect_language(cls, text: str) -> Tuple[str, float]:
        """Dil tespiti - confidence skoru ile"""
        if not text or len(text.strip()) < 10:
            return 'tr', 0.5  # Varsayılan Türkçe
        
        text_lower = text.lower()
        words = re.findall(r'\b[a-zçğıöşüA-ZÇĞIİÖŞÜ]+\b', text_lower)
        
        if not words:
            return 'tr', 0.5
        
        turkish_score = 0
        english_score = 0
        total_chars = len(text)
        
        # Türkçe karakter analizi
        turkish_char_count = sum(1 for char in text if char in cls.TURKISH_CHARS)
        if turkish_char_count > 0:
            turkish_score += (turkish_char_count / total_chars) * 100
        
        # Kelime analizi
        word_count = len(words)
        for word in words:
            if word in cls.TURKISH_WORDS:
                turkish_score += 2
            elif word in cls.ENGLISH_WORDS:
                english_score += 2
        
        # Türkçe ek analizi
        turkish_suffixes = ['lar', 'ler', 'dan', 'den', 'ta', 'te', 'de', 'da']
        for word in words:
            for suffix in turkish_suffixes:
                if word.endswith(suffix):
                    turkish_score += 1
                    break
        
        # İngilizce pattern analizi
        english_patterns = [r'\b(ing)\b', r'\b(tion)\b', r'\b(the)\b']
        for pattern in english_patterns:
            matches = len(re.findall(pattern, text_lower))
            english_score += matches * 2
        
        # Normalize et
        total_score = turkish_score + english_score
        if total_score == 0:
            return 'tr', 0.5
        
        turkish_confidence = turkish_score / total_score
        english_confidence = english_score / total_score
        
        if turkish_confidence > english_confidence:
            return 'tr', turkish_confidence
        else:
            return 'en', english_confidence
    
    @classmethod
    def is_mixed_language(cls, text: str, threshold: float = 0.3) -> bool:
        """Karışık dil kontrolü"""
        lang, confidence = cls.detect_language(text)
        return confidence < threshold


class SAPTerminologyAnalyzer:
    """SAP terminoloji analizi"""
    
    SAP_MODULES = {
        'FI': {
            'turkish': [
                'mali', 'muhasebe', 'genel muhasebe', 'hesap planı', 'muhasebe kaydı',
                'borç', 'alacak', 'bilanço', 'gelir tablosu', 'mali rapor',
                'bütçe', 'maliyet merkezi', 'kar merkezi', 'finansal',
                'nakit akışı', 'ödeme', 'tahsilat', 'fatura', 'dekont'
            ],
            'english': [
                'financial', 'accounting', 'general ledger', 'chart of accounts',
                'journal entry', 'debit', 'credit', 'balance sheet', 'income statement',
                'financial report', 'budget', 'cost center', 'profit center',
                'cash flow', 'payment', 'receipt', 'invoice', 'document'
            ]
        },
        'MM': {
            'turkish': [
                'malzeme', 'stok', 'satın alma', 'tedarikçi', 'satıcı',
                'sipariş', 'teslim alma', 'depo', 'envanter', 'malzeme kartı',
                'tedarik', 'procurement', 'vendor', 'purchase order',
                'malzeme planlaması', 'stok yönetimi', 'depo yönetimi'
            ],
            'english': [
                'material', 'stock', 'purchasing', 'procurement', 'vendor',
                'supplier', 'purchase order', 'goods receipt', 'warehouse',
                'inventory', 'material master', 'stock management',
                'warehouse management', 'material planning'
            ]
        },
        'SD': {
            'turkish': [
                'satış', 'müşteri', 'teklif', 'sipariş', 'sevkiyat',
                'fatura', 'dağıtım', 'sales', 'customer', 'quotation',
                'sales order', 'delivery', 'billing', 'distribution',
                'fiyat listesi', 'iskonto', 'kampanya', 'müşteri kartı'
            ],
            'english': [
                'sales', 'customer', 'quotation', 'sales order', 'delivery',
                'billing', 'distribution', 'price list', 'discount',
                'campaign', 'customer master', 'shipping', 'invoice'
            ]
        },
        'CRM': {
            'turkish': [
                'müşteri ilişkileri', 'fırsat', 'lead', 'kampanya',
                'aktivite', 'randevu', 'görev', 'müşteri hizmetleri',
                'şikayet', 'talep', 'potansiyel müşteri', 'satış süreci'
            ],
            'english': [
                'customer relationship', 'opportunity', 'lead', 'campaign',
                'activity', 'appointment', 'task', 'customer service',
                'complaint', 'request', 'prospect', 'sales process'
            ]
        },
        'PROD': {
            'turkish': [
                'üretim', 'imalat', 'iş emri', 'reçete', 'rotasyon',
                'kapasite', 'planlama', 'üretim planı', 'work order',
                'bill of material', 'routing', 'capacity planning'
            ],
            'english': [
                'production', 'manufacturing', 'work order', 'bill of material',
                'routing', 'capacity', 'planning', 'production plan',
                'shop floor', 'work center', 'operation'
            ]
        },
        'HR': {
            'turkish': [
                'insan kaynakları', 'personel', 'çalışan', 'bordro',
                'maaş', 'izin', 'mesai', 'performans', 'eğitim',
                'işe alım', 'işten çıkarma', 'özlük dosyası'
            ],
            'english': [
                'human resources', 'personnel', 'employee', 'payroll',
                'salary', 'leave', 'overtime', 'performance', 'training',
                'recruitment', 'termination', 'personnel file'
            ]
        }
    }
    
    @classmethod
    def detect_sap_modules(cls, text: str) -> List[Tuple[str, float]]:
        """SAP modüllerini tespit et - confidence skoru ile"""
        if not text:
            return []
        
        text_lower = text.lower()
        module_scores = {}
        
        for module, terms in cls.SAP_MODULES.items():
            score = 0
            total_terms = len(terms['turkish']) + len(terms['english'])
            
            # Türkçe terimler
            for term in terms['turkish']:
                # Tam kelime eşleşmesi
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                score += matches * 2
                
                # Kısmi eşleşme
                if term in text_lower:
                    score += 0.5
            
            # İngilizce terimler
            for term in terms['english']:
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                score += matches * 2
                
                if term in text_lower:
                    score += 0.5
            
            if score > 0:
                # Normalize et
                confidence = min(score / total_terms, 1.0)
                module_scores[module] = confidence
        
        # Skorlara göre sırala
        sorted_modules = sorted(module_scores.items(), key=lambda x: x[1], reverse=True)
        return [(module, score) for module, score in sorted_modules if score > 0.1]
    
    @classmethod
    def get_primary_sap_module(cls, text: str) -> Optional[str]:
        """Ana SAP modülünü tespit et"""
        modules = cls.detect_sap_modules(text)
        return modules[0][0] if modules else None


class TechnicalLevelAnalyzer:
    """Teknik seviye analizi"""
    
    TECHNICAL_INDICATORS = {
        'user': {
            'turkish': [
                'nasıl', 'adım adım', 'basit', 'kolay', 'anlatım',
                'kullanım', 'giriş', 'başlangıç', 'temel', 'öğretici'
            ],
            'english': [
                'how to', 'step by step', 'simple', 'easy', 'basic',
                'beginner', 'introduction', 'guide', 'tutorial'
            ]
        },
        'admin': {
            'turkish': [
                'konfigürasyon', 'ayar', 'parametre', 'kurulum',
                'yetki', 'kullanıcı yönetimi', 'sistem', 'yönetici'
            ],
            'english': [
                'configuration', 'setup', 'parameter', 'installation',
                'permission', 'user management', 'system', 'admin'
            ]
        },
        'developer': {
            'turkish': [
                'kod', 'script', 'fonksiyon', 'api', 'entegrasyon',
                'veritabanı', 'sql', 'query', 'geliştirme', 'programlama'
            ],
            'english': [
                'code', 'script', 'function', 'api', 'integration',
                'database', 'sql', 'query', 'development', 'programming',
                'technical', 'implementation', 'customization'
            ]
        }
    }
    
    @classmethod
    def detect_technical_level(cls, text: str) -> Tuple[str, float]:
        """Teknik seviye tespiti"""
        if not text:
            return 'user', 0.5
        
        text_lower = text.lower()
        level_scores = {}
        
        for level, indicators in cls.TECHNICAL_INDICATORS.items():
            score = 0
            
            for term in indicators['turkish'] + indicators['english']:
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            if score > 0:
                level_scores[level] = score
        
        if not level_scores:
            return 'user', 0.5
        
        # En yüksek skora sahip seviye
        max_level = max(level_scores, key=level_scores.get)
        max_score = level_scores[max_level]
        total_score = sum(level_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        return max_level, confidence


class IntentClassifier:
    """Niyet sınıflandırıcı"""
    
    INTENT_PATTERNS = {
        'error_solving': {
            'turkish': [
                'hata', 'sorun', 'problem', 'çalışmıyor', 'bozuk',
                'düzgün', 'eksik', 'yanlış', 'çözüm', 'nasıl düzeltirim',
                'neden olmuyor', 'ne yapmalıyım'
            ],
            'english': [
                'error', 'problem', 'issue', 'not working', 'broken',
                'fix', 'solve', 'troubleshoot', 'debug', 'wrong'
            ]
        },
        'how_to': {
            'turkish': [
                'nasıl', 'ne şekilde', 'hangi adımlar', 'yapılır',
                'oluşturulur', 'kaydedilir', 'işlem', 'adım adım',
                'öğretici', 'kılavuz', 'rehber'
            ],
            'english': [
                'how to', 'how do I', 'steps', 'tutorial', 'guide',
                'instruction', 'procedure', 'process', 'method'
            ]
        },
        'configuration': {
            'turkish': [
                'ayar', 'ayarlama', 'konfigürasyon', 'yapılandırma',
                'parametre', 'değer', 'seçenek', 'kurulum', 'setup'
            ],
            'english': [
                'configuration', 'setup', 'setting', 'parameter',
                'option', 'configure', 'customize', 'installation'
            ]
        },
        'explanation': {
            'turkish': [
                'nedir', 'ne demek', 'açıkla', 'anlat', 'tanım',
                'kavram', 'ne işe yarar', 'amacı nedir', 'farkı nedir'
            ],
            'english': [
                'what is', 'explain', 'definition', 'meaning',
                'concept', 'purpose', 'difference', 'overview'
            ]
        },
        'reporting': {
            'turkish': [
                'rapor', 'raporlama', 'analiz', 'dashboard',
                'grafik', 'çıktı', 'export', 'excel', 'print'
            ],
            'english': [
                'report', 'reporting', 'analysis', 'dashboard',
                'chart', 'export', 'print', 'output', 'analytics'
            ]
        }
    }
    
    @classmethod
    def classify_intent(cls, text: str) -> Tuple[str, float]:
        """Niyet sınıflandırması"""
        if not text:
            return 'general', 0.5
        
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, patterns in cls.INTENT_PATTERNS.items():
            score = 0
            
            for term in patterns['turkish'] + patterns['english']:
                # Tam kelime eşleşmesi
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                score += matches * 2
                
                # Kısmi eşleşme
                if term in text_lower:
                    score += 0.5
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return 'general', 0.5
        
        # En yüksek skora sahip niyet
        max_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[max_intent]
        total_score = sum(intent_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        return max_intent, confidence


class EntityExtractor:
    """Varlık çıkarıcı - SAP terminolojisi için"""
    
    ENTITY_PATTERNS = {
        'sap_transaction': {
            'pattern': r'\b[A-Z]{2,4}[0-9]{1,3}[A-Z]?\b',
            'examples': ['FB01', 'VA01', 'VF01', 'ME21N']
        },
        'document_number': {
            'pattern': r'\b[0-9]{8,10}\b',
            'examples': ['4500000123', '1900000456']
        },
        'currency': {
            'pattern': r'\b(TRY|USD|EUR|GBP)\b',
            'examples': ['TRY', 'USD', 'EUR']
        },
        'amount': {
            'pattern': r'\b[0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?\s*(?:TL|₺|$|€|£)\b',
            'examples': ['1.000,50 TL', '500 ₺', '$1,000']
        },
        'date': {
            'pattern': r'\b(?:[0-3]?[0-9][\./-][0-1]?[0-9][\./-](?:20)?[0-9]{2})\b',
            'examples': ['31.12.2024', '01/01/2025', '15-03-24']
        }
    }
    
    @classmethod
    def extract_entities(cls, text: str) -> List[Dict[str, Any]]:
        """Varlık çıkarma"""
        entities = []
        
        for entity_type, config in cls.ENTITY_PATTERNS.items():
            pattern = config['pattern']
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                entities.append({
                    'type': entity_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8  # Basit regex için sabit değer
                })
        
        return entities


class TextChunker:
    """Gelişmiş metin bölme"""
    
    @classmethod
    def intelligent_split(
        cls,
        text: str,
        max_chunk_size: int = 1000,
        overlap: int = 200,
        preserve_sentences: bool = True,
        preserve_paragraphs: bool = True
    ) -> List[ChunkResult]:
        """Akıllı metin bölme"""
        if not text:
            return []
        
        chunks = []
        
        if preserve_paragraphs:
            # Paragraf bazlı bölme
            paragraphs = text.split('\n\n')
            current_chunk = ""
            current_pos = 0
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                    # Chunk'ı kaydet
                    chunk = cls._create_chunk_result(
                        current_chunk,
                        current_pos,
                        current_pos + len(current_chunk),
                        len(chunks)
                    )
                    chunks.append(chunk)
                    
                    # Overlap için son kısmı al
                    if overlap > 0:
                        overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                        current_chunk = overlap_text + "\n\n" + paragraph
                        current_pos = current_pos + len(current_chunk) - len(overlap_text) - len(paragraph) - 2
                    else:
                        current_chunk = paragraph
                        current_pos = current_pos + len(current_chunk)
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # Son chunk'ı ekle
            if current_chunk:
                chunk = cls._create_chunk_result(
                    current_chunk,
                    current_pos,
                    current_pos + len(current_chunk),
                    len(chunks)
                )
                chunks.append(chunk)
        
        elif preserve_sentences:
            # Cümle bazlı bölme
            sentences = re.split(r'[.!?]+', text)
            current_chunk = ""
            current_pos = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                    chunk = cls._create_chunk_result(
                        current_chunk,
                        current_pos,
                        current_pos + len(current_chunk),
                        len(chunks)
                    )
                    chunks.append(chunk)
                    
                    if overlap > 0:
                        overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                        current_chunk = overlap_text + ". " + sentence
                        current_pos = current_pos + len(current_chunk) - len(overlap_text) - len(sentence) - 2
                    else:
                        current_chunk = sentence
                        current_pos = current_pos + len(current_chunk)
                else:
                    if current_chunk:
                        current_chunk += ". " + sentence
                    else:
                        current_chunk = sentence
            
            if current_chunk:
                chunk = cls._create_chunk_result(
                    current_chunk,
                    current_pos,
                    current_pos + len(current_chunk),
                    len(chunks)
                )
                chunks.append(chunk)
        
        else:
            # Karakter bazlı bölme
            start = 0
            chunk_index = 0
            
            while start < len(text):
                end = min(start + max_chunk_size, len(text))
                
                # Kelime sınırında kes
                if end < len(text):
                    last_space = text.rfind(' ', start, end)
                    if last_space > start:
                        end = last_space
                
                chunk_text = text[start:end]
                chunk = cls._create_chunk_result(chunk_text, start, end, chunk_index)
                chunks.append(chunk)
                
                start = max(end - overlap, end)
                chunk_index += 1
        
        return chunks
    
    @classmethod
    def _create_chunk_result(
        cls,
        text: str,
        start_pos: int,
        end_pos: int,
        chunk_index: int
    ) -> ChunkResult:
        """ChunkResult objesi oluştur"""
        words = len(text.split())
        chars = len(text)
        
        return ChunkResult(
            text=text.strip(),
            start_pos=start_pos,
            end_pos=end_pos,
            word_count=words,
            char_count=chars,
            chunk_index=chunk_index
        )


class TextAnalyzer:
    """Kapsamlı metin analizi"""
    
    @classmethod
    def analyze_text(cls, text: str) -> TextAnalysisResult:
        """Kapsamlı metin analizi"""
        if not text:
            return TextAnalysisResult(
                language='tr',
                word_count=0,
                char_count=0,
                sentence_count=0,
                paragraph_count=0,
                sap_modules=[],
                technical_level='user',
                intent='general',
                confidence=0.0,
                keywords=[],
                entities=[]
            )
        
        # Temel istatistikler
        clean_text_content = clean_text(text)
        words = re.findall(r'\b\w+\b', clean_text_content)
        sentences = re.split(r'[.!?]+', clean_text_content)
        paragraphs = text.split('\n\n')
        
        # Dil tespiti
        language, lang_confidence = LanguageDetector.detect_language(text)
        
        # SAP modül tespiti
        sap_modules_detected = SAPTerminologyAnalyzer.detect_sap_modules(text)
        sap_modules = [module for module, _ in sap_modules_detected[:3]]  # Top 3
        
        # Teknik seviye tespiti
        technical_level, tech_confidence = TechnicalLevelAnalyzer.detect_technical_level(text)
        
        # Niyet sınıflandırması
        intent, intent_confidence = IntentClassifier.classify_intent(text)
        
        # Anahtar kelimeler
        keywords = extract_keywords(text, max_count=10)
        
        # Varlık çıkarma
        entities = EntityExtractor.extract_entities(text)
        
        # Genel confidence hesaplama
        overall_confidence = (lang_confidence + tech_confidence + intent_confidence) / 3
        
        return TextAnalysisResult(
            language=language,
            word_count=len(words),
            char_count=len(clean_text_content),
            sentence_count=len([s for s in sentences if s.strip()]),
            paragraph_count=len([p for p in paragraphs if p.strip()]),
            sap_modules=sap_modules,
            technical_level=technical_level,
            intent=intent,
            confidence=overall_confidence,
            keywords=keywords,
            entities=entities
        )


# Utility functions
def detect_language(text: str) -> str:
    """Dil tespiti"""
    lang, _ = LanguageDetector.detect_language(text)
    return lang


def split_text_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    preserve_paragraphs: bool = True
) -> List[Dict[str, Any]]:
    """Metin chunk'lara bölme"""
    chunks = TextChunker.intelligent_split(
        text, chunk_size, overlap, preserve_paragraphs=preserve_paragraphs
    )
    
    return [
        {
            'text': chunk.text,
            'start_pos': chunk.start_pos,
            'end_pos': chunk.end_pos,
            'word_count': chunk.word_count,
            'char_count': chunk.char_count,
            'chunk_index': chunk.chunk_index
        }
        for chunk in chunks
    ]


def extract_sap_module(text: str) -> Optional[str]:
    """Ana SAP modülünü çıkar"""
    return SAPTerminologyAnalyzer.get_primary_sap_module(text)


def normalize_text_for_search(text: str) -> str:
   """Arama için metin normalleştir"""
   if not text:
       return ""
   
   # Unicode normalleştir
   text = unicodedata.normalize('NFKD', text)
   
   # Küçük harfe çevir
   text = text.lower()
   
   # Türkçe karakterleri normalize et
   turkish_normalize = {
       'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'
   }
   
   for tr_char, en_char in turkish_normalize.items():
       text = text.replace(tr_char, en_char)
   
   # Noktalama işaretlerini kaldır
   text = text.translate(str.maketrans('', '', string.punctuation))
   
   # Fazla boşlukları temizle
   text = ' '.join(text.split())
   
   # Sayıları koruyarak özel karakterleri temizle
   text = re.sub(r'[^\w\s]', ' ', text)
   
   # Tekrar fazla boşlukları temizle
   text = ' '.join(text.split())
   
   return text.strip()


def extract_search_terms(text: str, min_length: int = 2) -> List[str]:
   """Metinden arama terimlerini çıkar"""
   if not text:
       return []
   
   # Metni normalize et
   normalized = normalize_text_for_search(text)
   
   # Kelimelere böl
   words = normalized.split()
   
   # Stop words - Türkçe ve İngilizce
   stop_words = {
       # Türkçe stop words
       've', 'bir', 'bu', 'şu', 'o', 'için', 'ile', 'de', 'da',
       'ki', 'gibi', 'kadar', 'çok', 'az', 'en', 'daha', 'çünkü',
       'ama', 'fakat', 'ancak', 'ya', 'yada', 'veya', 'hem', 'ne',
       'hiç', 'her', 'bazı', 'kimi', 'hangi', 'nasıl', 'neden',
       'nerede', 'ne zaman', 'kim', 'kime', 'kimin', 'olan', 'olur',
       'var', 'yok', 'ise', 'eğer', 'tüm', 'bütün', 'kendi', 'böyle',
       
       # İngilizce stop words
       'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
       'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
       'during', 'before', 'after', 'above', 'below', 'between',
       'among', 'until', 'while', 'since', 'without', 'under'
   }
   
   # Filtreleme
   search_terms = []
   for word in words:
       if (len(word) >= min_length and 
           word not in stop_words and
           not word.isdigit() and
           word.isalnum()):
           search_terms.append(word)
   
   return search_terms


def generate_search_variations(query: str) -> List[str]:
   """Arama sorgusu için varyasyonlar oluştur"""
   if not query:
       return []
   
   variations = [query]
   
   # Normalize edilmiş versiyon
   normalized = normalize_text_for_search(query)
   if normalized != query.lower():
       variations.append(normalized)
   
   # Türkçe karakter varyasyonları
   turkish_variations = query.lower()
   char_maps = [
       ('c', 'ç'), ('g', 'ğ'), ('i', 'ı'), ('o', 'ö'), ('s', 'ş'), ('u', 'ü'),
       ('ç', 'c'), ('ğ', 'g'), ('ı', 'i'), ('ö', 'o'), ('ş', 's'), ('ü', 'u')
   ]
   
   for old_char, new_char in char_maps:
       if old_char in turkish_variations:
           variation = turkish_variations.replace(old_char, new_char)
           if variation not in variations:
               variations.append(variation)
   
   # Kelime köklerini çıkar (basit Türkçe stemming)
   words = query.split()
   stemmed_words = []
   
   for word in words:
       stemmed = simple_turkish_stem(word.lower())
       if stemmed != word.lower():
           stemmed_words.append(stemmed)
   
   if stemmed_words:
       stemmed_query = ' '.join(stemmed_words)
       if stemmed_query not in variations:
           variations.append(stemmed_query)
   
   # Kısaltılmiş varyasyonlar
   if len(query) > 3:
       # İlk 3 karakter
       prefix = query[:3].lower()
       if prefix not in variations:
           variations.append(prefix)
   
   return list(set(variations))[:10]  # Maksimum 10 varyasyon


def simple_turkish_stem(word: str) -> str:
   """Basit Türkçe stemming"""
   if len(word) < 4:
       return word
   
   # Yaygın Türkçe ekler
   suffixes = [
       'lar', 'ler', 'dan', 'den', 'tan', 'ten', 'nin', 'nun', 'nın', 'nün',
       'da', 'de', 'ta', 'te', 'yi', 'yu', 'yı', 'yü', 'si', 'su', 'sı', 'sü',
       'im', 'in', 'iz', 'um', 'un', 'uz', 'ım', 'ın', 'ız', 'ün', 'üz',
       'dir', 'dur', 'dır', 'dür', 'tir', 'tur', 'tır', 'tür'
   ]
   
   word_lower = word.lower()
   
   for suffix in sorted(suffixes, key=len, reverse=True):
       if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
           return word_lower[:-len(suffix)]
   
   return word_lower


def calculate_text_similarity_score(text1: str, text2: str, method: str = 'jaccard') -> float:
   """Gelişmiş metin benzerlik hesaplama"""
   if not text1 or not text2:
       return 0.0
   
   # Metinleri normalize et
   norm_text1 = normalize_text_for_search(text1)
   norm_text2 = normalize_text_for_search(text2)
   
   if method == 'jaccard':
       # Jaccard similarity
       words1 = set(norm_text1.split())
       words2 = set(norm_text2.split())
       
       if not words1 or not words2:
           return 0.0
       
       intersection = len(words1.intersection(words2))
       union = len(words1.union(words2))
       
       return intersection / union if union > 0 else 0.0
       
   elif method == 'cosine':
       # Cosine similarity (basit versiyon)
       words1 = norm_text1.split()
       words2 = norm_text2.split()
       
       # Kelime frekansları
       from collections import Counter
       freq1 = Counter(words1)
       freq2 = Counter(words2)
       
       # Ortak kelimeler
       common_words = set(freq1.keys()).intersection(set(freq2.keys()))
       
       if not common_words:
           return 0.0
       
       # Dot product
       dot_product = sum(freq1[word] * freq2[word] for word in common_words)
       
       # Magnitudes
       magnitude1 = sum(freq ** 2 for freq in freq1.values()) ** 0.5
       magnitude2 = sum(freq ** 2 for freq in freq2.values()) ** 0.5
       
       if magnitude1 == 0 or magnitude2 == 0:
           return 0.0
       
       return dot_product / (magnitude1 * magnitude2)
       
   elif method == 'levenshtein':
       # Levenshtein distance (normalized)
       def levenshtein_distance(s1: str, s2: str) -> int:
           if len(s1) < len(s2):
               return levenshtein_distance(s2, s1)
           
           if len(s2) == 0:
               return len(s1)
           
           previous_row = list(range(len(s2) + 1))
           for i, c1 in enumerate(s1):
               current_row = [i + 1]
               for j, c2 in enumerate(s2):
                   insertions = previous_row[j + 1] + 1
                   deletions = current_row[j] + 1
                   substitutions = previous_row[j] + (c1 != c2)
                   current_row.append(min(insertions, deletions, substitutions))
               previous_row = current_row
           
           return previous_row[-1]
       
       distance = levenshtein_distance(norm_text1, norm_text2)
       max_len = max(len(norm_text1), len(norm_text2))
       
       return 1 - (distance / max_len) if max_len > 0 else 0.0
   
   else:
       # Default: jaccard
       return calculate_text_similarity_score(text1, text2, 'jaccard')


def extract_technical_terms(text: str) -> List[Dict[str, Any]]:
   """Teknik terimler çıkar"""
   if not text:
       return []
   
   technical_terms = []
   text_lower = text.lower()
   
   # SAP terminolojisi
   sap_terms = {
       'transaction_codes': r'\b[A-Z]{2,4}[0-9]{1,3}[A-Z]?\b',
       'table_names': r'\b[A-Z]{3,8}\b(?=\s*(table|tablo))',
       'field_names': r'\b[A-Z][A-Z0-9_]{2,15}\b',
       'document_numbers': r'\b[0-9]{8,12}\b',
       'company_codes': r'\b[A-Z0-9]{2,4}\b(?=\s*(company|şirket))',
   }
   
   for term_type, pattern in sap_terms.items():
       matches = re.finditer(pattern, text, re.IGNORECASE)
       for match in matches:
           technical_terms.append({
               'type': term_type,
               'term': match.group(),
               'start': match.start(),
               'end': match.end(),
               'confidence': 0.8
           })
   
   # Teknik kavramlar
   technical_concepts = [
       'api', 'sql', 'database', 'server', 'client', 'http', 'https',
       'json', 'xml', 'csv', 'pdf', 'url', 'gui', 'cli', 'sdk',
       'veritabanı', 'sunucu', 'istemci', 'veri tabanı', 'sistem',
       'uygulama', 'yazılım', 'donanım', 'ağ', 'network'
   ]
   
   for concept in technical_concepts:
       if concept in text_lower:
           start_idx = text_lower.find(concept)
           technical_terms.append({
               'type': 'technical_concept',
               'term': concept,
               'start': start_idx,
               'end': start_idx + len(concept),
               'confidence': 0.6
           })
   
   # Terimları pozisyona göre sırala
   technical_terms.sort(key=lambda x: x['start'])
   
   return technical_terms


def extract_numbers_and_dates(text: str) -> List[Dict[str, Any]]:
   """Sayılar ve tarihleri çıkar"""
   if not text:
       return []
   
   extracted = []
   
   # Tarih pattern'ları
   date_patterns = [
       (r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b', 'date'),
       (r'\b\d{4}[-./]\d{1,2}[-./]\d{1,2}\b', 'date_iso'),
       (r'\b\d{1,2}\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+\d{4}\b', 'date_turkish'),
       (r'\b\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b', 'date_english'),
   ]
   
   for pattern, date_type in date_patterns:
       matches = re.finditer(pattern, text, re.IGNORECASE)
       for match in matches:
           extracted.append({
               'type': date_type,
               'value': match.group(),
               'start': match.start(),
               'end': match.end(),
               'confidence': 0.9
           })
   
   # Para birimi
   currency_patterns = [
       (r'\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*(?:TL|₺|TRY)\b', 'currency_try'),
       (r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:\$|USD|Dollar)\b', 'currency_usd'),
       (r'\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*(?:€|EUR|Euro)\b', 'currency_eur'),
   ]
   
   for pattern, currency_type in currency_patterns:
       matches = re.finditer(pattern, text, re.IGNORECASE)
       for match in matches:
           extracted.append({
               'type': currency_type,
               'value': match.group(),
               'start': match.start(),
               'end': match.end(),
               'confidence': 0.95
           })
   
   # Yüzdeler
   percentage_pattern = r'\b\d{1,3}(?:[.,]\d{1,2})?\s*%\b'
   matches = re.finditer(percentage_pattern, text)
   for match in matches:
       extracted.append({
           'type': 'percentage',
           'value': match.group(),
           'start': match.start(),
           'end': match.end(),
           'confidence': 0.9
       })
   
   # Sayılar
   number_pattern = r'\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\b'
   matches = re.finditer(number_pattern, text)
   for match in matches:
       # Diğer pattern'larla çakışmıyorsa ekle
       start, end = match.span()
       overlaps = any(
           item['start'] <= start < item['end'] or start <= item['start'] < end
           for item in extracted
       )
       
       if not overlaps:
           extracted.append({
               'type': 'number',
               'value': match.group(),
               'start': start,
               'end': end,
               'confidence': 0.7
           })
   
   # Pozisyona göre sırala
   extracted.sort(key=lambda x: x['start'])
   
   return extracted


def clean_text_for_embedding(text: str) -> str:
   """Embedding için metin temizleme"""
   if not text:
       return ""
   
   # Temel temizlik
   text = clean_text(text)
   
   # Çok uzun metinleri kes (embedding modelleri için)
   max_length = 1000  # Çoğu embedding modeli için uygun
   if len(text) > max_length:
       # Cümle sınırlarında kes
       sentences = text.split('.')
       result = ""
       for sentence in sentences:
           if len(result + sentence) > max_length:
               break
           result += sentence + "."
       text = result.rstrip(".")
   
   # Gereksiz boşlukları temizle
   text = ' '.join(text.split())
   
   # Minimum uzunluk kontrolü
   if len(text) < 10:
       return ""
   
   return text


def extract_sap_context(text: str) -> Dict[str, Any]:
   """SAP konteksti çıkar"""
   if not text:
       return {}
   
   context = {
       'sap_modules': [],
       'transaction_codes': [],
       'business_processes': [],
       'technical_level': 'user',
       'language': 'tr',
       'intent': 'general'
   }
   
   # SAP modüllerini tespit et
   detected_modules = SAPTerminologyAnalyzer.detect_sap_modules(text)
   context['sap_modules'] = [module for module, _ in detected_modules]
   
   # Transaction code'ları bul
   tcode_pattern = r'\b[A-Z]{2,4}[0-9]{1,3}[A-Z]?\b'
   tcodes = re.findall(tcode_pattern, text, re.IGNORECASE)
   context['transaction_codes'] = list(set(tcodes))
   
   # İş süreçlerini tespit et
   business_processes = [
       'satış', 'satın alma', 'muhasebe', 'stok', 'üretim',
       'raporlama', 'fatura', 'ödeme', 'tahsilat', 'bütçe',
       'maliyet', 'planlama', 'analiz', 'kontrol'
   ]
   
   text_lower = text.lower()
   detected_processes = [
       process for process in business_processes 
       if process in text_lower
   ]
   context['business_processes'] = detected_processes
   
   # Teknik seviye tespiti
   technical_level, _ = TechnicalLevelAnalyzer.detect_technical_level(text)
   context['technical_level'] = technical_level
   
   # Dil tespiti
   language, _ = LanguageDetector.detect_language(text)
   context['language'] = language
   
   # Intent tespiti
   intent, _ = IntentClassifier.classify_intent(text)
   context['intent'] = intent
   
   return context


def segment_text_by_topic(text: str, min_segment_length: int = 100) -> List[Dict[str, Any]]:
   """Metni konulara göre segmentlere böl"""
   if not text or len(text) < min_segment_length:
       return []
   
   segments = []
   
   # Paragraf bazlı bölme
   paragraphs = text.split('\n\n')
   
   for i, paragraph in enumerate(paragraphs):
       paragraph = paragraph.strip()
       if len(paragraph) < min_segment_length:
           continue
       
       # SAP konteksti çıkar
       sap_context = extract_sap_context(paragraph)
       
       # Teknik terimler
       tech_terms = extract_technical_terms(paragraph)
       
       # Anahtar kelimeler
       keywords = extract_keywords(paragraph, max_count=5)
       
       segment = {
           'index': i,
           'text': paragraph,
           'length': len(paragraph),
           'word_count': len(paragraph.split()),
           'sap_context': sap_context,
           'technical_terms': tech_terms,
           'keywords': keywords,
           'topic_score': len(keywords) + len(tech_terms)
       }
       
       segments.append(segment)
   
   # Benzer konuları birleştir
   merged_segments = []
   current_segment = None
   
   for segment in segments:
       if current_segment is None:
           current_segment = segment
       else:
           # Benzerlik kontrolü
           similarity = calculate_text_similarity_score(
               ' '.join(current_segment['keywords']),
               ' '.join(segment['keywords'])
           )
           
           # SAP modül benzerliği
           current_modules = set(current_segment['sap_context']['sap_modules'])
           segment_modules = set(segment['sap_context']['sap_modules'])
           module_similarity = len(current_modules.intersection(segment_modules)) / len(current_modules.union(segment_modules)) if current_modules.union(segment_modules) else 0
           
           # Birleştirme kararı
           if similarity > 0.3 or module_similarity > 0.5:
               # Segmentleri birleştir
               current_segment['text'] += '\n\n' + segment['text']
               current_segment['length'] += segment['length']
               current_segment['word_count'] += segment['word_count']
               current_segment['keywords'] = list(set(current_segment['keywords'] + segment['keywords']))
               current_segment['technical_terms'].extend(segment['technical_terms'])
               current_segment['topic_score'] += segment['topic_score']
           else:
               # Mevcut segmenti kaydet ve yenisini başlat
               merged_segments.append(current_segment)
               current_segment = segment
   
   if current_segment:
       merged_segments.append(current_segment)
   
   return merged_segments


def generate_text_summary(text: str, max_sentences: int = 3) -> str:
   """Basit metin özetleme"""
   if not text:
       return ""
   
   # Cümlelere böl
   sentences = re.split(r'[.!?]+', text)
   sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
   
   if len(sentences) <= max_sentences:
       return '. '.join(sentences) + '.'
   
   # Cümle skorlama
   sentence_scores = []
   
   # Tüm kelimeler
   all_words = extract_search_terms(' '.join(sentences))
   word_freq = Counter(all_words)
   
   for sentence in sentences:
       words = extract_search_terms(sentence)
       score = 0
       
       # Kelime frekansı skoru
       for word in words:
           score += word_freq.get(word, 0)
       
       # Cümle uzunluğu bonusu
       if 10 <= len(words) <= 25:
           score += 5
       
       # SAP terimleri bonusu
       sap_terms = ['sap', 'erp', 'business', 'one', 'hana']
       for term in sap_terms:
           if term in sentence.lower():
               score += 3
       
       # İlk ve son cümle bonusu
       if sentence == sentences[0] or sentence == sentences[-1]:
           score += 2
       
       sentence_scores.append((sentence, score))
   
   # En yüksek skorlu cümleleri seç
   sentence_scores.sort(key=lambda x: x[1], reverse=True)
   top_sentences = sentence_scores[:max_sentences]
   
   # Orijinal sıraya göre düzenle
   top_sentences.sort(key=lambda x: sentences.index(x[0]))
   
   summary = '. '.join([s[0] for s in top_sentences])
   return summary + '.' if not summary.endswith('.') else summary


# Utility functions for external use
def preprocess_query_for_search(query: str) -> Dict[str, Any]:
   """Arama sorgusu ön işleme"""
   return {
       'original': query,
       'normalized': normalize_text_for_search(query),
       'terms': extract_search_terms(query),
       'variations': generate_search_variations(query),
       'sap_context': extract_sap_context(query),
       'technical_terms': extract_technical_terms(query),
       'numbers_dates': extract_numbers_and_dates(query)
   }


def calculate_content_relevance(query: str, content: str) -> float:
   """İçerik relevans skoru hesapla"""
   if not query or not content:
       return 0.0
   
   # Temel benzerlik
   similarity = calculate_text_similarity_score(query, content, 'jaccard')
   
   # SAP modül uyumu
   query_context = extract_sap_context(query)
   content_context = extract_sap_context(content)
   
   query_modules = set(query_context.get('sap_modules', []))
   content_modules = set(content_context.get('sap_modules', []))
   
   if query_modules and content_modules:
       module_match = len(query_modules.intersection(content_modules)) / len(query_modules.union(content_modules))
       similarity += module_match * 0.3
   
   # Intent uyumu
   if query_context.get('intent') == content_context.get('intent'):
       similarity += 0.1
   
   # Teknik seviye uyumu
   if query_context.get('technical_level') == content_context.get('technical_level'):
       similarity += 0.1
   
   return min(similarity, 1.0)