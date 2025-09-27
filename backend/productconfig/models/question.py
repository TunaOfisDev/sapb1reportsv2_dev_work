# backend/productconfig/models/question.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel
from .brand import Brand
from .product_group import ProductGroup
from .product_model import ProductModel
from .category import Category

class Question(BaseModel):
    """
    Temel soru modeli
    """
    class QuestionType(models.TextChoices):
        CHOICE = 'choice', _('Tekli Seçim')
        MULTIPLE_CHOICE = 'multiple_choice', _('Çoklu Seçim')
        TEXT_INPUT = 'text_input', _('Metin Girişi')

    class QuestionCategoryType(models.TextChoices):
        MASTER_QUESTION = 'master_question', _('Master Sorusu')
        PRODUCT_MODEL_QUESTION = 'productmodel_question', _('Ürün Model Sorusu')

    # Model alanları
    name = models.CharField(max_length=255, verbose_name=_("Soru Adı"))
    question_type = models.CharField(max_length=25, choices=QuestionType.choices, verbose_name=_("Soru Tipi"))
    category_type = models.CharField(max_length=25, choices=QuestionCategoryType.choices, verbose_name=_("Soru Kategori Türü"))
    is_required = models.BooleanField(default=True, verbose_name=_("Zorunlu mu"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Soru Sırası"))
    variant_order = models.PositiveIntegerField(default=0, verbose_name=_("Variant Sırası"))
    help_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Yardım Metni"))

    # İlişkiler
    applicable_brands = models.ManyToManyField(Brand, blank=True, related_name="applicable_questions", verbose_name=_("İlgili Markalar"))
    applicable_groups = models.ManyToManyField(ProductGroup, blank=True, related_name="applicable_questions", verbose_name=_("İlgili Gruplar"))
    applicable_categories = models.ManyToManyField(Category, blank=True, related_name="applicable_questions", verbose_name=_("İlgili Kategoriler"))
    applicable_product_models = models.ManyToManyField(ProductModel, blank=True, related_name="applicable_questions", verbose_name=_("İlgili Ürün Modelleri"))

    class Meta:
        verbose_name = "05-Soru"
        verbose_name_plural = "05-Sorular"
        ordering = ['order']


    def __str__(self):
        return f"{self.name} ({self.get_question_type_display()})"

    def is_visible(self, variant) -> bool:
        """Sorunun görünür olup olmadığını kontrol eder."""
        dependent_rules = self.dependent_rules.filter(is_active=True)
        if not dependent_rules.exists():
            return True
        return any(rule.evaluate(variant) for rule in dependent_rules)

    
    def is_applicable_for_variant(self, variant, context=None) -> bool:
        """
        Sorunun variant için uygulanabilir olup olmadığını kontrol eder.
        TÜM applicable_* alanlarında en az bir eşleşme olmalıdır.
        """
        # Master sorular her zaman uygulanabilir
        if self.category_type == self.QuestionCategoryType.MASTER_QUESTION:
            return True

        # Variant bazlı kontroller
        if self.applicable_brands.exists():
            if not variant.brand or variant.brand not in self.applicable_brands.all():
                return False

        if self.applicable_categories.exists():
            if not variant.category or variant.category not in self.applicable_categories.all():
                return False

        if self.applicable_product_models.exists():
            if not variant.product_model or variant.product_model not in self.applicable_product_models.all():
                return False

        # Context bazlı kontroller
        if context and context.has_filters:
            # Brand eşleşmesi kontrolü
            if self.applicable_brands.exists():
                brand_match = False
                for brand_id in self.applicable_brands.values_list('id', flat=True):
                    if brand_id in context.applicable_brands:
                        brand_match = True
                        break
                if not brand_match:
                    return False

            # Category eşleşmesi kontrolü
            if self.applicable_categories.exists():
                category_match = False
                for category_id in self.applicable_categories.values_list('id', flat=True):
                    if category_id in context.applicable_categories:
                        category_match = True
                        break
                if not category_match:
                    return False

            # Product Model eşleşmesi kontrolü
            if self.applicable_product_models.exists():
                model_match = False
                for model_id in self.applicable_product_models.values_list('id', flat=True):
                    if model_id in context.applicable_product_models:
                        model_match = True
                        break
                if not model_match:
                    return False

        return True