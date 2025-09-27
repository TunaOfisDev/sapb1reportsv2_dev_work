# backend\productconfig\utils\old_component_code_helper.py
from typing import List, Dict
from django.db.models import QuerySet
from ..models import OldComponentCode, Variant
import logging

logger = logging.getLogger(__name__)

class OldComponentCodeHelper:
    """
    Eski bileşen kodlarının oluşturulması ve yönetilmesi için yardımcı sınıf.
    """

    def __init__(self):
        self.cache = {}  # Performans için önbellekleme

    def find_matching_rules(self, variant: Variant) -> List[OldComponentCode]:
        """
        Variant'a uygun kuralları bulur.

        Args:
            variant: Variant nesnesi

        Returns:
            List[OldComponentCode]: Eşleşen kurallar listesi
        """
        matching_rules = []
        try:
            all_rules = OldComponentCode.objects.filter(is_active=True)
            for rule in all_rules:
                if self._validate_rule(rule, variant.text_answers):
                    matching_rules.append(rule)

            logger.debug(f"Eşleşen kurallar bulundu: {len(matching_rules)} adet")
            return matching_rules
        except Exception as e:
            logger.error(f"Kural eşleştirme hatası: {str(e)}")
            return []

    def _validate_rule(self, rule: OldComponentCode, answers: Dict) -> bool:
        """
        Bir kuralın verilen cevaplarla geçerli olup olmadığını kontrol eder.

        Args:
            rule: OldComponentCode kuralı
            answers: Variant cevapları

        Returns:
            bool: Kural geçerli mi?
        """
        try:
            for q_num in range(1, 4):
                question = getattr(rule, f'question_{q_num}')
                expected_options = getattr(rule, f'expected_options_{q_num}').all()
                answer = answers.get(str(question.id))

                if not answer:
                    return False

                if 'answer_id' in answer and not any(
                    opt.id == answer['answer_id'] for opt in expected_options
                ):
                    return False

                if 'answer_ids' in answer and not set(answer['answer_ids']).intersection(
                    [opt.id for opt in expected_options]
                ):
                    return False

            return True
        except Exception as e:
            logger.error(f"Kural doğrulama hatası: {str(e)}")
            return False    
    
    def generate_codes_for_variant(self, variant: Variant) -> Dict:
        """
        Variant için eski bileşen kodlarını oluşturur.

        Args:
            variant: Variant nesnesi

        Returns:
            Dict: Oluşturulan eski bileşen kodları
        """
        try:
            rules = self.find_matching_rules(variant)
            if not rules:
                return {"status": "failure", "message": "Eşleşen kural bulunamadı."}

            generated_codes = []
            for rule in rules:
                result = rule.generate_code(variant.text_answers)
                if result and 'codes' in result:
                    generated_codes.extend(result['codes'])

            if not generated_codes:
                return {"status": "failure", "message": "Kod oluşturulamadı."}

            logger.info(f"Eski bileşen kodları oluşturuldu: {generated_codes}")
            return {"status": "success", "codes": generated_codes}
        except Exception as e:
            logger.error(f"Eski bileşen kod oluşturma hatası: {str(e)}")
            return {"status": "failure", "message": str(e)}

    def get_old_component_codes(self, variant: Variant) -> List[Dict]:
        """
        Variant için tüm eski bileşen kodlarını oluşturur ve detaylarını döndürür.
        
        Args:
            variant: Variant nesnesi
            
        Returns:
            List[Dict]: Her kod için detaylı bilgi
        """
        try:
            results = []
            code_rules = self._get_active_code_rules()

            for rule in code_rules:
                rule_result = rule.generate_code(variant.text_answers)
                if rule_result:
                    results.append({
                        'rule_name': rule.name,
                        'codes': rule_result['codes'],
                        'sequence_numbers': rule_result['sequence_numbers'],
                        'number_of_codes': rule_result['number_of_codes'],
                        'code_format': rule_result['code_format']
                    })

            logger.info(f"Eski bileşen kodları oluşturuldu - Variant ID: {variant.id}, Kodlar: {results}")
            return results

        except Exception as e:
            logger.error(f"Kod oluşturma hatası - Variant ID: {variant.id}: {str(e)}")
            return []

    def prepare_for_rest_api(self, variant: Variant) -> Dict:
        """
        API için eski bileşen kodlarını hazırlar.
        
        Args:
            variant: Variant nesnesi
            
        Returns:
            Dict: API için meta ve kod bilgileri
        """
        try:
            old_codes = self.get_old_component_codes(variant)

            meta = {
                'variant_id': variant.id,
                'total_rules': len(old_codes),
                'code_formats': [rule['code_format'] for rule in old_codes]
            }

            details = [
                {
                    'rule_name': rule['rule_name'],
                    'codes': rule['codes'],
                    'number_of_codes': rule['number_of_codes'],
                    'sequence_numbers': rule['sequence_numbers']
                }
                for rule in old_codes
            ]

            return {
                'meta': meta,
                'details': details
            }

        except Exception as e:
            logger.error(f"API hazırlık hatası: {str(e)}")
            return {'error': str(e)}

    def get_component_details(self, variant: Variant) -> List[Dict]:
        """
        Variant için eski bileşen kodlarının detaylarını döndürür.
        
        Args:
            variant: Variant nesnesi
            
        Returns:
            List[Dict]: Kod detayları
        """
        try:
            old_codes = self.get_old_component_codes(variant)
            return [
                {
                    'rule_name': rule['rule_name'],
                    'codes': rule['codes'],
                    'sequence_numbers': rule['sequence_numbers'],
                    'number_of_codes': rule['number_of_codes'],
                    'code_format': rule['code_format']
                }
                for rule in old_codes
            ]

        except Exception as e:
            logger.error(f"Bileşen detayları hatası: {str(e)}")
            return []

    def _get_active_code_rules(self) -> QuerySet[OldComponentCode]:
        """
        Aktif eski bileşen kodu kurallarını getirir.
        """
        cache_key = "active_rules"
        if cache_key not in self.cache:
            self.cache[cache_key] = OldComponentCode.objects.filter(
                is_active=True
            ).select_related(
                'question_1', 'question_2', 'question_3'
            ).prefetch_related(
                'expected_options_1', 'expected_options_2', 'expected_options_3'
            )
        return self.cache[cache_key]

    def clear_cache(self):
        """Önbelleği temizler"""
        self.cache.clear()
