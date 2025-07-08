# backend/productconfig/services/variant_service.py
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from decimal import Decimal
from django.db.models import QuerySet
from ..models import Variant, Question, Option, DependentRule
from .question_service import QuestionService
from .dependent_rule_service import DependentRuleService
from .price_multiplier_service import PriceMultiplierService  # Yeni eklenen import
from .old_component_code_service import OldComponentCodeService
from ..utils import VariantHelper, DependentRuleHelper
from ..utils.data_fetcher import fetch_hana_db_data
import logging

logger = logging.getLogger(__name__)
# .env dosyasından ENABLE_LOGGING değişkenini kontrol et
import os
if not os.getenv('ENABLE_LOGGING', 'True').lower() == 'true':
    logger.setLevel(logging.CRITICAL)  # Loglamayı sadece CRITICAL seviyesine indir

class VariantService:
    def __init__(self):
        self.dependent_rule_service = DependentRuleService()
        self.question_service = QuestionService()
        self.helper = DependentRuleHelper()
        self.price_multiplier_service = PriceMultiplierService()
        self.old_component_code_service = OldComponentCodeService()

    def create_variant_with_answer(self, question, answer):
        """
        Bir varyant oluşturur ve soruya verilen cevabı işler.
        """
        # Sadece modelde bulunan alanlarla işlem yapalım
        variant = Variant.objects.create(
            project_name=answer if question.question_type == 'text_input' else '',
            status=Variant.VariantStatus.DRAFT
        )
        logger.info("Yeni varyant oluşturuldu: %s", variant.id)
        self.process_answer(variant, question, answer)
        return variant

    def create_variant(self, question=None, answer=None):
        """
        Yeni bir varyant oluşturur.
        """
        variant = Variant.objects.create(
            project_name=answer if question and question.question_type == 'text_input' else '',
            status=Variant.VariantStatus.DRAFT
        )
        if question and answer:
            variant.text_answers = {str(question.id): {"answer": answer}}
            variant.save()
        return variant


    def update_variant_with_answer(self, variant_id, question, answer):
        """
        Var olan varyant üzerinde yanıt güncellemeleri yapar.
        """
        try:
            variant = Variant.objects.get(id=variant_id)
            self.process_answer(variant, question, answer)
            return variant
        except Variant.DoesNotExist:
            raise ObjectDoesNotExist(f"Variant ID {variant_id} bulunamadı.")



    def process_answer(self, variant: Variant, question: Question, answer):
        """
        Varyanta verilen yanıtları işler.
        """
        logger.info(f"Yanıt işleniyor - Varyant ID: {variant.id}, Soru ID: {question.id}, Yanıt: {answer}")
        selected_option = None

        if question.question_type == 'text_input':
            variant.text_answers[str(question.id)] = {
                "question_id": question.id,
                "answer_text": answer
            }
        elif question.question_type == 'choice':
            selected_option = Option.objects.get(id=answer)
            variant.options.add(selected_option)
            variant.text_answers[str(question.id)] = {
                "question_id": question.id,
                "answer_id": selected_option.id,
                "answer_text": selected_option.name
            }
        elif question.question_type == 'multiple_choice':
            if not isinstance(answer, (list, tuple)):
                answer = [answer]
            selected_options = Option.objects.filter(id__in=answer)
            variant.options.add(*selected_options)
            variant.text_answers[str(question.id)] = {
                "question_id": question.id,
                "answer_ids": [option.id for option in selected_options],
                "answer_texts": [option.name for option in selected_options]
            }

        variant.save()
        logger.debug(f"Varyant yanıt kaydedildi: {variant.text_answers}")

        # Soru answered_questions'a ekleniyor
        variant.answered_questions.add(question)

        # Varyant detaylarını güncelle
        self._update_variant_details(variant)

        # Koşullu soruları değerlendir
        self._evaluate_conditional_questions(variant, question)

        # Eski bileşen kodlarını oluştur ve güncelle
        self._update_old_component_codes(variant)



    def _update_old_component_codes(self, variant: Variant):
        """
        Eski bileşen kodlarını oluşturur ve varyanta kaydeder.
        """
        try:
            # OldComponentCodeService ile eski kodları oluştur
            old_codes_result = self.old_component_code_service.generate_codes_for_variant(variant)
            
            # Eğer dönen sonuç bir liste ise doğrudan eski bileşen kodlarına ata
            if isinstance(old_codes_result, list):
                variant.old_component_codes = old_codes_result
                variant.save()
                logger.info(f"Eski bileşen kodları güncellendi - Variant ID: {variant.id}")
            elif isinstance(old_codes_result, dict) and old_codes_result.get('status') == 'success':
                # Eğer sonuç sözlük yapısında ise
                variant.old_component_codes = old_codes_result.get('codes', [])
                variant.save()
                logger.info(f"Eski bileşen kodları güncellendi - Variant ID: {variant.id}")
            else:
                logger.warning(f"Eski bileşen kodları oluşturulamadı - Variant ID: {variant.id}, Hata: {old_codes_result}")
        except Exception as e:
            logger.error(f"Eski bileşen kod güncelleme hatası - Variant ID: {variant.id}, Hata: {str(e)}")




    def _update_variant_details(self, variant: Variant):
        """
        Varyantın kodunu, açıklamasını, fiyatını ve eski bileşen kodlarını günceller.
        Hem malzeme bazlı fiyatı hem de çarpan kurallarını uygular.
        """
        try:
            # Varyant kodu ve açıklamasını güncelle
            variant.variant_code = VariantHelper.format_variant_code(variant)
            variant.variant_description = VariantHelper.update_variant_description(variant)

            # Seçili tüm seçenekleri ve ID'leri al
            selected_options = list(variant.options.all())
            selected_option_ids = set()
            for answer in variant.text_answers.values():
                if 'answer_id' in answer:
                    selected_option_ids.add(answer['answer_id'])
                elif 'answer_ids' in answer:
                    selected_option_ids.update(answer['answer_ids'])

            # Toplam fiyatı hesapla
            total_price = Decimal('0')
            for option in selected_options:
                # 1. Malzeme bazlı fiyatı hesapla
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

                # 2. Çarpan kurallarını uygula
                price_details = self.price_multiplier_service.get_multiplier_details(
                    option=option,
                    selected_option_ids=list(selected_option_ids)
                )

                # Eğer çarpan varsa uygula
                final_price = base_price * price_details['final_multiplier']

                # Option'ın price_modifier alanını güncelle
                option.price_modifier = final_price
                option.save()

                total_price += final_price

                logger.debug(
                    f"Seçenek fiyat hesaplama - "
                    f"ID: {option.id}, "
                    f"Base Price: {base_price}, "
                    f"Multiplier: {price_details['final_multiplier']}, "
                    f"Final Price: {final_price}"
                )

            # Toplam fiyatı kaydet
            variant.total_price = total_price

            # Eski bileşen kodlarını oluştur ve kaydet
            old_component_codes = self.old_component_code_service.generate_codes_for_variant(variant)
            if old_component_codes:
                variant.old_component_codes = old_component_codes
                logger.debug(
                    f"Eski bileşen kodları güncellendi - Variant ID: {variant.id}, "
                    f"Codes: {old_component_codes}"
                )
            else:
                logger.warning(f"Eski bileşen kodları oluşturulamadı - Variant ID: {variant.id}")

            # Varyantı kaydet
            variant.save()

            logger.info(
                f"Varyant detayları güncellendi - "
                f"ID: {variant.id}, "
                f"Total Price: {total_price}, "
                f"Old Component Codes: {old_component_codes}"
            )

        except Exception as e:
            logger.error(f"Varyant detay güncelleme hatası: {str(e)}")
            # Hata durumunda temel fiyat hesaplamasını kullan
            variant.total_price = VariantHelper.calculate_total_price(variant)
            variant.old_component_codes = []
            variant.save()

    def generate_codes_for_variant(self, variant: Variant) -> list:
        """
        Variant için eski bileşen kodlarını oluşturur.
        """
        try:
            matching_rules = self.helper.find_matching_rules(variant)
            generated_codes = []

            for rule in matching_rules:
                result = rule.generate_code(variant.text_answers)
                if result:
                    generated_codes.extend(result['codes'])

            return generated_codes  # Liste olarak dön
        except Exception as e:
            logger.error(f"Eski bileşen kod oluşturma hatası: {str(e)}")
            return []




    def calculate_option_final_price(option, selected_option_ids):
        """
        Bir seçeneğin aktif fiyatını hesaplar.
        """
        # Malzeme bazlı fiyat belirleme
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

        # Çarpan kuralları
        price_details = PriceMultiplierService().get_multiplier_details(
            option=option,
            selected_option_ids=selected_option_ids
        )

        return base_price * price_details['final_multiplier']




    def _evaluate_conditional_questions(self, variant: Variant, question: Question):
        """
        Koşullu soruları değerlendirir ve günceller.
        Sadece mevcut soru için kuralları değerlendirir.
        """
        logger.info(f"Koşullu sorular değerlendiriliyor - Soru ID: {question.id}")
        rules = self.helper.get_rules_for_question(question)
        logger.debug(f"İlgili kurallar: {[rule.id for rule in rules]}")

        for rule in rules:
            logger.debug(f"Kural değerlendiriliyor: Kural ID {rule.id}")
            is_triggered = self.helper.evaluate_rule(rule, variant)
            logger.debug(f"Kural değerlendirme sonucu: {is_triggered}")

            dependent_questions = rule.dependent_questions.all()
            
            if rule.rule_type == DependentRule.RuleType.SHOW_ON_OPTION:
                if is_triggered:
                    self._activate_dependent_questions(dependent_questions, variant)
                else:
                    self._deactivate_dependent_questions(dependent_questions, variant)
            else:  # HIDE_ON_OPTION
                if is_triggered:
                    self._deactivate_dependent_questions(dependent_questions, variant)
                else:
                    self._activate_dependent_questions(dependent_questions, variant)

            logger.debug(f"Kural değerlendirmesi tamamlandı: Kural ID {rule.id}")


    def _activate_dependent_questions(self, questions: QuerySet, variant: Variant):
        """
        Bağımlı soruları sadece variant için aktifleştirir.
        """
        for question in questions:
            # Sadece variant.answered_questions ilişkisini ekle
            if question not in variant.answered_questions.all():
                variant.answered_questions.add(question)
                logger.info(f"Bağımlı soru variant için aktifleştirildi - Soru ID: {question.id}")
                variant.save()

    def _deactivate_dependent_questions(self, questions: QuerySet, variant: Variant):
        """
        Bağımlı soruları sadece variant için devre dışı bırakır.
        """
        for question in questions:
            # Sadece variant.answered_questions ilişkisini kaldır
            if question in variant.answered_questions.all():
                variant.answered_questions.remove(question)
                # Yanıtı da temizle
                if str(question.id) in variant.text_answers:
                    del variant.text_answers[str(question.id)]
                logger.info(f"Bağımlı soru variant için devre dışı bırakıldı - Soru ID: {question.id}")
                variant.save()

    
    def get_variant_summary(self, variant: Variant):
        """
        Varyantın özet bilgilerini döndürür.
        Seçenek fiyatlarını, çarpan detaylarını ve varyantın toplam fiyatını içerir.
        """
        try:
            # Seçilen seçeneklerin IDsini al
            selected_options = list(variant.options.all())
            selected_option_ids = [opt.id for opt in selected_options]

            # Seçenek özetini oluştur
            options_summary = []
            for option in selected_options:
                # Final fiyatı ve çarpan detaylarını hesapla
                base_price = self._calculate_base_price(option, selected_option_ids)
                price_details = self.price_multiplier_service.get_multiplier_details(
                    option=option,
                    selected_option_ids=selected_option_ids
                )
                final_price = base_price * price_details['final_multiplier']

                options_summary.append({
                    "id": option.id,
                    "name": option.name,
                    "base_price": str(base_price),
                    "final_price": str(final_price),
                    "multiplier": float(price_details['final_multiplier']),
                    "applied_rules": price_details['rules']
                })

            # Varyant özetini döndür
            return {
                "variant_code": variant.variant_code,
                "variant_description": variant.variant_description,
                "total_price": str(variant.total_price),
                "selected_options": options_summary
            }

        except Exception as e:
            logger.error(f"Varyant özeti getirme hatası: {str(e)}")
            # Hata durumunda temel bir özet döndür
            return {
                "variant_code": variant.variant_code,
                "variant_description": variant.variant_description,
                "total_price": str(variant.total_price)
            }

    def _calculate_base_price(self, option, selected_option_ids):
        """
        Seçeneğin baz fiyatını malzeme tetikleyicilerine göre hesaplar.
        """
        if any(trigger.id in selected_option_ids for trigger in option.melamine_triggers.all()):
            return option.price_melamine
        elif any(trigger.id in selected_option_ids for trigger in option.laminate_triggers.all()):
            return option.price_laminate
        elif any(trigger.id in selected_option_ids for trigger in option.veneer_triggers.all()):
            return option.price_veneer
        elif any(trigger.id in selected_option_ids for trigger in option.lacquer_triggers.all()):
            return option.price_lacquer
        return option.normal_price


    def get_variant_info(self, variant):
        """
        Variant'ın detay bilgilerini güvenli şekilde döner.
        """
        try:
            # old_component_codes'u güvenli şekilde kontrol edip listeye dönüştür
            if isinstance(variant.old_component_codes, list):
                formatted_old_component_codes = variant.old_component_codes
            elif isinstance(variant.old_component_codes, str):
                formatted_old_component_codes = variant.old_component_codes.split(", ")
            else:
                formatted_old_component_codes = []

            # Variant özetini oluştur
            variant_info = {
                "id": variant.id,
                "project_name": variant.project_name,
                "variant_code": variant.variant_code,
                "variant_description": variant.variant_description,
                "total_price": str(variant.total_price),
                "status": variant.status,
                "created_at": variant.created_at,
                "old_component_codes": formatted_old_component_codes,  # Güvenli liste
            }
            return variant_info

        except Exception as e:
            logger.error(f"Varyant bilgisi getirme hatası: {str(e)}")
            return {
                "id": variant.id,
                "project_name": variant.project_name,
                "variant_code": variant.variant_code,
                "variant_description": variant.variant_description,
                "total_price": str(variant.total_price),
                "status": variant.status,
                "created_at": variant.created_at,
                "old_component_codes": []
            }



    def get_variant(self, variant_id: int) -> Variant:
        """
        ID'ye göre varyant getirir
        """
        try:
            return Variant.objects.get(id=variant_id)
        except Variant.DoesNotExist:
            logger.error(f"Varyant bulunamadı: {variant_id}")
            raise ObjectDoesNotExist(f"Varyant bulunamadı: {variant_id}")
        except Exception as e:
            logger.error(f"Varyant getirme hatası: {str(e)}")
            raise


    def get_next_question(self, variant, selected_option=None):
        """
        Kullanıcının seçimine göre sıradaki uygun soruyu belirler.
        """
        context = {"hidden_questions": []}  # Gizli soruları geçici olarak tutmak için context kullan
        current_question = self.question_service.get_current_question(variant)

        # Sıradaki görünür soruyu belirle
        all_questions = self.question_service.get_all_questions()
        visible_questions = [
            question for question in all_questions
            if question.id not in context.get("hidden_questions", [])
        ]

        # Sıradaki soruyu döndür
        for question in visible_questions:
            if question not in variant.answered_questions.all():
                return question
        return None


    def revert_last_answer(self, variant: Variant):
        """Son soruya verilen yanıtı geri alır"""
        try:
            # Son yanıtlanan soruyu bul
            last_question = variant.answered_questions.order_by('-id').first()
            if not last_question:
                return None

            # Son sorunun yanıtını al
            answer = variant.text_answers.get(str(last_question.id))
            if answer and 'answer_id' in answer:
                # Seçeneği options'dan kaldır
                option = Option.objects.get(id=answer['answer_id'])
                variant.options.remove(option)

            # Soruyu answered_questions'dan kaldır
            variant.answered_questions.remove(last_question)
            
            # text_answers'dan kaldır
            if str(last_question.id) in variant.text_answers:
                del variant.text_answers[str(last_question.id)]

            # Varyant detaylarını güncelle
            self._update_variant_details(variant)
            
            # Bir önceki soruya dön
            previous_question = variant.answered_questions.order_by('-id').first()
            return previous_question

        except Exception as e:
            logger.error(f"Geri alma hatası: {str(e)}")
            raise

    def delete_variant(self, variant_id: int):
        """Varyantı tamamen siler"""
        try:
            variant = Variant.objects.get(id=variant_id)
            # İlişkili kayıtları temizle
            variant.options.clear()
            variant.answered_questions.clear()
            # Varyantı sil
            variant.hard_delete()
            return True
        except Variant.DoesNotExist:
            logger.error(f"Silinecek varyant bulunamadı: {variant_id}")
            raise
        except Exception as e:
            logger.error(f"Varyant silme hatası: {str(e)}")
            raise

    def get_previous_answers(self, variant: Variant):
        """Varyantın önceki yanıtlarını getirir"""
        answers = []
        for question in variant.answered_questions.order_by('variant_order', 'order'):
            answer = variant.text_answers.get(str(question.id))
            if answer:
                answers.append({
                    'question_id': question.id,
                    'question_text': question.name,
                    'answer_id': answer.get('answer_id'),
                    'answer_text': answer.get('answer_text')
                })
        return answers


    def get_variant_list(self, **filters):
        """
        Filtrelere göre varyant listesini getirir.
        """
        queryset = Variant.objects.filter(is_active=True)
        
        # Filtreleri uygula
        if 'brand_id' in filters and filters['brand_id']:
            queryset = queryset.filter(brand_id=filters['brand_id'])
        if 'category_id' in filters and filters['category_id']:
            queryset = queryset.filter(category_id=filters['category_id'])
        if 'product_model_id' in filters and filters['product_model_id']:
            queryset = queryset.filter(product_model_id=filters['product_model_id'])
        if 'status' in filters and filters['status']:
            queryset = queryset.filter(status=filters['status'])
            
        # Varyant listesini döndür
        return queryset.order_by('-created_at')
    
    def get_or_create_variant(self, variant_id=None):
        if variant_id:
            try:
                variant = Variant.objects.get(id=variant_id)
                return variant
            except Variant.DoesNotExist:
                raise ObjectDoesNotExist(f"Variant ID {variant_id} bulunamadı.")
        else:
            # Yeni bir varyant oluşturma mantığı
            variant = Variant.objects.create()
            return variant
    

    @transaction.atomic
    def update_variant_with_hana_data(self, variant: Variant, token: str, variant_code: str) -> bool:
        try:
            logger.info(f"HANA veri güncelleme başlatıldı - Variant ID: {variant.id}, Code: {variant_code}")

            hana_data = fetch_hana_db_data(token, variant_code)
            if not hana_data["success"]:
                logger.error(f"HANA verisi alınamadı: {hana_data['error']}")
                return False

            hana_details = hana_data["data"]
            logger.debug(f"HANA'dan Gelen Detaylar: {hana_details}")

            # Güncelleme işlemini loglayın
            logger.debug(f"Güncelleme öncesi Variant: {variant.__dict__}")
            variant.sap_item_code = hana_details.get("sap_item_code", "")
            variant.sap_item_description = hana_details.get("sap_item_description", "")
            variant.sap_U_eski_bilesen_kod = hana_details.get("sap_U_eski_bilesen_kod", "")
            variant.sap_price = Decimal(hana_details.get("sap_price", 0))
            variant.sap_currency = hana_details.get("sap_currency", "")
            logger.debug(f"Güncelleme sonrası Variant: {variant.__dict__}")

            # Kaydet
            variant.save()
            logger.info(f"Variant başarıyla güncellendi - ID: {variant.id}")
            return True

        except Exception as e:
            logger.error(f"HANA güncelleme hatası - Variant ID: {variant.id}, Hata: {str(e)}")
            return False



