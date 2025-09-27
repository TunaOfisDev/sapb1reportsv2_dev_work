# backend/productconfig/utils/option_helper.py
from ..models import Option, Variant
from decimal import Decimal
import logging

logger = logging.getLogger('productconfig')


class OptionHelper:
    """
    Option modeline yönelik özel işlemleri sağlayan yardımcı sınıf.
    """
    def calculate_material_price(self, option: Option, selected_option_ids: set) -> Decimal:
        """
        Seçilen malzemeye göre fiyat hesaplar.
        
        Args:
            option: Fiyatı hesaplanacak seçenek
            selected_option_ids: Seçili olan tüm seçenek ID'leri
            
        Returns:
            Decimal: Hesaplanan fiyat
        """
        try:
            # Tetikleyicilere göre fiyat seçimi
            if any(trigger.id in selected_option_ids for trigger in option.melamine_triggers.all()):
                return option.price_melamine
            elif any(trigger.id in selected_option_ids for trigger in option.laminate_triggers.all()):
                return option.price_laminate
            elif any(trigger.id in selected_option_ids for trigger in option.veneer_triggers.all()):
                return option.price_veneer
            elif any(trigger.id in selected_option_ids for trigger in option.lacquer_triggers.all()):
                return option.price_lacquer
            else:
                return option.normal_price

        except Exception as e:
            logger.error(f"Malzeme fiyatı hesaplama hatası - Option ID {option.id}: {str(e)}")
            return Decimal('0')


    def filter_options_for_question(self, question, applicable_brands=None, applicable_groups=None, applicable_categories=None, applicable_product_models=None):
        """
        Soruya ve applicable_* listelerine göre seçenekleri filtreler.
        """

        # Soru tipi `master_question` ise `master_question_options` seçenekleri getir
        if question.category_type == 'master_question':
            option_types = ['master_question_options', 'conditional_question_options']
        # Soru tipi `productmodel_question` ise `model_question_options` seçenekleri getir
        elif question.category_type == 'productmodel_question':
            option_types = ['model_question_options', 'conditional_question_options']
        else:
            option_types = ['conditional_question_options']  # Koşullu sorular için sadece koşullu seçenekler

        filter_conditions = {
            'question_option_relations__question': question,
            'is_active': True,
            'option_type__in': option_types
        }

        if applicable_brands:
            filter_conditions['applicable_brands__id__in'] = applicable_brands
        if applicable_groups:
            filter_conditions['applicable_groups__id__in'] = applicable_groups
        if applicable_categories:
            filter_conditions['applicable_categories__id__in'] = applicable_categories
        if applicable_product_models:
            filter_conditions['applicable_product_models__id__in'] = applicable_product_models

        return Option.objects.filter(**filter_conditions).distinct().order_by('name')


    def filter_options_by_model(self, model):
        """
        Seçilen modele göre model seçenekleri filtreler.
        """
        return Option.objects.filter(
            option_type='model_question_options',
            applicable_product_models=model
        ).order_by('name')

    def calculate_price_effect(self, base_price: Decimal, options, selected_option_ids=None):
        """
        Seçeneklerin fiyat etkisine göre toplam fiyatı hesaplar.
        
        Args:
            base_price: Temel fiyat
            options: Seçenekler listesi
            selected_option_ids: Seçili seçenek ID'leri (malzeme fiyatı için)
        """
        selected_ids = set(selected_option_ids) if selected_option_ids else set()
        total_price = base_price

        for opt in options:
            if selected_ids:
                price = self.calculate_material_price(opt, selected_ids)
            else:
                price = opt.price_modifier
            total_price += price

        return total_price

    def filter_conditional_options(self, question, variant):
        """
        Belirli bir soruya göre koşullu seçenekleri filtreler.
        """
        if not isinstance(variant, Variant):
            raise TypeError("Expected a Variant instance for 'variant' parameter.")
        
        return Option.objects.filter(
            question_option_relations__question=question,
            applicable_brands=variant.brand,
            applicable_categories=variant.category,
            applicable_product_models=variant.product_model,
            option_type='conditional_question_options'
        ).order_by('name')


    def get_base_options(self, question):
        """Soru için temel seçenek sorgusunu oluşturur"""
        return Option.objects.filter(
            question_option_relations__question=question,
            is_active=True
        )

    def filter_by_question_type(self, options, category_type):
        """Soru tipine göre seçenekleri filtreler"""
        if category_type == 'master_question':
            return options.filter(
                option_type__in=['master_question_options', 'conditional_question_options']
            )
        elif category_type == 'productmodel_question':
            return options.filter(
                option_type__in=['model_question_options', 'conditional_question_options']
            )
        return options.filter(option_type='conditional_question_options')

    def apply_context_filters(self, options, **filters):
        """Context filtrelerini uygular"""
        if filters.get('applicable_brands'):
            options = options.filter(
                applicable_brands__id__in=filters['applicable_brands']
            )
        
        if filters.get('applicable_groups'):
            options = options.filter(
                applicable_groups__id__in=filters['applicable_groups']
            )
        
        if filters.get('applicable_categories'):
            options = options.filter(
                applicable_categories__id__in=filters['applicable_categories']
            )
        
        if filters.get('applicable_product_models'):
            options = options.filter(
                applicable_product_models__id__in=filters['applicable_product_models']
            )
        
        return options
    
    def filter_by_product_models(self, options, product_model_ids):
        """ProductModel ID'lerine göre seçenekleri filtreler"""
        if not product_model_ids:
            return options.none()
            
        return options.filter(
            applicable_product_models__id__in=product_model_ids,
            is_active=True
        ).distinct()
    
    
    def get_active_material_price(self, option: Option, variant: Variant) -> Decimal:
        """
        Varyant için aktif malzeme fiyatını hesaplar.
        
        Args:
            option: Fiyatı hesaplanacak seçenek
            variant: Varyant
            
        Returns:
            Decimal: Aktif malzeme fiyatı
        """
        try:
            selected_option_ids = set()
            for answer in variant.text_answers.values():
                if 'answer_id' in answer:
                    selected_option_ids.add(answer['answer_id'])
                elif 'answer_ids' in answer:
                    selected_option_ids.update(answer['answer_ids'])

            return self.calculate_material_price(option, selected_option_ids)

        except Exception as e:
            logger.error(f"Aktif malzeme fiyatı hesaplama hatası: {str(e)}")
            return Decimal('0')