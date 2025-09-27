# backend/productconfig/services/price_multiplier_service.py
from decimal import Decimal
from typing import List, Dict, Optional
from django.core.exceptions import ValidationError
from ..models import PriceMultiplierRule, Option, Variant
from ..utils.price_multiplier_helper import PriceMultiplierHelper
import logging

logger = logging.getLogger(__name__)

class PriceMultiplierService:
    """
    Fiyat çarpan kurallarının yönetimi ve hesaplamaları için servis sınıfı.
    """
    
    def __init__(self):
        self.helper = PriceMultiplierHelper()

    def create_price_multiplier_rule(
        self,
        name: str,
        target_option_ids: List[int],
        trigger_option_ids: List[int],
        multiplier_factor: Decimal,
        logical_operator: str = 'and',
        min_trigger_count: int = 1,
        description: str = ''
    ) -> Optional[PriceMultiplierRule]:
        """
        Yeni bir fiyat çarpan kuralı oluşturur.
        """
        try:
            # Yeni kural oluştur
            rule = PriceMultiplierRule.objects.create(
                name=name,
                multiplier_factor=multiplier_factor,
                logical_operator=logical_operator,
                min_trigger_count=min_trigger_count,
                description=description
            )
            
            # Hedef ve tetikleyici seçenekleri ekle
            target_options = Option.objects.filter(id__in=target_option_ids)
            trigger_options = Option.objects.filter(id__in=trigger_option_ids)
            rule.target_options.set(target_options)
            rule.trigger_options.set(trigger_options)
            
            # Kuralı doğrula
            is_valid, message = self.helper.validate_rule_compatibility(rule)
            if not is_valid:
                rule.delete()
                raise ValidationError(message)
                
            logger.info(f"Yeni fiyat çarpan kuralı oluşturuldu - ID: {rule.id}")
            return rule

        except Option.DoesNotExist:
            logger.error("Seçeneklerden biri bulunamadı.")
            return None
        except Exception as e:
            logger.error(f"Kural oluşturma hatası: {str(e)}")
            return None

    def update_price_multiplier_rule(
        self,
        rule_id: int,
        data: dict
    ) -> Optional[PriceMultiplierRule]:
        """
        Mevcut bir fiyat çarpan kuralını günceller.
        """
        try:
            rule = PriceMultiplierRule.objects.get(id=rule_id)
            
            # Temel alanları güncelle
            for field, value in data.items():
                if field not in ['trigger_options', 'target_options']:
                    setattr(rule, field, value)
            
            # Tetikleyici ve hedef seçenekleri güncelle
            if 'trigger_options' in data:
                rule.trigger_options.set(data['trigger_options'])
            if 'target_options' in data:
                rule.target_options.set(data['target_options'])
            
            # Kuralı doğrula
            is_valid, message = self.helper.validate_rule_compatibility(rule)
            if not is_valid:
                raise ValidationError(message)
                
            rule.save()
            logger.info(f"Fiyat çarpan kuralı güncellendi - ID: {rule.id}")
            return rule

        except PriceMultiplierRule.DoesNotExist:
            logger.error(f"Kural bulunamadı - ID: {rule_id}")
            return None
        except Exception as e:
            logger.error(f"Kural güncelleme hatası: {str(e)}")
            return None

    def calculate_option_price(
        self,
        option: Option,
        selected_option_ids: List[int]
    ) -> Decimal:
        """
        Seçeneğin güncel fiyatını çarpan kurallarını uygulayarak hesaplar.
        """
        try:
            rules = self.helper.get_rules_for_option(option)
            max_multiplier = Decimal('1.0')
            
            for rule in rules:
                is_triggered, multiplier = rule.evaluate(selected_option_ids)
                if is_triggered:
                    max_multiplier = max(max_multiplier, multiplier)
            
            return self.helper.calculate_modified_price(option, max_multiplier)

        except Exception as e:
            logger.error(f"Fiyat hesaplama hatası - Option ID {option.id}: {str(e)}")
            return Decimal('0')

    def get_multiplier_details(
        self,
        option: Option,
        selected_option_ids: List[int]
    ) -> Dict:
        """
        Seçenek için aktif çarpan kurallarının detaylarını getirir.
        """
        details = {
            'base_price': option.price_modifier,
            'rules': [],
            'final_multiplier': Decimal('1.0'),
            'final_price': option.price_modifier
        }
        
        try:
            rules = self.helper.get_rules_for_option(option)
            
            for rule in rules:
                is_triggered, multiplier = rule.evaluate(selected_option_ids)
                if is_triggered:
                    details['rules'].append({
                        'rule_name': rule.name,
                        'multiplier': multiplier,
                        'triggered_by': [
                            opt.name for opt in rule.trigger_options.all()
                            if opt.id in selected_option_ids
                        ]
                    })
                    details['final_multiplier'] = max(
                        details['final_multiplier'], 
                        multiplier
                    )
            
            details['final_price'] = self.helper.calculate_modified_price(
                option, 
                details['final_multiplier']
            )

        except Exception as e:
            logger.error(f"Çarpan detayları alma hatası - Option ID {option.id}: {str(e)}")
            
        return details

    def calculate_variant_prices(
        self,
        variant: Variant
    ) -> Dict[int, Decimal]:
        """
        Varyant için tüm seçeneklerin güncel fiyatlarını hesaplar.
        """
        try:
            selected_option_ids = list(variant.options.values_list('id', flat=True))
            final_prices = {}
            
            for option in variant.options.all():
                final_prices[option.id] = self.calculate_option_price(
                    option,
                    selected_option_ids
                )
            
            return final_prices

        except Exception as e:
            logger.error(f"Varyant fiyat hesaplama hatası - Variant ID {variant.id}: {str(e)}")
            return {}

    def validate_and_get_conflicts(
        self,
        rule: PriceMultiplierRule
    ) -> List[Dict]:
        """
        Kural çakışmalarını kontrol eder ve raporlar.
        """
        conflicts = []
        
        try:
            existing_rules = PriceMultiplierRule.objects.filter(
                target_options__in=rule.target_options.all(),
                is_active=True
            ).exclude(id=rule.id)
            
            for existing_rule in existing_rules:
                trigger_intersection = set(existing_rule.trigger_options.all()) & set(rule.trigger_options.all())
                
                if trigger_intersection:
                    conflicts.append({
                        'rule_id': existing_rule.id,
                        'rule_name': existing_rule.name,
                        'conflict_type': 'trigger_overlap',
                        'conflict_details': {
                            'overlapping_options': [opt.name for opt in trigger_intersection]
                        }
                    })

        except Exception as e:
            logger.error(f"Kural çakışma kontrolü hatası: {str(e)}")
            
        return conflicts

    def delete_rule(self, rule_id: int) -> bool:
        """
        Fiyat çarpan kuralını siler.
        """
        try:
            rule = PriceMultiplierRule.objects.get(id=rule_id)
            rule.delete()
            logger.info(f"Fiyat çarpan kuralı silindi - ID: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Kural silme hatası - Rule ID {rule_id}: {str(e)}")
            return False
