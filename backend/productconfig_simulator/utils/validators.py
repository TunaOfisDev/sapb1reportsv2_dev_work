# backend/productconfig_simulator/utils/validators.py
import json
import logging
from django.db.models import Q
from django.core.exceptions import ValidationError
from productconfig.models import (
    Brand, ProductGroup, Category, ProductModel, 
    Question, Option, DependentRule, ConditionalOption
)

logger = logging.getLogger(__name__)

def validate_simulation_data(data):
    """
    Simülasyon oluşturma verilerini doğrular.
    
    Args:
        data: Simülasyon verileri sözlüğü
        
    Returns:
        dict: Doğrulanmış veriler
        
    Raises:
        ValidationError: Doğrulama hatası olursa
    """
    # Zorunlu alanlar
    if 'level' not in data:
        raise ValidationError("Simülasyon seviyesi (level) belirtilmelidir.")
    
    level = data.get('level')
    
    # Seviye geçerliliği
    valid_levels = ['brand', 'product_group', 'category', 'product_model']
    if level not in valid_levels:
        raise ValidationError(f"Geçersiz simülasyon seviyesi. Geçerli değerler: {', '.join(valid_levels)}")
    
    # Seviyeye göre zorunlu alanlar
    if level == 'brand' and 'brand' not in data:
        raise ValidationError("Marka seviyesinde simülasyon için 'brand' belirtilmelidir.")
        
    if level == 'product_group' and 'product_group' not in data:
        raise ValidationError("Ürün grubu seviyesinde simülasyon için 'product_group' belirtilmelidir.")
        
    if level == 'category' and 'category' not in data:
        raise ValidationError("Kategori seviyesinde simülasyon için 'category' belirtilmelidir.")
        
    if level == 'product_model' and 'product_model' not in data:
        raise ValidationError("Ürün modeli seviyesinde simülasyon için 'product_model' belirtilmelidir.")
    
    # Sayısal değerler
    max_variants = data.get('max_variants_per_model', 1000)
    if not isinstance(max_variants, int) or max_variants <= 0:
        raise ValidationError("'max_variants_per_model' pozitif bir tam sayı olmalıdır.")
    
    # Boolean değerler
    for field in ['include_dependent_rules', 'include_conditional_options', 'include_price_multipliers']:
        if field in data and not isinstance(data[field], bool):
            raise ValidationError(f"'{field}' bir boolean değer olmalıdır.")
    
    return data


def validate_product_model_for_simulation(product_model):
    """
    Bir ürün modelinin simülasyon için uygunluğunu kontrol eder.
    
    Args:
        product_model: Kontrol edilecek ürün modeli
        
    Returns:
        dict: Doğrulama sonuçlarını içeren sözlük
    """
    results = {
        'is_valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Ürün modeline ait soruları getir
    questions = Question.objects.filter(
        applicable_product_models=product_model,
        is_active=True
    )
    
    # Soru sayısını kontrol et
    if questions.count() == 0:
        results['is_valid'] = False
        results['errors'].append("Bu ürün modeli için tanımlanmış soru bulunmuyor.")
        return results
    
    # Her soru için kontrol
    for question in questions:
        # Seçenek kontrolü (text_input hariç)
        if question.question_type != 'text_input':
            options = Option.objects.filter(
                question_option_relations__question=question,
                applicable_product_models=product_model,
                is_active=True
            )
            
            if options.count() == 0:
                results['is_valid'] = False
                results['errors'].append(f"Soru '{question.name}' (ID: {question.id}) için uygun seçenek bulunamadı.")
    
    # Bağımlı kuralları kontrol et
    dependent_rules = DependentRule.objects.filter(
        is_active=True
    ).filter(
        Q(parent_question__applicable_product_models=product_model) |
        Q(dependent_questions__applicable_product_models=product_model)
    ).distinct()
    
    for rule in dependent_rules:
        # Ana soru uygun mu?
        if not rule.parent_question.is_applicable_for_variant(product_model):
            results['warnings'].append(
                f"Bağımlı kural '{rule.name}' (ID: {rule.id}) için ana soru '{rule.parent_question.name}' "
                f"bu ürün modeli için uygun değil."
            )
        
        # Tetikleyici seçenek uygun mu?
        if not rule.trigger_option.is_applicable_for_variant(product_model):
            results['warnings'].append(
                f"Bağımlı kural '{rule.name}' (ID: {rule.id}) için tetikleyici seçenek '{rule.trigger_option.name}' "
                f"bu ürün modeli için uygun değil."
            )
        
        # Bağımlı sorular uygun mu?
        for dep_question in rule.dependent_questions.all():
            if not dep_question.is_applicable_for_variant(product_model):
                results['warnings'].append(
                    f"Bağımlı kural '{rule.name}' (ID: {rule.id}) için bağımlı soru '{dep_question.name}' "
                    f"bu ürün modeli için uygun değil."
                )
    
    # Koşullu seçenekleri kontrol et
    conditional_options = ConditionalOption.objects.filter(
        is_active=True,
        target_question__applicable_product_models=product_model
    )
    
    for cond_option in conditional_options:
        # Tetikleyici seçenekler uygun mu?
        if not cond_option.trigger_option_1.is_applicable_for_variant(product_model):
            results['warnings'].append(
                f"Koşullu seçenek '{cond_option.name}' (ID: {cond_option.id}) için tetikleyici seçenek 1 "
                f"'{cond_option.trigger_option_1.name}' bu ürün modeli için uygun değil."
            )
            
        if not cond_option.trigger_option_2.is_applicable_for_variant(product_model):
            results['warnings'].append(
                f"Koşullu seçenek '{cond_option.name}' (ID: {cond_option.id}) için tetikleyici seçenek 2 "
                f"'{cond_option.trigger_option_2.name}' bu ürün modeli için uygun değil."
            )
    
    # Uygulanabilir seçenek kontrolü
    if results['is_valid'] and len(results['warnings']) > 0:
        results['is_valid'] = True  # Uyarılar olsa bile geçerli kabul edilir
        
    return results


def validate_variant_data(variant_data):
    """
    Simüle edilmiş varyant verilerini doğrular.
    
    Args:
        variant_data: Varyant verileri sözlüğü
        
    Returns:
        dict: Doğrulanmış veriler
        
    Raises:
        ValidationError: Doğrulama hatası olursa
    """
    # Zorunlu alanlar
    required_fields = ['product_model', 'variant_code', 'text_answers']
    for field in required_fields:
        if field not in variant_data:
            raise ValidationError(f"'{field}' alanı belirtilmelidir.")
    
    # Varyant kodu kontrolü
    if not variant_data.get('variant_code'):
        raise ValidationError("Varyant kodu boş olamaz.")
    
    # Product model nesnesi mi kontrolü
    if not isinstance(variant_data.get('product_model'), ProductModel):
        raise ValidationError("'product_model' geçerli bir ProductModel nesnesi olmalıdır.")
    
    # text_answers sözlük mü kontrolü
    text_answers = variant_data.get('text_answers')
    if not isinstance(text_answers, dict):
        raise ValidationError("'text_answers' bir sözlük olmalıdır.")
    
    # Seçenek listesi kontrolü
    selected_options = variant_data.get('selected_options', [])
    if not isinstance(selected_options, list):
        raise ValidationError("'selected_options' bir liste olmalıdır.")
    
    # Eski bileşen kodları kontrolü
    old_component_codes = variant_data.get('old_component_codes', [])
    if not isinstance(old_component_codes, list):
        raise ValidationError("'old_component_codes' bir liste olmalıdır.")
    
    return variant_data