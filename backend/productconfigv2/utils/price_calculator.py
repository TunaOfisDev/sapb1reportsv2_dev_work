# productconfigv2/utils/price_calculator.py

from decimal import Decimal
from ..models import SpecificationType, SpecOption


def calculate_variant_price(product, selection_map):
    """
    Ürün ve kullanıcı seçimlerine göre toplam varyant fiyatını hesaplar.

    selection_map: {"Engine": "500cc", "Color": "Red"}
    """
    total = Decimal(product.base_price)

    for spec_name, option_name in selection_map.items():
        try:
            spec_type = SpecificationType.objects.get(name=spec_name)
            option = SpecOption.objects.get(spec_type=spec_type, name=option_name)

            # Fiyat çarpanı uygulanabilir
            delta = option.price_delta * spec_type.multiplier
            total += delta
        except (SpecificationType.DoesNotExist, SpecOption.DoesNotExist):
            continue  # Eksik veya geçersiz seçim varsa atla

    return round(total, 2)
