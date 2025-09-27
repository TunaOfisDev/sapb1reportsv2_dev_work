# backend/productconfig_simulator/utils/simulator_helpers.py
from django.db.models import Count
import logging
from productconfig.models import (
    Brand, ProductGroup, Category, ProductModel, 
    Question, Option, DependentRule
)

logger = logging.getLogger(__name__)

class SimulationJobHelper:
    """
    SimulationJob modeli için yardımcı fonksiyonlar içeren sınıf.
    """
    
    def calculate_total_models(self, level, brand=None, product_group=None, category=None, product_model=None):
        """
        Belirtilen simülasyon seviyesine göre toplam model sayısını hesaplar.
        
        Args:
            level: Simülasyon seviyesi
            brand: Marka (opsiyonel)
            product_group: Ürün grubu (opsiyonel)
            category: Kategori (opsiyonel)
            product_model: Ürün modeli (opsiyonel)
            
        Returns:
            int: Toplam model sayısı
        """
        if level == 'product_model' and product_model:
            return 1
            
        if level == 'category' and category:
            return ProductModel.objects.filter(
                category=category, 
                is_active=True
            ).count()
            
        if level == 'product_group' and product_group:
            categories = Category.objects.filter(
                product_group=product_group, 
                is_active=True
            )
            return ProductModel.objects.filter(
                category__in=categories, 
                is_active=True
            ).count()
            
        if level == 'brand' and brand:
            product_groups = ProductGroup.objects.filter(
                brand=brand, 
                is_active=True
            )
            categories = Category.objects.filter(
                product_group__in=product_groups, 
                is_active=True
            )
            return ProductModel.objects.filter(
                category__in=categories, 
                is_active=True
            ).count()
            
        return 0
        
    def get_product_models_for_simulation(self, level, brand=None, product_group=None, category=None, product_model=None):
        """
        Simülasyon için ürün modellerini döndürür.
        
        Args:
            level: Simülasyon seviyesi
            brand: Marka (opsiyonel)
            product_group: Ürün grubu (opsiyonel)
            category: Kategori (opsiyonel)
            product_model: Ürün modeli (opsiyonel)
            
        Returns:
            QuerySet: Ürün modelleri queryset'i
        """
        if level == 'product_model' and product_model:
            return ProductModel.objects.filter(id=product_model.id, is_active=True)
            
        if level == 'category' and category:
            return ProductModel.objects.filter(
                category=category, 
                is_active=True
            )
            
        if level == 'product_group' and product_group:
            categories = Category.objects.filter(
                product_group=product_group, 
                is_active=True
            )
            return ProductModel.objects.filter(
                category__in=categories, 
                is_active=True
            )
            
        if level == 'brand' and brand:
            product_groups = ProductGroup.objects.filter(
                brand=brand, 
                is_active=True
            )
            categories = Category.objects.filter(
                product_group__in=product_groups, 
                is_active=True
            )
            return ProductModel.objects.filter(
                category__in=categories, 
                is_active=True
            )
            
        return ProductModel.objects.none()
        
    def check_model_data_quality(self, product_model):
        """
        Bir ürün modelinin veri kalitesini kontrol eder.
        
        Args:
            product_model: Kontrol edilecek ürün modeli
            
        Returns:
            dict: Kontrol sonuçlarını içeren sözlük
        """
        results = {
            'model_id': product_model.id,
            'model_name': product_model.name,
            'question_count': 0,
            'option_count': 0,
            'missing_options': [],
            'dependent_rule_issues': [],
            'is_valid': True
        }
        
        # Ürün modeline ait soruları getir
        questions = Question.objects.filter(
            applicable_product_models=product_model,
            is_active=True
        )
        results['question_count'] = questions.count()
        
        # Her soru için kontrol yap
        for question in questions:
            # Soruya ait seçenekleri kontrol et
            options = Option.objects.filter(
                question_option_relations__question=question,
                applicable_product_models=product_model,
                is_active=True
            )
            
            # Seçenek yoksa hata kaydı
            if options.count() == 0 and question.question_type != 'text_input':
                results['missing_options'].append({
                    'question_id': question.id,
                    'question_name': question.name,
                    'question_type': question.question_type
                })
                results['is_valid'] = False
                
            # Seçenek sayısını toplam sayaca ekle
            results['option_count'] += options.count()
            
            # Bağımlı kuralları kontrol et
            dependent_rules = DependentRule.objects.filter(
                parent_question=question,
                is_active=True
            )
            
            for rule in dependent_rules:
                # Kural geçerli mi kontrol et
                rule_valid = True
                issues = []
                
                # Tetikleyici seçenek uygun mu?
                if not rule.trigger_option.is_applicable_for_variant(product_model):
                    rule_valid = False
                    issues.append("Tetikleyici seçenek bu ürün modeli için uygun değil")
                
                # Bağımlı sorular uygun mu?
                for dep_question in rule.dependent_questions.all():
                    if not dep_question.is_applicable_for_variant(product_model):
                        rule_valid = False
                        issues.append(f"Bağımlı soru '{dep_question.name}' bu ürün modeli için uygun değil")
                
                if not rule_valid:
                    results['dependent_rule_issues'].append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'parent_question': question.name,
                        'issues': issues
                    })
                    results['is_valid'] = False
        
        return results
        
    def estimate_simulation_time(self, product_model_count, max_variants_per_model):
        """
        Simülasyon için tahmini süreyi hesaplar.
        
        Args:
            product_model_count: İşlenecek ürün modeli sayısı
            max_variants_per_model: Model başına maksimum varyant sayısı
            
        Returns:
            dict: Tahmini süre bilgilerini içeren sözlük
        """
        # Tahmini süreler (saniye cinsinden)
        # Bu değerler gerçek ölçümlere göre ayarlanmalıdır
        base_time_per_model = 5  # Temel süre 
        time_per_variant = 0.1  # Her varyant için eklenecek süre
        
        # Toplam tahmini süre (saniye)
        estimated_seconds = base_time_per_model * product_model_count
        estimated_seconds += time_per_variant * product_model_count * max_variants_per_model
        
        # Dakika ve saat hesabı
        minutes, seconds = divmod(estimated_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        return {
            'estimated_seconds': estimated_seconds,
            'estimated_time_str': f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            'model_count': product_model_count,
            'max_variants_per_model': max_variants_per_model
        }