# backend/productconfig/utils/price_multiplier_helper.py
from decimal import Decimal
from typing import List, Dict, Tuple, Set
from django.db.models import QuerySet
from ..models import PriceMultiplierRule, Option
import logging

logger = logging.getLogger(__name__)

class PriceMultiplierHelper:
    def get_rules_for_option(self, option: Option) -> QuerySet[PriceMultiplierRule]:
        """Bir seçenek için geçerli tüm kuralları getirir."""
        return PriceMultiplierRule.objects.filter(
            target_options=option,
            is_active=True
        ).order_by('order')

    
    def evaluate_rules_for_variant(self, selected_option_ids: List[int]) -> Dict[int, Decimal]:
        # self parametresi eklendi
        """Seçili seçenekler için tüm kuralları değerlendirir."""
        multipliers = {}
        try:
            rules = PriceMultiplierRule.objects.filter(
                target_options__id__in=selected_option_ids,
                is_active=True
            ).prefetch_related('target_options')

            for rule in rules:
                is_triggered, multiplier = rule.evaluate(selected_option_ids)
                if is_triggered:
                    for target_option in rule.target_options.all():
                        current_multiplier = multipliers.get(target_option.id, Decimal('1.0'))
                        multipliers[target_option.id] = max(current_multiplier, multiplier)

        except Exception as e:
            logger.error(f"Kural değerlendirme hatası: {str(e)}")
            
        return multipliers
  
    def calculate_modified_price(self, option: Option, multiplier: Decimal) -> Decimal:
        # self parametresi eklendi
        """Seçeneğin fiyatını çarpan faktörüyle hesaplar."""
        base_price = Decimal(str(option.price_modifier))
        return base_price * multiplier

    
    def validate_rule_compatibility(self, rule: PriceMultiplierRule) -> Tuple[bool, str]:
        # self parametresi eklendi
        """Kuralın geçerliliğini kontrol eder."""
        try:
            # Minimum tetikleyici sayısı kontrolü
            trigger_count = rule.trigger_options.count()
            if trigger_count < rule.min_trigger_count:
                return False, f"En az {rule.min_trigger_count} tetikleyici seçenek gerekli"

            # Hedef seçeneğin tetikleyiciler arasında olmaması kontrolü
            for target_option in rule.target_options.all():
                if target_option in rule.trigger_options.all():
                    return False, f"Hedef seçenek '{target_option.name}' tetikleyiciler arasında olamaz"

            # Çarpan değeri kontrolü
            if rule.multiplier_factor <= 0:
                return False, "Çarpan değeri pozitif olmalı"

            return True, "Kural geçerli"

        except Exception as e:
            logger.error(f"Kural doğrulama hatası: {str(e)}")
            return False, f"Doğrulama hatası: {str(e)}"

    def get_applicable_rules(
        self, 
        selected_options: List[Option],
        target_option: Option
    ) -> List[PriceMultiplierRule]:
        """
        Seçili seçenekler ve hedef seçenek için uygulanabilir kuralları getirir.
        
        Args:
            selected_options: Seçili seçenekler listesi
            target_option: Hedef seçenek
            
        Returns:
            List[PriceMultiplierRule]: Uygulanabilir kurallar listesi
        """
        try:
            # Hedef seçenek için tüm aktif kuralları al
            rules = self.get_rules_for_option(target_option)
            
            # Seçili seçenek ID'lerini al
            selected_ids = [opt.id for opt in selected_options]
            
            # Her kuralı değerlendir
            applicable_rules = []
            for rule in rules:
                is_triggered, _ = rule.evaluate(selected_ids)
                if is_triggered:
                    applicable_rules.append(rule)
                    
            return applicable_rules

        except Exception as e:
            logger.error(f"Kural filtreleme hatası: {str(e)}")
            return []

    def get_active_multipliers(
        self, 
        selected_option_ids: List[int]
    ) -> Dict[int, List[Dict]]:
        """
        Seçili seçenekler için aktif çarpanları ve detaylarını getirir.
        
        Args:
            selected_option_ids: Seçili seçenek ID'leri
            
        Returns:
            Dict[int, List[Dict]]: {
                option_id: [{
                    'rule_name': str,
                    'multiplier': Decimal,
                    'triggered_by': List[str]
                }]
            }
        """
        active_multipliers = {}
        
        try:
            # Seçili seçeneklerle ilgili kuralları getir
            rules = PriceMultiplierRule.objects.filter(
                target_option__id__in=selected_option_ids,
                is_active=True
            ).select_related('target_option').prefetch_related('trigger_options')

            for rule in rules:
                is_triggered, multiplier = rule.evaluate(selected_option_ids)
                
                if is_triggered:
                    target_id = rule.target_option.id
                    if target_id not in active_multipliers:
                        active_multipliers[target_id] = []
                        
                    # Tetikleyen seçenek isimlerini al
                    triggered_by = [
                        opt.name for opt in rule.trigger_options.all()
                        if opt.id in selected_option_ids
                    ]
                    
                    active_multipliers[target_id].append({
                        'rule_name': rule.name,
                        'multiplier': multiplier,
                        'triggered_by': triggered_by
                    })

        except Exception as e:
            logger.error(f"Aktif çarpan getirme hatası: {str(e)}")
            
        return active_multipliers