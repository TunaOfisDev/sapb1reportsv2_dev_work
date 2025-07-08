# backend/productconfig/utils/question_helper.py
from typing import List
from ..models import Question, Option, ProductModel, Category, Brand
import logging

logger = logging.getLogger(__name__)

class QuestionHelper:
    """
    Soru modeline yönelik temel işlemleri sağlayan yardımcı sınıf.
    """

    def get_master_questions(self, brand: Brand, category: Category):
        """
        Seçilen marka ve kategoriye göre master soruları filtreler.
        """
        return Question.objects.filter(
            category_type=Question.QuestionCategoryType.MASTER_QUESTION,
            applicable_brands=brand,
            applicable_categories=category,
            is_active=True
        ).order_by('order')

    def get_product_model_questions(self, brand: Brand, category: Category, model: ProductModel):
        """
        Seçilen marka, kategori ve modele göre ürün modeline özgü soruları filtreler.
        """
        return Question.objects.filter(
            category_type=Question.QuestionCategoryType.PRODUCT_MODEL_QUESTION,
            applicable_brands=brand,
            applicable_categories=category,
            applicable_product_models=model,
            is_active=True
        ).order_by('order')

    def get_options_for_question(self, question: Question):
        """
        Verilen soruya bağlı seçenekleri getirir.
        """
        if question.question_option_relations.exists():
            relation = question.question_option_relations.first()
            return relation.options.all()
        return Option.objects.none()  # İlişki yoksa boş döndür


    
