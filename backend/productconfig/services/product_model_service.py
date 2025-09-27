# backend/productconfig/services/product_model_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from ..models import ProductModel, Category, Option
from ..utils.product_model_helper import ProductModelHelper
from ..dto.question_context import QuestionContext

class ProductModelService:
    """
    ProductModel işlemlerini yöneten servis sınıfı.
    """
    def __init__(self):
        self.helper = ProductModelHelper()

    def get_models_by_category(self, category: Category) -> QuerySet[ProductModel]:
        """Kategoriye ait product modelleri getirir"""
        return self.helper.filter_models_by_category(category)

    def get_model_ids_by_category(self, category: Category) -> List[int]:
        """Kategori için ürün model ID'lerini getirir"""
        return list(self.get_models_by_category(category).values_list('id', flat=True))

    def create_product_model(self, data: Dict[str, Any]) -> ProductModel:
        """
        Yeni bir ürün modeli oluşturur.
        """
        try:
            # Veri validasyonu
            self.helper.validate_model_data(data)
            
            # Model oluşturma
            model = ProductModel.objects.create(**data)
            
            # Fiyat aralığını güncelle
            self.update_price_range_for_model(model)
            
            return model
        except Exception as e:
            raise ValidationError(f"Ürün modeli oluşturulamadı: {str(e)}")

    def update_price_range_for_model(self, product_model: ProductModel) -> None:
        """
        Ürün modelinin minimum ve maksimum fiyatlarını günceller.
        """
        min_price, max_price = self.helper.calculate_price_range_for_model(product_model)
        product_model.min_price = min_price
        product_model.max_price = max_price
        product_model.save()

    def update_product_model(self, model_id: int, data: Dict[str, Any]) -> ProductModel:
        """
        Ürün modelini günceller.
        """
        try:
            model = ProductModel.objects.get(id=model_id)
            self.helper.validate_model_data(data)
            
            for key, value in data.items():
                setattr(model, key, value)
            
            model.save()
            self.update_price_range_for_model(model)
            
            return model
        except ProductModel.DoesNotExist:
            raise ValidationError(f"ID:{model_id} ürün modeli bulunamadı.")
        except Exception as e:
            raise ValidationError(f"Güncelleme hatası: {str(e)}")

    def delete_product_model(self, model_id: int, hard_delete: bool = False) -> None:
        """
        Ürün modelini siler.
        """
        try:
            model = ProductModel.objects.get(id=model_id)
            if hard_delete:
                model.hard_delete()
            else:
                model.delete()  # Soft delete
        except ProductModel.DoesNotExist:
            raise ValidationError(f"ID:{model_id} ürün modeli bulunamadı.")

    def get_model_options(self, model_id: int, context: Optional[QuestionContext] = None) -> QuerySet[Option]:
        """
        Ürün modeline özgü seçenekleri getirir.
        """
        return self.helper.get_model_specific_options(model_id, context)

    def get_model_with_options(self, model_id: int) -> Optional[ProductModel]:
        """
        Seçenekleriyle birlikte ürün modelini getirir.
        """
        return self.helper.get_model_with_options(model_id)

    def filter_models(self, criteria: Dict[str, Any]) -> QuerySet[ProductModel]:
        """
        Kriterlere göre ürün modellerini filtreler.
        """
        return self.helper.filter_models_with_criteria(criteria)

    def validate_configuration(self, model_id: int, selected_options: List[int]) -> bool:
        """
        Seçilen seçeneklerin ürün modeli için geçerli olup olmadığını kontrol eder.
        """
        try:
            model = self.get_model_with_options(model_id)
            if not model:
                raise ValidationError(f"ID:{model_id} ürün modeli bulunamadı.")

            # Seçenekleri kontrol et
            valid_option_ids = set(model.applicable_options.values_list('id', flat=True))
            selected_option_ids = set(selected_options)

            if not selected_option_ids.issubset(valid_option_ids):
                invalid_options = selected_option_ids - valid_option_ids
                raise ValidationError(f"Geçersiz seçenekler: {invalid_options}")

            return True
        except Exception as e:
            raise ValidationError(f"Validasyon hatası: {str(e)}")