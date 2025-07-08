# backend/productconfig_simulator/services/simulated_variant_service.py
from django.db.models import Q, Count, Avg, Sum, Min, Max
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import logging

from ..models.simulated_variant import SimulatedVariant
from ..utils.variant_helpers import SimulatedVariantHelper
from .base_service import BaseService

logger = logging.getLogger(__name__)

class SimulatedVariantService(BaseService):
    """
    Simüle edilmiş varyantlar için servis sınıfı.
    """
    
    def __init__(self):
        super().__init__(SimulatedVariant)
        self.helper = SimulatedVariantHelper()
    
    def create_simulated_variant(self, simulation, product_model, variant_data):
        """
        Simüle edilmiş bir varyant oluşturur.
        
        Args:
            simulation: Simülasyon işi
            product_model: Ürün modeli
            variant_data (dict): Varyant verileri içeren sözlük
        
        Returns:
            SimulatedVariant: Oluşturulan simüle edilmiş varyant
        """
        if not variant_data.get('variant_code'):
            raise ValidationError("Varyant kodu gereklidir")
        
        # Temel varyant nesnesini oluştur
        variant = SimulatedVariant(
            simulation=simulation,
            product_model=product_model,
            variant_code=variant_data.get('variant_code'),
            variant_description=variant_data.get('variant_description', ''),
            total_price=variant_data.get('total_price', Decimal('0')),
            text_answers=variant_data.get('text_answers', {}),
            old_component_codes=variant_data.get('old_component_codes', [])
        )
        variant.save()
        
        # Seçilen seçenekleri ekle (varsa)
        selected_options = variant_data.get('selected_options', [])
        if selected_options:
            variant.selected_options.set(selected_options)
        
        logger.debug(f"Simüle edilmiş varyant oluşturuldu: ID={variant.id}, Kod={variant.variant_code}")
        return variant
    
    def get_variants_by_simulation(self, simulation_id):
        """Belirli bir simülasyona ait tüm varyantları döndürür"""
        return self.filter_by(simulation_id=simulation_id)
    
    def get_variants_by_product_model(self, product_model_id, simulation_id=None):
        """Belirli bir ürün modeline ait tüm varyantları döndürür"""
        if simulation_id:
            return self.filter_by(product_model_id=product_model_id, simulation_id=simulation_id)
        return self.filter_by(product_model_id=product_model_id)
    
    def get_variant_statistics(self, simulation_id):
        """
        Belirli bir simülasyon için varyant istatistiklerini hesaplar.
        """
        variants = self.get_variants_by_simulation(simulation_id)
        
        if not variants.exists():
            return {
                'total_count': 0,
                'price_info': {
                    'min': 0,
                    'max': 0,
                    'avg': 0,
                },
                'by_product_model': []
            }
        
        # Fiyat istatistikleri
        price_stats = variants.aggregate(
            min_price=Min('total_price'),
            max_price=Max('total_price'),
            avg_price=Avg('total_price')
        )
        
        # Ürün modeline göre gruplandırma
        model_stats = variants.values('product_model__name') \
            .annotate(
                count=Count('id'),
                min_price=Min('total_price'),
                max_price=Max('total_price'),
                avg_price=Avg('total_price')
            ).order_by('product_model__name')
        
        return {
            'total_count': variants.count(),
            'price_info': {
                'min': float(price_stats['min_price']) if price_stats['min_price'] else 0,
                'max': float(price_stats['max_price']) if price_stats['max_price'] else 0,
                'avg': float(price_stats['avg_price']) if price_stats['avg_price'] else 0,
            },
            'by_product_model': list(model_stats)
        }
    
    def compare_with_actual_variants(self, simulation_id, limit=100):
        """
        Simüle edilmiş varyantları gerçek varyantlarla karşılaştırır.
        
        Args:
            simulation_id: Simülasyon ID'si
            limit: Karşılaştırılacak maksimum varyant sayısı
            
        Returns:
            dict: Karşılaştırma sonuçlarını içeren sözlük
        """
        variants = self.get_variants_by_simulation(simulation_id)[:limit]
        comparison_results = []
        
        for variant in variants:
            comparison = variant.compare_with_actual()
            comparison_results.append({
                'simulated_variant_id': variant.id,
                'variant_code': variant.variant_code,
                'product_model': variant.product_model.name,
                'comparison_result': comparison
            })
        
        # Özeti hesapla
        total = len(comparison_results)
        exists_count = sum(1 for r in comparison_results if r['comparison_result'].get('exists', False))
        price_match_count = sum(1 for r in comparison_results 
                               if r['comparison_result'].get('exists', False) 
                               and r['comparison_result'].get('price_match', False))
        
        return {
            'summary': {
                'total_compared': total,
                'exists_in_actual': exists_count,
                'price_match': price_match_count,
                'exists_percentage': (exists_count / total) * 100 if total > 0 else 0,
                'price_match_percentage': (price_match_count / exists_count) * 100 if exists_count > 0 else 0,
            },
            'details': comparison_results
        }
    
    def bulk_create_variants(self, simulation, product_model, variant_data_list):
        """
        Toplu olarak simüle edilmiş varyantlar oluşturur.
        
        Args:
            simulation: Simülasyon işi
            product_model: Ürün modeli
            variant_data_list: Varyant verileri listesi
            
        Returns:
            int: Oluşturulan varyant sayısı
        """
        variants_to_create = []
        option_relations = []
        
        for variant_data in variant_data_list:
            if not variant_data.get('variant_code'):
                logger.warning(f"Varyant kodu eksik, bu varyant atlanıyor: {variant_data}")
                continue
            
            variant = SimulatedVariant(
                simulation=simulation,
                product_model=product_model,
                variant_code=variant_data.get('variant_code'),
                variant_description=variant_data.get('variant_description', ''),
                total_price=variant_data.get('total_price', Decimal('0')),
                text_answers=variant_data.get('text_answers', {}),
                old_component_codes=variant_data.get('old_component_codes', [])
            )
            variants_to_create.append(variant)
            
            # Seçenekleri ayrıca saklayalım, bulk_create sonrası ilişkilendirilecek
            selected_options = variant_data.get('selected_options', [])
            if selected_options:
                option_relations.append((variant, selected_options))
                
        # Toplu olarak varyantları oluştur
        created_variants = SimulatedVariant.objects.bulk_create(variants_to_create)
        
        # Seçenekleri ilişkilendir
        for idx, (variant, options) in enumerate(option_relations):
            if options:
                created_variants[idx].selected_options.set(options)
        
        logger.info(f"{len(created_variants)} adet simüle edilmiş varyant toplu olarak oluşturuldu")
        return len(created_variants)
    
    def export_variants_to_json(self, simulation_id, file_path=None):
        """
        Simüle edilmiş varyantları JSON formatında dışa aktarır.
        
        Args:
            simulation_id: Simülasyon ID'si
            file_path: Dosya yolu (None ise string olarak döndürür)
            
        Returns:
            str/None: JSON string veya None (dosyaya yazıldıysa)
        """
        variants = self.get_variants_by_simulation(simulation_id)
        
        # Varyantları dict formatına dönüştür
        variants_data = [variant.to_dict() for variant in variants]
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(variants_data, f, ensure_ascii=False, indent=2)
            return None
        
        return json.dumps(variants_data, ensure_ascii=False, indent=2)
    
    def export_variants_to_csv(self, simulation_id, file_path=None):
        """
        Simüle edilmiş varyantları CSV formatında dışa aktarır.
        
        Args:
            simulation_id: Simülasyon ID'si
            file_path: Dosya yolu (None ise string olarak döndürür)
            
        Returns:
            str/None: CSV string veya None (dosyaya yazıldıysa)
        """
        return self.helper.export_to_csv(
            self.get_variants_by_simulation(simulation_id), 
            file_path
        )