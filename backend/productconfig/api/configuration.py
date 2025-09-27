# backend/productconfig/api/configuration.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from ..models import Option
from .pcserializers import ProductModelSerializer
from ..dto.question_context import  QuestionContext
from ..services import (
    BrandService, CategoryService, OptionService, ProductGroupService,
    ProductModelService, QuestionOptionRelationService, QuestionService,
    VariantService, DependentRuleService, ConditionalOptionsService, PriceMultiplierService
)
import logging

logger = logging.getLogger(__name__)
# .env dosyasından ENABLE_LOGGING değişkenini kontrol et
import os
if not os.getenv('ENABLE_LOGGING', 'True').lower() == 'true':
    logger.setLevel(logging.CRITICAL)  # Loglamayı sadece CRITICAL seviyesine indir

class ConfigurationAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brand_service = BrandService()
        self.category_service = CategoryService()
        self.option_service = OptionService()
        self.product_group_service = ProductGroupService()
        self.product_model_service = ProductModelService()
        self.question_option_relation_service = QuestionOptionRelationService()
        self.question_service = QuestionService()
        self.variant_service = VariantService()
        self.dependent_rule_service = DependentRuleService()
        self.conditional_options_service = ConditionalOptionsService()
        

    def get(self, request, variant_id=None):
        """
        Varyant ID ile mevcut yapilandirmayi doner, yoksa ilk soru ile ba_lar.
        """
        try:
            context = QuestionContext()

            if variant_id:
                variant = self.variant_service.get_variant(variant_id)
                context.update_from_variant_history(variant)

                current_question = self.question_service.get_current_question(variant)
                options = self.option_service.filter_options_for_question(current_question)
                filtered_options = context.refine_options(options)

                return Response({
                    'variant_id': variant.id,
                    'current_question': self.question_service.serialize_question(current_question),
                    'options': self._serialize_options(variant, filtered_options),  # Burada duzeltildi
                    'context': self._serialize_context(context),
                }, status=status.HTTP_200_OK)
            else:
                initial_question = self.question_service.get_initial_question()
                if initial_question:
                    return Response({
                        "question": self.question_service.serialize_question(initial_question),
                        "message": "Yapilandirma ba_latildi."
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'detail': '0lk soru bulunamadi.'},
                        status=status.HTTP_404_NOT_FOUND
                    )

        except ObjectDoesNotExist:
            return Response({'detail': 'Varyant bulunamadi.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"GET Hatasi: {str(e)}")
            return Response({'detail': f'Hata: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            variant_id = request.data.get('variant_id')
            question_id = request.data.get('question_id')
            answer = request.data.get('answer')

            if not question_id or answer is None:
                return Response(
                    {'detail': 'Soru ID ve yanit gereklidir.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question = self.question_service.get_question_by_id(question_id)

            if not variant_id:
                variant = self.variant_service.create_variant(question, answer)
            else:
                variant = self.variant_service.update_variant_with_answer(variant_id, question, answer)

            context = self._process_answer(question, answer, variant)
            next_question, updated_context = self._get_next_question(variant, context)

            if next_question:
                return self._prepare_next_question_response(next_question, variant, updated_context)
            else:
                return self._prepare_completion_response(variant)  # Guncellenmi_ variant_info ile doner

        except ObjectDoesNotExist as e:
            logger.error(f"Kayit bulunamadi hatasi: {str(e)}")
            return Response(
                {'detail': 'Belirtilen ID\'ye sahip soru veya varyant bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





    def _serialize_context(self, context):
        """
        Context bilgisini serialize eder.
        """
        return {
            "selected_brand": context.selected_brand.id if context.selected_brand else None,
            "selected_group": context.selected_group.id if context.selected_group else None,
            "selected_category": context.selected_category.id if context.selected_category else None,
            "selected_model": context.selected_model.id if context.selected_model else None,
        }



    def _handle_post_request(self, request):
        """Handle the main POST request logic"""
        variant_id = request.data.get('variant_id')
        question_id = request.data.get('question_id')
        answer = request.data.get('answer')

        if not question_id or answer is None:
            return Response(
                {'detail': 'Soru ID ve yanit gereklidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Secenek validasyonu
        if isinstance(answer, (list, int)):
            question = self.question_service.get_question_by_id(question_id)
            available_options = self.option_service.filter_options_for_question(question)
            available_option_ids = [opt.id for opt in available_options]
            
            answer_ids = [answer] if isinstance(answer, int) else answer
            if not self.conditional_options_service.validate_user_selection(answer_ids, available_option_ids):
                return Response(
                    {'detail': 'Gecersiz secenek secimi.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Mevcut i_lem mantigi devam eder...
        logger.info(f"Gelen veriler - Question ID: {question_id}, Answer: {answer}")
        question = self.question_service.get_question_by_id(question_id)
        variant = self._handle_variant(variant_id, question, answer)
        context = self._process_answer(question, answer, variant)
        next_question, updated_context = self._get_next_question(variant, context)

        if next_question:
            return self._prepare_next_question_response(next_question, variant, updated_context)
        else:
            return self._prepare_completion_response(variant)



    def _handle_variant(self, variant_id, question, answer):
        """Create or update variant"""
        if not variant_id:
            return self.variant_service.create_variant_with_answer(question, answer)
        return self.variant_service.update_variant_with_answer(variant_id, question, answer)

    def _process_answer(self, question, answer, variant):
        """
        Kullanici cevabini i_ler ve onceki secimlere dayali olarak guncellenmi_ context doner.
        """
        # 1. Cevabi i_le ve context'i guncelle
        context = self.question_service.process_answer(question, answer, variant)
        
        # 2. Master sorular tamamlandiysa ProductModel bilgilerini guncelle
        if self.question_service.is_last_master_question(variant):
            logger.debug("Son master soru tamamlandi, ProductModel bilgileri guncelleniyor.")
            # Secilen kategoriye bagli ProductModel'leri getir
            product_models_qs = self.product_model_service.get_models_by_category(context.selected_category)
            context.applicable_product_models = set(product_models_qs.values_list('id', flat=True))  # Set[int]
            context.is_after_master_questions = True
        
        # 3. Variant gecmi_ine gore context'i yeniden olu_tur
        context.update_from_variant_history(variant)
        
        # 4. Guncellenmi_ context bilgilerini logla
        logger.debug(f"""
            Kullanici cevabi i_lendi ve context guncellendi:
            Question ID: {question.id}
            Answer: {answer}
            Is After Master: {context.is_after_master_questions}
            Updated Applicable Brands: {context.applicable_brands}
            Updated Applicable Categories: {context.applicable_categories}
            Updated Applicable Models: {context.applicable_product_models}
            Selected Category: {context.selected_category}
        """)

        # 5. Guncellenmi_ context'i dondur
        return context

    def _get_next_question(self, variant, context):
        """
        Determine and return the next question based on variant's state and context
        """
        next_question, updated_context = self.question_service.get_next_question(variant, context)
        
        if next_question is None:
            # Tum sorular tamamlandi
            logger.debug("Tum sorular tamamlandi, varyant guncelleniyor...")
            # Son context bilgilerini varyanta yansit
            if updated_context:
                self._update_variant_with_context(variant, updated_context)
                
            variant.status = 'completed'
            variant.save()
            
        return next_question, updated_context
    
    def _update_variant_with_context(self, variant, context):
        """
        Variant'i context bilgilerine gore gunceller
        """
        if context.selected_brand:
            variant.brand = context.selected_brand
        if context.selected_group:
            variant.product_group = context.selected_group
        if context.selected_category:
            variant.category = context.selected_category
        if context.selected_model:
            variant.product_model = context.selected_model
        variant.save()
    


    def _prepare_next_question_response(self, next_question, variant, context):
        """
        Siradaki soru icin yanit hazirlar.
        """
        # 1. Soru verilerini serialize et
        question_data = self.question_service.serialize_question(next_question)

        # 2. Secenekleri filtrele
        filtered_options = self._filter_options_based_on_context(next_question, context)

        # 3. Kullanici tarafindan secilen secenekleri belirle
        user_selected_options = self._get_user_selected_options(variant)

        # 4. Mevcut secenekleri serialize et
        serialized_options = self._serialize_options(variant, filtered_options)

        # 5. Koşullu secenekleri birleştir
        question_data['options'] = self.conditional_options_service.merge_with_existing_options(
            next_question.id,
            serialized_options,
            user_selected_options
        )

        # 6. ProductModel verilerini ekle
        product_models = (
            self.product_model_service.get_models_by_category(context.selected_category)
            if context.selected_category else None
        )
        serialized_product_models = (
            ProductModelSerializer(product_models, many=True).data
            if product_models else []
        )

        # 7. Yanıt verisini oluştur
        response_data = {
            'variant_id': variant.id,
            'variant_info': self.variant_service.get_variant_info(variant),
            'question': question_data,
            'context': {
                'is_after_master': context.is_after_master_questions,
                'selected_category': context.selected_category.id if context.selected_category else None,
                'applicable_models': serialized_product_models
            },
            'is_completed': False  # Başlangıçta sorular tamamlanmadı
        }

        # 8. Eğer `next_question` yoksa, yani tüm sorular tamamlandıysa:
        if not next_question:
            response_data['is_completed'] = True
            response_data['question'] = None  # Sonraki soru yok

        # 9. Secenek kontrolu
        if not question_data['options'] and next_question and next_question.question_type not in ['text_input']:
            response_data['warning'] = 'Bu soru icin uygun secenek bulunamadi.'

        return Response(response_data, status=status.HTTP_200_OK)



    def _filter_options_based_on_context(self, next_question, context):
        """
        Context'e gore secenekleri filtreler.
        """
        if context.is_after_master_questions and context.applicable_product_models:
            # ProductModel'lere gore filtreleme
            return self.option_service.get_options_by_product_models(
                next_question,
                context.applicable_product_models
            )
        else:
            # Applicable filtrelere gore secenekleri filtrele
            return self.option_service.filter_options_for_question(
                next_question,
                applicable_brands=context.applicable_brands if context.has_filters else None,
                applicable_groups=context.applicable_groups if context.has_filters else None,
                applicable_categories=context.applicable_categories if context.has_filters else None,
                applicable_product_models=context.applicable_product_models if context.has_filters else None
            )

    def _get_user_selected_options(self, variant):
        """
        Kullanici tarafindan secilen secenekleri dondurur.
        """
        user_selected_options = []
        if variant.text_answers:
            for answer in variant.text_answers.values():
                if 'answer_id' in answer:
                    user_selected_options.append(answer['answer_id'])
                elif 'answer_ids' in answer:
                    user_selected_options.extend(answer['answer_ids'])
        return user_selected_options

    def calculate_option_final_price(self, option, selected_option_ids):
        """
        Bir secenegin aktif fiyatini hesaplar.
        """
        # Malzeme bazli fiyat belirleme
        if any(trigger.id in selected_option_ids for trigger in option.melamine_triggers.all()):
            base_price = option.price_melamine
        elif any(trigger.id in selected_option_ids for trigger in option.laminate_triggers.all()):
            base_price = option.price_laminate
        elif any(trigger.id in selected_option_ids for trigger in option.veneer_triggers.all()):
            base_price = option.price_veneer
        elif any(trigger.id in selected_option_ids for trigger in option.lacquer_triggers.all()):
            base_price = option.price_lacquer
        else:
            base_price = option.normal_price

        # carpan kurallari
        price_details = PriceMultiplierService().get_multiplier_details(
            option=option,
            selected_option_ids=selected_option_ids
        )

        return base_price * price_details['final_multiplier']

    def _serialize_options(self, variant, options):
        """
        Seçenekleri serialize eder.
        """
        selected_option_ids = list(variant.options.values_list('id', flat=True))
        return [
            {
                "id": opt.id,
                "name": opt.name,
                "option_type": opt.option_type,
                "final_price": str(self.calculate_option_final_price(opt, selected_option_ids)),
                "normal_price": str(opt.normal_price),
                "price_melamine": str(opt.price_melamine),
                "price_laminate": str(opt.price_laminate),
                "price_veneer": str(opt.price_veneer),
                "price_lacquer": str(opt.price_lacquer),
                "melamine_triggers": list(opt.melamine_triggers.values_list('id', flat=True)),
                "laminate_triggers": list(opt.laminate_triggers.values_list('id', flat=True)),
                "veneer_triggers": list(opt.veneer_triggers.values_list('id', flat=True)),
                "lacquer_triggers": list(opt.lacquer_triggers.values_list('id', flat=True)),
                "image_url": self.request.build_absolute_uri(opt.image.url) if opt.image else None,
                # Applicable ilişkileri ekleniyor
                "applicable_brands": list(opt.applicable_brands.values_list('id', flat=True)),
                "applicable_groups": list(opt.applicable_groups.values_list('id', flat=True)),
                "applicable_categories": list(opt.applicable_categories.values_list('id', flat=True)),
                "applicable_product_models": list(opt.applicable_product_models.values_list('id', flat=True))
            }
            for opt in options
        ]



    def _prepare_completion_response(self, variant):
        """
        Tamamlanmış varyant bilgilerini hazırlar.
        """
        try:
            # Varyant durumunu tamamlandı olarak işaretle
            variant.status = 'completed'
            variant.save()

            logger.info(f"Tüm sorular tamamlandı - Variant ID: {variant.id}")

            # Varyant özetini ve detaylarını al
            variant_summary = self.variant_service.get_variant_summary(variant)
            variant_info = self.variant_service.get_variant_info(variant)

            return Response({
                'variant_id': variant.id,
                'detail': 'Yapılandırma tamamlandı.',
                'variant_info': variant_info,
                'is_completed': True  # Soruların tamamlandığını belirt
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Tamamlama yanıtı hazırlanırken hata: {str(e)}")
            return Response({'detail': f'Tamamlanma hatası: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    

    def delete(self, request, variant_id=None):
        """Varyanti siler"""
        try:
            if not variant_id:
                return Response(
                    {'detail': 'Varyant ID gereklidir.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.variant_service.delete_variant(variant_id)
            return Response(
                {'detail': 'Varyant ba_ariyla silindi.'},
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Varyant bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Silme hatasi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, variant_id):
        """Bir onceki soruya geri doner"""
        try:
            # Varyant servis uzerinden varyanti al
            variant = self.variant_service.get_variant(variant_id)
            
            # Geri alma i_lemini gercekle_tir
            previous_question = self.variant_service.revert_last_answer(variant)

            if previous_question:
                # Context'i guncelle
                context = QuestionContext()
                context.update_from_variant_history(variant)
                
                return self._prepare_next_question_response(
                    previous_question, 
                    variant,
                    context
                )
            else:
                return Response(
                    {'detail': 'Geri donulecek soru kalmadi.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Varyant bulunamadi.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Geri alma hatasi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    def refine_options_by_previous_selections(self, context: QuestionContext, current_options: QuerySet[Option]) -> QuerySet[Option]:
        """
        onceki secimlere ve QuestionContext'e gore secenekleri filtreler.
        """
        # Eger filtreleme icin bir gecmi_ yoksa, oldugu gibi dondur
        if not context.has_filters:
            logger.debug("Filtreleme yapilmadi, tum secenekler donduruluyor.")
            return current_options

        # 0lk olarak, QuestionContext uzerinden applicable filtreleme uygula
        filtered_options = context.apply_applicable_filters(current_options)
        logger.debug(f"Applicable filtre sonrasi secenekler: {filtered_options}")

        # Daha sonra secim gecmi_ine gore filtreleme yap
        selection_history = context.selection_history
        category_ids = set()
        model_ids = set()

        # Secim gecmi_inden applicable alanlari topla
        for answer in selection_history.values():
            if 'applicable_categories' in answer:
                category_ids.update(answer['applicable_categories'])
            if 'applicable_product_models' in answer:
                model_ids.update(answer['applicable_product_models'])

        # Kategori bazli filtreleme
        if category_ids:
            filtered_options = filtered_options.filter(
                applicable_categories__id__in=category_ids
            )
            logger.debug(f"Kategori filtreleme sonrasi secenekler: {filtered_options}")

        # Model bazli filtreleme
        if model_ids and context.is_after_master_questions:
            filtered_options = filtered_options.filter(
                applicable_product_models__id__in=model_ids
            )
            logger.debug(f"Model filtreleme sonrasi secenekler: {filtered_options}")

        # Ekstra filtreleme gerektiginde burada tanimlanabilir (ornegin, ozel kullanici kurallari)
        filtered_options = context.apply_additional_filters(filtered_options)

        # Sonuclari distinct olarak dondur
        return filtered_options.distinct()



    def filter_product_chain(self, current_options: QuerySet[Option], context) -> QuerySet[Option]:
        """
        urun zinciri ili_kilerine gore filtreleme yapar
        """
        filtered = current_options
        
        if self.selected_category:
            filtered = filtered.filter(
                applicable_categories=self.selected_category,
                applicable_product_models__category=self.selected_category
            )
        
        if self.selected_model:
            filtered = filtered.filter(
                applicable_product_models=self.selected_model
            )
        
        return filtered.distinct()