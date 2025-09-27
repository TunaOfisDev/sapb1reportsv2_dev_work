# backend/productconfig/services/option_service.py
from decimal import Decimal
from typing import Dict
from ..models import Option
from ..dto.question_context import QuestionContext
from ..utils.option_helper import OptionHelper
from django.db.models import Q
import logging

logger = logging.getLogger('productconfig')

class OptionService:
    """
    Seçeneklerin filtrelenmesi ve belirli kriterlere göre getirilmesi işlemlerini yönetir.
    """
    def __init__(self):
        self.helper = OptionHelper()

    def get_material_price(self, option: Option, selected_option_ids: set) -> Decimal:
        """
        Seçenek için malzeme bazlı fiyatı hesaplar.
        """
        try:
            return self.helper.calculate_material_price(option, selected_option_ids)
        except Exception as e:
            logger.error(f"Malzeme fiyatı hesaplama hatası - Option ID {option.id}: {str(e)}")
            return Decimal('0')
        
    def update_option_prices(self, option: Option, variant) -> bool:
        """
        Seçenek fiyatlarını varyanta göre günceller.
        """
        try:
            selected_option_ids = set()
            for answer in variant.text_answers.values():
                if 'answer_id' in answer:
                    selected_option_ids.add(answer['answer_id'])
                elif 'answer_ids' in answer:
                    selected_option_ids.update(answer['answer_ids'])

            option.price_modifier = self.helper.calculate_material_price(option, selected_option_ids)
            option.save()
            return True
        except Exception as e:
            logger.error(f"Seçenek fiyat güncelleme hatası - Option ID {option.id}: {str(e)}")
            return False

    def get_active_material_prices(self, options, variant) -> Dict[int, Decimal]:
        """
        Seçenekler listesi için aktif malzeme fiyatlarını hesaplar.
        """
        try:
            return {
                option.id: self.helper.get_active_material_price(option, variant)
                for option in options
            }
        except Exception as e:
            logger.error(f"Aktif malzeme fiyatları hesaplama hatası: {str(e)}")
            return {}



    def filter_options_for_question(self, question, applicable_brands=None, applicable_groups=None, 
                                applicable_categories=None, applicable_product_models=None):
        """Soruya göre seçenekleri filtreler"""
        
        options = self.helper.get_base_options(question)
        
        # Soru tipine göre filtreleme
        options = self.helper.filter_by_question_type(
            options, 
            question.category_type
        )

        # Bağlam bazlı filtreleme
        options = self.helper.apply_context_filters(
            options,
            applicable_brands=applicable_brands,
            applicable_groups=applicable_groups, 
            applicable_categories=applicable_categories,
            applicable_product_models=applicable_product_models
        )

        return options.distinct().order_by('name')

    def get_filtered_options(self, question, variant=None, context=None):
        """
        Soru ve varyantta göre seçenekleri filtreler.
        Hem variant hem de context bilgilerini kullanır.
        """
        options = Option.objects.filter(
            question_option_relations__question=question,
            is_active=True
        )

        if variant:
            if variant.brand:
                options = options.filter(
                    Q(applicable_brands=variant.brand) |
                    Q(applicable_brands__isnull=True)
                )
            
            if variant.category:
                options = options.filter(
                    Q(applicable_categories=variant.category) |
                    Q(applicable_categories__isnull=True)
                )
            
            if variant.product_model:
                options = options.filter(
                    Q(applicable_product_models=variant.product_model) |
                    Q(applicable_product_models__isnull=True)
                )

        if context and context.has_filters:
            if context.applicable_brands:
                options = options.filter(
                    Q(applicable_brands__id__in=context.applicable_brands) |
                    Q(applicable_brands__isnull=True)
                )
            
            if context.applicable_categories:
                options = options.filter(
                    Q(applicable_categories__id__in=context.applicable_categories) |
                    Q(applicable_categories__isnull=True)
                )
            
            if context.applicable_product_models:
                options = options.filter(
                    Q(applicable_product_models__id__in=context.applicable_product_models) |
                    Q(applicable_product_models__isnull=True)
                )

        return options.distinct().order_by('name')

    def validate_option_applicability(self, option, variant):
        """
        Seçeneğin varyant için uygun olup olmadığını kontrol eder.
        TÜM applicable_* alanlarında eşleşme olmalıdır.
        """
        # Brand kontrolü
        if option.applicable_brands.exists():
            if not variant.brand or variant.brand not in option.applicable_brands.all():
                return False

        # Category kontrolü
        if option.applicable_categories.exists():
            if not variant.category or variant.category not in option.applicable_categories.all():
                return False

        # Product Model kontrolü
        if option.applicable_product_models.exists():
            if not variant.product_model or variant.product_model not in option.applicable_product_models.all():
                return False

        return True
    

    def _is_option_applicable(self, option: Option, context: QuestionContext) -> bool:
        """
        Seçeneğin context'e uygun olup olmadığını kontrol eder.
        TÜM applicable_* alanlarında eşleşme olmalıdır.
        """
        if context.applicable_brands and option.applicable_brands.exists():
            brand_match = False
            for brand_id in option.applicable_brands.values_list('id', flat=True):
                if brand_id in context.applicable_brands:
                    brand_match = True
                    break
            if not brand_match:
                return False

        if context.applicable_categories and option.applicable_categories.exists():
            category_match = False
            for category_id in option.applicable_categories.values_list('id', flat=True):
                if category_id in context.applicable_categories:
                    category_match = True
                    break
            if not category_match:
                return False

        if context.applicable_product_models and option.applicable_product_models.exists():
            model_match = False
            for model_id in option.applicable_product_models.values_list('id', flat=True):
                if model_id in context.applicable_product_models:
                    model_match = True
                    break
            if not model_match:
                return False

        return True
    
    def get_options_by_product_models(self, question, product_model_ids):
        """
        ProductModel ID'lerine göre seçenekleri filtreler
        """
        if not product_model_ids:
            return Option.objects.none()

        # Temel sorgu    
        options = self.helper.get_base_options(question)

        # Soru tipine göre seçenek tiplerini filtrele
        if question.category_type == 'productmodel_question':
            options = self.helper.filter_by_question_type(
                options,
                question.category_type
            )
            
        # ProductModel filtresini uygula
        options = self.helper.filter_by_product_models(options, product_model_ids)

        return options.distinct().order_by('name')
    
    def filter_options_by_chain(self, question, brand=None, group=None, category=None, models=None):
        """
        Markalar, gruplar, kategoriler ve modeller zincirine göre seçenekleri filtreler.
        """
        queryset = Option.objects.filter(question=question, is_active=True)

        if brand:
            queryset = queryset.filter(applicable_brands=brand)
        if group:
            queryset = queryset.filter(applicable_groups=group)
        if category:
            queryset = queryset.filter(applicable_categories=category)
        if models:
            queryset = queryset.filter(applicable_product_models__in=models)

        return queryset.distinct()
