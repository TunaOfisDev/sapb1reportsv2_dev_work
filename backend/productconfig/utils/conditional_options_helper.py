# backend/productconfig/utils/conditional_options_helper.py
from typing import List, Dict, Optional, Tuple
from ..models import ConditionalOption, Question, Option

class ConditionalOptionsHelper:
    @staticmethod
    def get_applicable_options(
        user_selected_option_ids: List[int], 
        question_id: int,
        standard_options: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Kullanıcı seçimlerine göre uygun seçenekleri belirler."""
        target_question = Question.objects.get(id=question_id)
        
        # Koşullu seçenekleri al
        conditional_rules = ConditionalOption.objects.filter(
            trigger_option_1__id__in=user_selected_option_ids,
            trigger_option_2__id__in=user_selected_option_ids,
            target_question=target_question,
            is_active=True
        ).distinct()

        # Görüntüleme moduna göre seçenekleri belirle
        final_options = []
        has_override = False

        for rule in conditional_rules:
            options = rule.applicable_options.filter(is_active=True)
            
            # OVERRIDE modu varsa sadece o seçenekleri kullan
            if rule.display_mode == ConditionalOption.DisplayMode.OVERRIDE:
                has_override = True
                final_options.extend(
                    ConditionalOptionsHelper._serialize_option(opt) 
                    for opt in options
                )
                # İlk OVERRIDE kuralını uygula ve çık
                break
                
            # APPEND modu için seçenekleri biriktir    
            final_options.extend(
                ConditionalOptionsHelper._serialize_option(opt)
                for opt in options
            )

        # OVERRIDE yoksa ve standard seçenekler verildiyse birleştir
        if not has_override and standard_options:
            final_options = (
                ConditionalOptionsHelper.inject_conditional_options(
                    standard_options, 
                    final_options
                )
            )

        return final_options

    @staticmethod 
    def _serialize_option(option: Option) -> Dict:
        """Seçenek objesini serialize eder."""
        return {
            "id": option.id,
            "name": option.name,
            "option_type": option.option_type,
            "variant_code_part": option.variant_code_part,
            "variant_description_part": option.variant_description_part,
            "image_url": option.get_image_url,
            "applicable_brands": [
                b.id for b in option.applicable_brands.all()
            ],
            "applicable_groups": [
                g.id for g in option.applicable_groups.all()
            ],
            "applicable_categories": [
                c.id for c in option.applicable_categories.all()
            ],
            "applicable_product_models": [
                m.id for m in option.applicable_product_models.all()
            ]
        }

    @staticmethod
    def inject_conditional_options(
        existing_options: List[Dict],
        conditional_options: List[Dict]
    ) -> List[Dict]:
        """Mevcut seçenekleri koşullu seçeneklerle birleştirir."""
        existing_ids = {opt['id'] for opt in existing_options}
        
        for option in conditional_options:
            if option['id'] not in existing_ids:
                existing_options.append(option)
                
        return existing_options
