# backend/productconfig/dto/rule_context.py
from typing import Set, Dict, Optional
import logging

logger = logging.getLogger(__name__)
# .env dosyasından ENABLE_LOGGING değişkenini kontrol et
import os
if not os.getenv('ENABLE_LOGGING', 'True').lower() == 'true':
    logger.setLevel(logging.CRITICAL)  # Loglamayı sadece CRITICAL seviyesine indir

class RuleContext:
    """
    Bağımlı kural değerlendirmelerinin durumunu tutan DTO sınıfı.
    Hidden/visible soru ID'lerini ve kural değerlendirme sonuçlarını önbellekte tutar.
    """
    def __init__(self):
        # Soru görünürlükleri için setler
        self.hidden_questions: Set[int] = set()
        self.visible_questions: Set[int] = set()
        
        # Kural değerlendirme önbelleği 
        self.rule_cache: Dict[str, bool] = {}
        
        # Geçici durum bilgileri
        self.current_evaluation: Dict = {
            'rule_id': None,
            'variant_id': None,
            'status': None
        }

    def add_hidden_question(self, question_id: int) -> None:
        """Soruyu gizli olarak işaretler"""
        logger.debug(f"Soru gizlendi: {question_id}")
        self.hidden_questions.add(question_id)
        self.visible_questions.discard(question_id)

    def add_visible_question(self, question_id: int) -> None:
        """Soruyu görünür olarak işaretler"""
        logger.debug(f"Soru görünür yapıldı: {question_id}")
        self.visible_questions.add(question_id)
        self.hidden_questions.discard(question_id)

    def is_question_visible(self, question_id: int) -> bool:
        """Sorunun görünür olup olmadığını kontrol eder"""
        return (
            question_id in self.visible_questions and 
            question_id not in self.hidden_questions
        )

    def cache_rule_result(self, rule_id: int, variant_id: int, result: bool) -> None:
        """Kural değerlendirme sonucunu önbelleğe alır"""
        cache_key = self._get_cache_key(rule_id, variant_id)
        self.rule_cache[cache_key] = result
        logger.debug(f"Kural sonucu önbelleğe alındı: {cache_key} = {result}")

    def get_cached_result(self, rule_id: int, variant_id: int) -> Optional[bool]:
        """Önbellekteki kural değerlendirme sonucunu getirir"""
        cache_key = self._get_cache_key(rule_id, variant_id)
        result = self.rule_cache.get(cache_key)
        logger.debug(f"Önbellekten kural sonucu alındı: {cache_key} = {result}")
        return result

    def clear_cache(self) -> None:
        """Önbelleği temizler"""
        self.rule_cache.clear()
        logger.debug("Kural önbelleği temizlendi")

    def reset(self) -> None:
        """Tüm context durumunu sıfırlar"""
        self.hidden_questions.clear()
        self.visible_questions.clear()
        self.clear_cache()
        self.current_evaluation = {
            'rule_id': None,
            'variant_id': None,
            'status': None
        }
        logger.debug("RuleContext sıfırlandı")

    def start_evaluation(self, rule_id: int, variant_id: int) -> None:
        """Yeni bir kural değerlendirmesi başlatır"""
        self.current_evaluation.update({
            'rule_id': rule_id,
            'variant_id': variant_id,
            'status': 'evaluating'
        })
        logger.debug(f"Kural değerlendirmesi başladı: Kural {rule_id}, Varyant {variant_id}")

    def end_evaluation(self, status: str = 'completed') -> None:
        """Mevcut kural değerlendirmesini sonlandırır"""
        self.current_evaluation['status'] = status
        logger.debug(f"Kural değerlendirmesi tamamlandı: {self.current_evaluation}")

    def get_evaluation_status(self) -> Dict:
        """Mevcut değerlendirme durumunu döndürür"""
        return self.current_evaluation.copy()

    def _get_cache_key(self, rule_id: int, variant_id: int) -> str:
        """Önbellek anahtarı oluşturur"""
        return f"rule_{rule_id}_variant_{variant_id}"

    @property
    def has_active_evaluation(self) -> bool:
        """Aktif bir değerlendirme olup olmadığını kontrol eder"""
        return self.current_evaluation['status'] == 'evaluating'