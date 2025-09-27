# backend/productconfig/utils/variant_helper.py
from decimal import Decimal
from django.db.models import Sum
from ..models import Variant, Question, Option
from .data_fetcher import fetch_hana_db_data
import logging

logger = logging.getLogger(__name__)

class VariantHelper:
    """
    Varyant işlemleri için yardımcı sınıf.
    """
    @staticmethod
    def calculate_total_price(variant: Variant) -> Decimal:
        """Seçeneklere göre toplam fiyatı hesaplar."""
        base_price = variant.product_model.base_price if variant.product_model else Decimal('0')
        options_price = variant.options.aggregate(total=Sum('price_modifier'))['total'] or Decimal('0')
        return base_price + options_price

    @staticmethod
    def format_variant_code(variant: Variant) -> str:
        code_parts = []
        answered_questions = Question.objects.filter(
            answered_variants=variant,
            id__in=[int(qid) for qid in variant.text_answers.keys()]
        ).order_by('variant_order', 'order')

        for question in answered_questions:
            answer = variant.text_answers.get(str(question.id))
            if answer:
                if 'answer_id' in answer:
                    # Tekli seçim
                    try:
                        option = Option.objects.get(id=answer['answer_id'])
                        if option.variant_code_part:
                            code_parts.append(option.variant_code_part.strip())
                    except Option.DoesNotExist:
                        pass
                elif 'answer_ids' in answer:
                    # Çoklu seçim
                    options = Option.objects.filter(id__in=answer['answer_ids'])
                    for option in options:
                        if option.variant_code_part:
                            code_parts.append(option.variant_code_part.strip())

        return '.'.join(filter(None, code_parts)) if code_parts else ''


    @staticmethod
    def update_variant_description(variant: Variant) -> str:
        desc_parts = []
        answered_questions = Question.objects.filter(
            answered_variants=variant,
            id__in=[int(qid) for qid in variant.text_answers.keys()]
        ).order_by('variant_order', 'order')

        for question in answered_questions:
            answer = variant.text_answers.get(str(question.id))
            if answer:
                if 'answer_id' in answer:
                    # Tekli seçim
                    try:
                        option = Option.objects.get(id=answer['answer_id'])
                        if option.variant_description_part:
                            desc_parts.append(option.variant_description_part.strip())
                    except Option.DoesNotExist:
                        pass
                elif 'answer_ids' in answer:
                    # Çoklu seçim
                    options = Option.objects.filter(id__in=answer['answer_ids'])
                    for option in options:
                        if option.variant_description_part:
                            desc_parts.append(option.variant_description_part.strip())

        return '-'.join(filter(None, desc_parts)) if desc_parts else ''




            
