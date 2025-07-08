# backend\productconfig\services\old_component_code_service.py
from typing import Dict
from ..models import Variant, OldComponentCode
from ..utils.old_component_code_helper import OldComponentCodeHelper
import logging

logger = logging.getLogger(__name__)

class OldComponentCodeService:
    """
    Eski bileşen kodlarının oluşturulması ve yönetilmesi için servis sınıfı.
    """

    def __init__(self):
        self.helper = OldComponentCodeHelper()

    def generate_codes(self, variant_id: int) -> Dict:
        """
        Bir variant için eski bileşen kodlarını oluşturur.
        
        Args:
            variant_id: Variant'ın ID'si
        
        Returns:
            Dict: Kod oluşturma sonuçları
        """
        try:
            # Variant nesnesini al
            variant = Variant.objects.get(id=variant_id)

            # Eski bileşen kodlarını oluştur
            codes = self.helper.get_old_component_codes(variant)

            logger.info(f"Eski bileşen kodları oluşturuldu - Variant ID: {variant_id}, Kodlar: {codes}")
            return {
                'status': 'success',
                'variant_id': variant_id,
                'codes': codes
            }

        except Variant.DoesNotExist:
            logger.error(f"Variant bulunamadı - ID: {variant_id}")
            return {
                'status': 'error',
                'message': f"Variant bulunamadı - ID: {variant_id}"
            }
        except Exception as e:
            logger.error(f"Kod oluşturma hatası - Variant ID: {variant_id}, Hata: {str(e)}")
            return {
                'status': 'error',
                'message': f"Kod oluşturma hatası: {str(e)}"
            }

    def prepare_api_response(self, variant_id: int) -> Dict:
        """
        Bir variant için API yanıtını hazırlar.
        
        Args:
            variant_id: Variant'ın ID'si
        
        Returns:
            Dict: API için hazırlanmış yanıt
        """
        try:
            # Variant nesnesini al
            variant = Variant.objects.get(id=variant_id)

            # API için verileri hazırla
            api_response = self.helper.prepare_for_rest_api(variant)

            logger.info(f"API yanıtı hazırlandı - Variant ID: {variant_id}")
            return {
                'status': 'success',
                'data': api_response
            }

        except Variant.DoesNotExist:
            logger.error(f"Variant bulunamadı - ID: {variant_id}")
            return {
                'status': 'error',
                'message': f"Variant bulunamadı - ID: {variant_id}"
            }
        except Exception as e:
            logger.error(f"API yanıtı hazırlama hatası - Variant ID: {variant_id}, Hata: {str(e)}")
            return {
                'status': 'error',
                'message': f"API yanıtı hazırlama hatası: {str(e)}"
            }

    def get_rule_details(self, variant_id: int) -> Dict:
        """
        Bir variant için uygun kuralların detaylarını döndürür.
        
        Args:
            variant_id: Variant'ın ID'si
        
        Returns:
            Dict: Kurallar ve detaylar
        """
        try:
            # Variant nesnesini al
            variant = Variant.objects.get(id=variant_id)

            # Bileşen detaylarını al
            rule_details = self.helper.get_component_details(variant)

            logger.info(f"Variant için kural detayları alındı - Variant ID: {variant_id}")
            return {
                'status': 'success',
                'data': rule_details
            }

        except Variant.DoesNotExist:
            logger.error(f"Variant bulunamadı - ID: {variant_id}")
            return {
                'status': 'error',
                'message': f"Variant bulunamadı - ID: {variant_id}"
            }
        except Exception as e:
            logger.error(f"Kural detaylarını alma hatası - Variant ID: {variant_id}, Hata: {str(e)}")
            return {
                'status': 'error',
                'message': f"Kural detaylarını alma hatası: {str(e)}"
            }

    def generate_codes_for_variant(self, variant):
        """
        Verilen varyant için tüm eski bileşen kodlarını oluşturur.
        """
        try:
            helper = OldComponentCodeHelper()
            # Tüm kurallar için kodları oluştur
            generated_codes = []
            matching_rules = helper.find_matching_rules(variant)

            for rule in matching_rules:
                result = rule.generate_code(variant.text_answers)
                if result and 'codes' in result:
                    generated_codes.extend(result['codes'])

            logger.info(f"Toplam {len(generated_codes)} eski bileşen kodu oluşturuldu - Variant ID: {variant.id}")
            return generated_codes

        except Exception as e:
            logger.error(f"Eski bileşen kod oluşturma hatası: {str(e)}")
            return []