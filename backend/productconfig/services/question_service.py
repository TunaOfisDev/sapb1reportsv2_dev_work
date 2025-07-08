# backend/productconfig/services/question_service.py
from ..models import Question, Option, Variant, ProductGroup, Category
from .product_model_service import ProductModelService  # Bu satırı en üste ekleyin
from ..dto.question_context import QuestionContext
from ..utils.question_helper import QuestionHelper
from django.core.exceptions import ObjectDoesNotExist
import logging
from typing import Optional, List, Dict, Union, Tuple

logger = logging.getLogger(__name__)

class QuestionService:
    """Soru işlemleri için servis sınıfı"""

    def __init__(self):
        self.helper = QuestionHelper()
        self.product_model_service = ProductModelService() 

    def get_initial_question(self) -> Optional[Question]:
        """İlk master soruyu sıraya göre getirir"""
        return Question.objects.filter(
            category_type=Question.QuestionCategoryType.MASTER_QUESTION,
            is_active=True
        ).order_by('order').first()

    def get_question_by_id(self, question_id: int) -> Question:
        """ID ile soruyu getirir"""
        try:
            return Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise ObjectDoesNotExist(f"Soru bulunamadı: ID {question_id}")

    def get_next_question(self, variant: Variant, context: QuestionContext = None) -> Tuple[Optional[Question], QuestionContext]:
        """Sıradaki soruyu ve güncellenmiş bağlamı döndürür."""
        if context is None:
            context = QuestionContext(
                selected_brand=variant.brand,
                selected_group=variant.product_group,
                selected_category=variant.category,
                selected_model=variant.product_model
            )

        # Master sorular bitti mi kontrolü
        are_master_questions_completed = self._check_master_questions_completed(variant)
        if are_master_questions_completed and not context.is_after_master_questions:
            context.is_after_master_questions = True
            self._update_product_model_context(context)

        # Cevaplanmamış soruları al 
        unanswered_questions = self._get_unanswered_questions(variant)

        # Master sorular için kontrol
        if not context.is_after_master_questions:
            master_question = self._get_next_master_question(unanswered_questions)
            if master_question:
                return master_question, context

        # Model soruları için kontrol
        model_questions = self._get_model_questions(unanswered_questions)
        if not model_questions:
            return None, context

        # Uygun model sorusunu bul
        next_question = self._find_applicable_question(model_questions, context)
        return next_question, context

    def _check_master_questions_completed(self, variant) -> bool:
        """Master soruların tamamlanıp tamamlanmadığını kontrol eder"""
        master_questions = Question.objects.filter(
            category_type=Question.QuestionCategoryType.MASTER_QUESTION,
            is_active=True
        )
        answered_master_questions = variant.answered_questions.filter(
            category_type=Question.QuestionCategoryType.MASTER_QUESTION
        )
        return answered_master_questions.count() == master_questions.count()

    def _update_product_model_context(self, context: QuestionContext):
        """
        ProductModel context'ini günceller.
        """
        try:
            if context.selected_category:
                product_models = self.product_model_service.get_model_ids_by_category(
                    context.selected_category
                )
                if product_models:
                    context.applicable_product_models = set(product_models)
                    logger.debug(f"Applicable Product Models Güncellendi: {context.applicable_product_models}")
                else:
                    logger.warning("Seçilen kategori için uygun ürün modeli bulunamadı.")
        except Exception as e:
            logger.error(f"ProductModel güncellenirken hata: {str(e)}")


    def _get_latest_group_category(self, variant: Variant) -> Tuple[Optional[ProductGroup], Optional[Category]]:
        """Son seçilen grup ve kategori bilgisini alır"""
        if not variant.text_answers:
            return None
            
        # Yanıtları tersten iterate et
        for question_id, answer in sorted(
            variant.text_answers.items(), 
            key=lambda x: int(x[0]), 
            reverse=True
        ):
            if 'answer_id' not in answer:
                continue
                
            try:
                option = Option.objects.get(id=answer['answer_id'])
                
                # Grup ve kategori bilgisi varsa dön
                has_group = option.applicable_groups.exists()
                has_category = option.applicable_categories.exists()
                
                if has_group and has_category:
                    return (
                        option.applicable_groups.first(),
                        option.applicable_categories.first()
                    )
                    
            except Option.DoesNotExist:
                continue
                
        return None
            
    def process_answer(self, question: Question, answer: Union[str, int], variant: Variant) -> QuestionContext:
        """
        Soru cevabını işler, kaydeder ve güncellenmiş bağlamı döndürür.
        """
        logger.info(f"Yanıt işleniyor - Soru ID: {question.id}, Yanıt: {answer}")
        
        context = QuestionContext(
            selected_brand=variant.brand,
            selected_group=variant.product_group,
            selected_category=variant.category,
            selected_model=variant.product_model
        )

        if question.question_type == 'text_input':
            variant.text_answers[str(question.id)] = {
                "question_id": question.id,
                "answer_text": answer
            }
        else:
            selected_option = Option.objects.get(id=answer)
            variant.text_answers[str(question.id)] = {
                "question_id": question.id,
                "answer_id": answer,
                "answer_text": selected_option.name
            }

            # Seçenek üzerinden bağlamı güncelle
            context.update_from_option(selected_option)

            # Seçenek üzerinden bağlı alanları güncelle
            if selected_option.applicable_brands.exists():
                variant.brand = selected_option.applicable_brands.first()
                context.selected_brand = variant.brand

            if selected_option.applicable_groups.exists():
                variant.product_group = selected_option.applicable_groups.first()
                context.selected_group = variant.product_group
                
            if selected_option.applicable_categories.exists():
                variant.category = selected_option.applicable_categories.first()
                context.selected_category = variant.category
                
            if selected_option.applicable_product_models.exists():
                variant.product_model = selected_option.applicable_product_models.first()
                context.selected_model = variant.product_model

            variant.options.add(selected_option)

        variant.answered_questions.add(question)
        variant.save()

        logger.info(f"Yanıt başarıyla kaydedildi - Soru ID: {question.id}")
        return context


    def filter_questions_for_variant(self, variant: Variant, context: QuestionContext = None) -> List[Question]:
        """
        Variant için uygun soruları filtreler.
        """
        questions = Question.objects.filter(
            is_active=True
        ).exclude(
            id__in=variant.answered_questions.values_list('id', flat=True)
        ).order_by('order')

        # Ürün modeli ile ilişkilendirilmemiş soruları filtrele
        filtered_questions = [
            q for q in questions if self._is_question_applicable(q, context)
        ]

        return filtered_questions

    def _is_question_applicable(self, question: Question, context: QuestionContext) -> bool:
        """
        Sorunun context'e uygun olup olmadığını kontrol eder.
        """
        if question.category_type == Question.QuestionCategoryType.MASTER_QUESTION:
            return True

        if context.is_after_master_questions:
            # Ürün modeli sonrası sorular için ürün modeline uygunluk kontrolü
            if question.applicable_product_models.exists():
                model_ids = set(question.applicable_product_models.values_list('id', flat=True))
                if not (context.applicable_product_models & model_ids):
                    return False

        return True





    def serialize_question(self, question: Question, context: QuestionContext = None, request = None) -> Dict:
        """
        Soru nesnesini serializer eder
        """
        options = self.helper.get_options_for_question(question)
        
        # Context varsa seçenekleri filtrele
        if context and context.has_filters:
            options = [opt for opt in options if self._is_option_applicable(opt, context)]

        serialized_options = []
        for opt in options:
            option_data = {
                "id": opt.id,
                "name": opt.name,
                "option_type": opt.option_type,
                # Fiyat alanlarını ekle
                "final_price": str(opt.price_modifier),
                "normal_price": str(opt.normal_price),
                "price_melamine": str(opt.price_melamine),
                "price_laminate": str(opt.price_laminate),
                "price_veneer": str(opt.price_veneer),
                "price_lacquer": str(opt.price_lacquer),
                # Tetikleyici alanları ekle
                "melamine_triggers": list(opt.melamine_triggers.values_list('id', flat=True)),
                "laminate_triggers": list(opt.laminate_triggers.values_list('id', flat=True)),
                "veneer_triggers": list(opt.veneer_triggers.values_list('id', flat=True)),
                "lacquer_triggers": list(opt.lacquer_triggers.values_list('id', flat=True)),
                # Applicable alanları ekle
                "applicable_brands": [b.id for b in opt.applicable_brands.all()],
                "applicable_groups": [g.id for g in opt.applicable_groups.all()],
                "applicable_categories": [c.id for c in opt.applicable_categories.all()],
                "applicable_product_models": [m.id for m in opt.applicable_product_models.all()]
            }

            # Resim URL'sini ekle
            if opt.image:
                if request:
                    option_data["image_url"] = request.build_absolute_uri(opt.image.url)
                else:
                    option_data["image_url"] = opt.image.url
            else:
                option_data["image_url"] = None

            serialized_options.append(option_data)

        return {
            "id": question.id,
            "text": question.name,
            "type": question.question_type,
            "is_required": question.is_required,
            "help_text": question.help_text,
            "category_type": question.category_type,
            # Sorunun kendi applicable alanlarını da ekle
            "applicable_brands": [b.id for b in question.applicable_brands.all()],
            "applicable_groups": [g.id for g in question.applicable_groups.all()],
            "applicable_categories": [c.id for c in question.applicable_categories.all()],
            "applicable_product_models": [m.id for m in question.applicable_product_models.all()],
            "options": serialized_options
        }
    


    def _is_option_applicable(self, option: Option, context: QuestionContext) -> bool:
        """Seçeneğin context'e uygun olup olmadığını kontrol eder"""
        if context.applicable_brands:
            if option.applicable_brands.exists():
                if not any(brand_id in context.applicable_brands 
                          for brand_id in option.applicable_brands.values_list('id', flat=True)):
                    return False

        if context.applicable_categories:
            if option.applicable_categories.exists():
                if not any(cat_id in context.applicable_categories 
                          for cat_id in option.applicable_categories.values_list('id', flat=True)):
                    return False

        if context.applicable_product_models:
            if option.applicable_product_models.exists():
                if not any(model_id in context.applicable_product_models 
                          for model_id in option.applicable_product_models.values_list('id', flat=True)):
                    return False

        return True
    
    def is_last_master_question(self, variant) -> bool:
        """
        Variant'ın son cevaplanan sorusunun son master soru olup olmadığını kontrol eder
        """
        try:
            # Son cevaplanmış soruyu al
            last_answered = variant.answered_questions.order_by('-order').first()
            if not last_answered:
                return False

            # Cevaplanmamış master soru var mı kontrol et
            unanswered_master_exists = Question.objects.filter(
                category_type=Question.QuestionCategoryType.MASTER_QUESTION,
                is_active=True
            ).exclude(
                id__in=variant.answered_questions.values_list('id', flat=True)
            ).exists()

            # Son soru master soru ve cevaplanmamış master soru kalmadıysa True dön
            return (
                last_answered.category_type == Question.QuestionCategoryType.MASTER_QUESTION
                and not unanswered_master_exists
            )

        except Exception as e:
            logger.error(f"Master soru kontrolünde hata: {str(e)}")
            return False
        
    def _get_unanswered_questions(self, variant) -> List[Question]:
        """Cevaplanmamış soruları getirir"""
        return Question.objects.filter(
            is_active=True
        ).exclude(
            id__in=variant.answered_questions.values_list('id', flat=True)
        ).order_by('order')

    def _get_next_master_question(self, questions) -> Optional[Question]:
        """Sıradaki master soruyu döndürür"""
        return questions.filter(
            category_type=Question.QuestionCategoryType.MASTER_QUESTION
        ).first()

    def _get_model_questions(self, questions) -> List[Question]:
        """Ürün model sorularını döndürür"""
        return questions.filter(
            category_type=Question.QuestionCategoryType.PRODUCT_MODEL_QUESTION
        ).order_by('order')

    def _find_applicable_question(self, questions, context) -> Optional[Question]:
        """Uygun soruyu bulur"""
        for question in questions:
            # Ürün modeli uygunluk kontrolü ekle
            if question.applicable_product_models.exists():
                if context.applicable_product_models and not any(
                    model_id in context.applicable_product_models
                    for model_id in question.applicable_product_models.values_list('id', flat=True)
                ):
                    continue  # Uygun değilse diğer soruya geç

            if context.is_applicable_with_question(question):
                return question
        return None


    
    