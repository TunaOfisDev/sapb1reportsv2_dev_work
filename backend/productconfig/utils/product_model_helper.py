# backend/productconfig/utils/product_model_helper.py
from typing import List, Optional, Tuple, Set
from django.db.models import QuerySet, Q, Sum, Prefetch
from decimal import Decimal
from django.core.exceptions import ValidationError

from ..models import ProductModel, Category, Option
from ..dto.question_context import QuestionContext

class ProductModelHelper:
    """
    ProductModel modeline yönelik özel işlemleri sağlayan yardımcı sınıf.
    """
    def filter_models_by_category(self, category: Category) -> QuerySet[ProductModel]:
        """
        Belirli bir kategoriye ait tüm ürün modellerini döndürür.
        """
        return ProductModel.objects.filter(
            category=category, 
            is_active=True
        ).order_by('name')

    def calculate_price_range_for_model(self, product_model: ProductModel) -> Tuple[Decimal, Decimal]:
        """
        Ürün modeline ait minimum ve maksimum fiyatları hesaplar.
        """
        options = product_model.applicable_options.filter(is_active=True)
        
        min_price_effect = options.aggregate(
            min_effect=Sum('price_modifier', filter=Q(price_modifier__lt=0))
        )['min_effect'] or Decimal('0')
        
        max_price_effect = options.aggregate(
            max_effect=Sum('price_modifier', filter=Q(price_modifier__gt=0))
        )['max_effect'] or Decimal('0')

        min_price = max(Decimal('0'), product_model.base_price + min_price_effect)
        max_price = product_model.base_price + max_price_effect
        
        return min_price, max_price

    def get_model_specific_options(self, model_id: int, context: Optional[QuestionContext] = None) -> QuerySet[Option]:
        """
        Belirli bir ürün modeline özgü seçenekleri getirir ve filtreler.
        """
        options = Option.objects.filter(
            applicable_product_models__id=model_id,
            is_active=True
        )

        if context and context.has_filters:
            # Marka filtresi
            if context.applicable_brands:
                options = options.filter(
                    Q(applicable_brands__id__in=context.applicable_brands) |
                    Q(applicable_brands__isnull=True)
                )
            
            # Kategori filtresi
            if context.applicable_categories:
                options = options.filter(
                    Q(applicable_categories__id__in=context.applicable_categories) |
                    Q(applicable_categories__isnull=True)
                )

            # Diğer filtreler
            if context.applicable_groups:
                options = options.filter(
                    Q(applicable_groups__id__in=context.applicable_groups) |
                    Q(applicable_groups__isnull=True)
                )

        return options.distinct()

    def get_model_with_options(self, model_id: int) -> Optional[ProductModel]:
        """
        Bir ürün modelini tüm seçenekleriyle birlikte getirir.
        """
        return ProductModel.objects.prefetch_related(
            Prefetch(
                'applicable_options',
                queryset=Option.objects.filter(is_active=True)
            )
        ).filter(id=model_id, is_active=True).first()

    def filter_models_with_criteria(self, criteria: dict) -> QuerySet[ProductModel]:
        """
        Belirli kriterlere göre ürün modellerini filtreler.
        """
        filters = Q(is_active=True)
        
        if 'category_id' in criteria:
            filters &= Q(category_id=criteria['category_id'])
            
        if 'price_range' in criteria:
            price_range = criteria['price_range']
            if 'min' in price_range:
                filters &= Q(base_price__gte=price_range['min'])
            if 'max' in price_range:
                filters &= Q(base_price__lte=price_range['max'])
                
        if 'is_configurable' in criteria:
            filters &= Q(is_configurable=criteria['is_configurable'])

        return ProductModel.objects.filter(filters).order_by('name')

    def validate_model_data(self, data: dict) -> None:
        """
        Ürün modeli verilerini validate eder.
        """
        if 'base_price' in data:
            if data['base_price'] < 0:
                raise ValidationError("Taban fiyat 0'dan küçük olamaz.")
            if data['base_price'] > 1000000:
                raise ValidationError("Taban fiyat 1.000.000'dan büyük olamaz.")

        if 'category' not in data:
            raise ValidationError("Kategori zorunludur.")