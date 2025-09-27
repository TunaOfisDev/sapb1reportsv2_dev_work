# backend/productconfig_simulator/utils/variant_helpers.py
import csv
import io
import json
import logging
from datetime import datetime
from decimal import Decimal

from django.db.models import QuerySet
from productconfig.models import (
    Variant, Option, Question, DependentRule, 
    ConditionalOption, ProductModel
)
from productconfig.utils import VariantHelper

logger = logging.getLogger(__name__)

class SimulatedVariantHelper:
    """
    SimulatedVariant modeli için yardımcı fonksiyonlar içeren sınıf.
    """
    
    def generate_variants_for_model(self, product_model, max_variants=1000, 
                                     include_dependent_rules=True,
                                     include_conditional_options=True,
                                     include_price_multipliers=True):
        """
        Belirli bir ürün modeli için tüm olası varyantları oluşturur.
        
        Args:
            product_model: Ürün modeli
            max_variants: Maksimum varyant sayısı
            include_dependent_rules: Bağımlı kurallar dahil edilsin mi
            include_conditional_options: Koşullu seçenekler dahil edilsin mi
            include_price_multipliers: Fiyat çarpanları dahil edilsin mi
            
        Returns:
            list: Varyant verileri listesi
        """
        # Ürün modeline ait soruları getir
        questions = Question.objects.filter(
            applicable_product_models=product_model,
            is_active=True
        ).order_by('order')

        # İlk soruya özel işlem (Proje Nedir için)
        first_question = questions.first()
        if first_question and first_question.name == "Proje Nedir":
            # Varsayılan bir proje adı ata
            initial_text = f"Simülasyon Projesi {datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # initial_answers yoksa oluştur
            if not initial_answers:
                initial_answers = {}
            
            # İlk sorunun cevabını ekle
            initial_answers[str(first_question.id)] = {
                "question_id": first_question.id,
                "answer_text": initial_text
            }
        
        # Soruları ve olası cevapları hazırla
        question_options_map = {}
        for question in questions:
            if question.question_type == 'text_input':
                # Metin girişi soruları için varsayılan değer
                question_options_map[question.id] = ["Default Text"]
            else:
                # Seçenek soruları için uygun seçenekleri getir
                options = Option.objects.filter(
                    question_option_relations__question=question,
                    applicable_product_models=product_model,
                    is_active=True
                )
                
                if options.exists():
                    question_options_map[question.id] = list(options)
                else:
                    # Seçenek yoksa hata logu
                    logger.warning(f"Soru {question.id} ({question.name}) için uygun seçenek bulunamadı")
                    question_options_map[question.id] = []
        
        # Üretilecek varyantları sakla
        variants = []
        variant_count = 0
        
        # Recursive olarak varyantları oluştur
        def build_variants(current_question_idx=0, answers=None, selected_options=None):
            nonlocal variant_count
            
            if answers is None:
                answers = {}
            if selected_options is None:
                selected_options = []
                
            # Maksimum varyant sayısına ulaşıldı mı kontrol et
            if variant_count >= max_variants:
                return
                
            # Tüm sorular cevaplandı, varyantı kaydet
            if current_question_idx >= len(questions):
                variant_data = self._create_variant_data(
                    product_model, answers, selected_options,
                    include_price_multipliers=include_price_multipliers
                )
                variants.append(variant_data)
                variant_count += 1
                return
                
            current_question = questions[current_question_idx]

            # İlk soru için özel işlem (Proje Nedir)
            if current_question_idx == 0 and current_question.name == "Proje Nedir":
                project_name = f"Simülasyon Projesi {datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_answers = answers.copy() if answers else {}
                new_answers[str(current_question.id)] = {
                    "question_id": current_question.id,
                    "answer_text": project_name
                }
                # Sonraki soruya geç
                build_variants(current_question_idx + 1, new_answers, selected_options)
                return
            
            # Eğer bağımlı kurallar dahil edilecekse soru görünür mü kontrol et
            if include_dependent_rules and not self._is_question_visible(current_question, answers):
                # Görünmüyorsa sonraki soruya geç
                build_variants(current_question_idx + 1, answers, selected_options)
                return
                
            # Soru için olası seçenekleri al
            possible_options = question_options_map.get(current_question.id, [])
            
            # Koşullu seçenekleri dahil et
            if include_conditional_options:
                conditional_options = self._get_conditional_options(
                    current_question, selected_options
                )
                possible_options.extend(conditional_options)
            
            # Seçenek yoksa veya metin girişi ise
            if not possible_options or current_question.question_type == 'text_input':
                # Metin girişi için varsayılan değer
                if current_question.question_type == 'text_input':
                    text_value = f"Text for Question {current_question.id}"
                    new_answers = answers.copy()
                    new_answers[str(current_question.id)] = {
                        "question_id": current_question.id,
                        "answer_text": text_value
                    }
                    # Sonraki soruya geç
                    build_variants(current_question_idx + 1, new_answers, selected_options)
                else:
                    # Seçenek yoksa sonraki soruya geç
                    build_variants(current_question_idx + 1, answers, selected_options)
                return
                
            # Tekli seçim soruları
            if current_question.question_type == 'choice':
                for option in possible_options:
                    new_answers = answers.copy()
                    new_selected_options = selected_options.copy()
                    
                    new_answers[str(current_question.id)] = {
                        "question_id": current_question.id,
                        "answer_id": option.id,
                        "answer_text": option.name
                    }
                    new_selected_options.append(option)
                    
                    # Sonraki soruya geç
                    build_variants(current_question_idx + 1, new_answers, new_selected_options)
                    
            # Çoklu seçim soruları (sadece ilk seçeneği seç basitlik için)
            elif current_question.question_type == 'multiple_choice':
                # Performans için sadece tek bir seçenek seçiyoruz
                # Gerçek simülasyonda tüm kombinasyonlar değerlendirilmelidir
                if possible_options:
                    option = possible_options[0]
                    new_answers = answers.copy()
                    new_selected_options = selected_options.copy()
                    
                    new_answers[str(current_question.id)] = {
                        "question_id": current_question.id,
                        "answer_ids": [option.id],
                        "answer_texts": [option.name]
                    }
                    new_selected_options.append(option)
                    
                    # Sonraki soruya geç
                    build_variants(current_question_idx + 1, new_answers, new_selected_options)
                else:
                    # Seçenek yoksa sonraki soruya geç
                    build_variants(current_question_idx + 1, answers, selected_options)
        
        # Varyant oluşturmayı başlat
        build_variants()
        
        return variants
        
    def _create_variant_data(self, product_model, answers, selected_options, include_price_multipliers=True):
        """
        Varyant verilerini oluşturur.
        
        Args:
            product_model: Ürün modeli
            answers: Soru yanıtları
            selected_options: Seçilen seçenekler
            include_price_multipliers: Fiyat çarpanları dahil edilsin mi
            
        Returns:
            dict: Varyant verileri
        """
        # Gerçek variant oluşturma mantığını simüle et
        mock_variant = self._create_mock_variant(product_model, answers, selected_options)
        
        # Varyant kodu oluştur
        variant_code = VariantHelper.format_variant_code(mock_variant)
        
        # Varyant açıklaması oluştur
        variant_description = VariantHelper.update_variant_description(mock_variant)
        
        # Toplam fiyatı hesapla
        base_price = product_model.base_price or Decimal('0')
        
        # Seçenek fiyatları toplamı
        option_prices = Decimal('0')
        for option in selected_options:
            option_prices += option.price_modifier
        
        # Fiyat çarpanları (simülasyon için basitleştirilmiş)
        total_price = base_price + option_prices
        
        if include_price_multipliers:
            # Gerçek fiyat çarpanlarını uygulamak için
            # PriceMultiplierService kullanılabilir
            pass
        
        # Eski bileşen kodları (simüle edilmiş)
        old_component_codes = [f"OCC-{product_model.id}-{datetime.now().strftime('%Y%m%d')}"]
        
        return {
            'product_model': product_model,
            'variant_code': variant_code,
            'variant_description': variant_description,
            'total_price': total_price,
            'text_answers': answers,
            'selected_options': [option.id for option in selected_options],
            'old_component_codes': old_component_codes
        }
        
    def _create_mock_variant(self, product_model, answers, selected_options):
        """
        Simülasyon için sahte bir varyant nesnesi oluşturur.
        Bu nesne gerçek veritabanına kaydedilmez.
        
        Args:
            product_model: Ürün modeli
            answers: Soru yanıtları
            selected_options: Seçilen seçenekler
            
        Returns:
            Variant: Sahte varyant nesnesi
        """
        variant = Variant(
            product_model=product_model,
            text_answers=answers
        )
        
        # options ManyToMany alanını simüle edemeyiz, 
        # bu yüzden bir dizi olarak ele alırız
        variant.options = selected_options
        
        return variant
        
    def _is_question_visible(self, question, answers):
        """
        Belirli bir yanıt kümesi için sorunun görünür olup olmadığını kontrol eder.
        
        Args:
            question: Kontrol edilecek soru
            answers: Mevcut soru yanıtları
            
        Returns:
            bool: Soru görünür mü
        """
        # Bağımlı kuralları getir
        dependent_rules = DependentRule.objects.filter(
            dependent_questions=question,
            is_active=True
        )
        
        # Kural yoksa her zaman görünür
        if not dependent_rules.exists():
            return True
            
        # Her kural için kontrol et
        for rule in dependent_rules:
            parent_question_id = str(rule.parent_question.id)
            
            # Eğer üst soru henüz cevaplanmamışsa
            if parent_question_id not in answers:
                continue
                
            parent_answer = answers[parent_question_id]
            
            # answer_id kontrolü
            if 'answer_id' in parent_answer:
                answer_id = parent_answer['answer_id']
                
                # Kural türüne göre değerlendir
                if rule.rule_type == 'show_on_option':
                    if answer_id == rule.trigger_option.id:
                        return True
                elif rule.rule_type == 'hide_on_option':
                    if answer_id == rule.trigger_option.id:
                        return False
            
            # answer_ids kontrolü (çoklu seçim)
            elif 'answer_ids' in parent_answer:
                answer_ids = parent_answer['answer_ids']
                
                # Kural türüne göre değerlendir
                if rule.rule_type == 'show_on_option':
                    if rule.trigger_option.id in answer_ids:
                        return True
                elif rule.rule_type == 'hide_on_option':
                    if rule.trigger_option.id in answer_ids:
                        return False
        
        # SHOW_ON_OPTION kuralları için, hiçbir kural tetiklenmezse görünmez
        # HIDE_ON_OPTION kuralları için, hiçbir kural tetiklenmezse görünür
        default_visibility = any(
            rule.rule_type == 'hide_on_option' 
            for rule in dependent_rules
        )
        
        return default_visibility
        
    def _get_conditional_options(self, question, selected_options):
        """
        Seçilen seçeneklere göre koşullu seçenekleri döndürür.
        
        Args:
            question: Hedef soru
            selected_options: Seçilen seçenekler
            
        Returns:
            list: Koşullu seçenekler listesi
        """
        selected_option_ids = [option.id for option in selected_options]
        
        # Koşullu seçenekleri getir
        conditional_options = ConditionalOption.objects.filter(
            target_question=question,
            is_active=True
        )
        
        applicable_options = []
        
        for cond_option in conditional_options:
            # Tetikleyici seçenekler seçilmiş mi kontrol et
            trigger1_selected = cond_option.trigger_option_1.id in selected_option_ids
            trigger2_selected = cond_option.trigger_option_2.id in selected_option_ids
            
            # Lojik operatöre göre değerlendir
            is_triggered = False
            if cond_option.logical_operator == "AND":
                is_triggered = trigger1_selected and trigger2_selected
            else:  # OR
                is_triggered = trigger1_selected or trigger2_selected
                
            # Tetiklenmişse seçenekleri ekle
            if is_triggered:
                applicable_options.extend(cond_option.applicable_options.all())
                
                # OVERRIDE modu ise diğer koşullu seçenekleri dikkate alma
                if cond_option.display_mode == 'override':
                    break
                    
        return applicable_options
        
    def export_to_csv(self, variants, file_path=None):
        """
        Varyantları CSV formatında dışa aktarır.
        
        Args:
            variants: Varyant queryset veya listesi
            file_path: Dosya yolu (None ise string olarak döndürür)
            
        Returns:
            str/None: CSV string veya None (dosyaya yazıldıysa)
        """
        if not variants:
            return None
            
        if isinstance(variants, QuerySet) and not variants.exists():
            return None
            
        # CSV dosyası için bellek tamponunu ayarla
        output = io.StringIO() if file_path is None else None
        
        # CSV dosyasını aç
        if file_path:
            csvfile = open(file_path, 'w', newline='', encoding='utf-8')
        else:
            csvfile = output
            
        # CSV yazıcısını hazırla
        writer = csv.writer(csvfile)
        
        # Başlık satırını yaz
        writer.writerow([
            'ID', 'Ürün Modeli', 'Varyant Kodu', 'Varyant Açıklaması',
            'Toplam Fiyat', 'Eski Bileşen Kodları', 'Oluşturulma Zamanı'
        ])
        
        # Varyant verilerini yaz
        for variant in variants:
            writer.writerow([
                variant.id,
                variant.product_model.name,
                variant.variant_code,
                variant.variant_description,
                variant.total_price,
                ', '.join(variant.old_component_codes) if isinstance(variant.old_component_codes, list) else variant.old_component_codes,
                variant.created_at.strftime('%Y-%m-%d %H:%M:%S') if variant.created_at else ''
            ])
            
        # Dosya işlemlerini tamamla
        if file_path:
            csvfile.close()
            return None
        else:
            return output.getvalue()