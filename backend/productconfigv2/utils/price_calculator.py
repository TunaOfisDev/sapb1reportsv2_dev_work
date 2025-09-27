# productconfigv2/utils/price_calculator.py

from decimal import Decimal
from ..models import SpecificationType, SpecOption, Product

def calculate_variant_price(product, selection_map):
    """
    Ürün ve kullanıcı seçimlerine göre price_delta'ları kullanarak toplam varyant fiyatını hesaplar.
    Bu fonksiyon, SAP'den fiyat çekilmeden önce bir önizleme sağlar.
    """
    total = Decimal(product.base_price)

    option_ids = [v for v in selection_map.values() if v]
    if not option_ids:
        return round(total, 2)

    selected_options = SpecOption.objects.filter(id__in=option_ids).select_related('spec_type')

    for option in selected_options:
        delta = option.price_delta * option.spec_type.multiplier
        total += delta

    return round(total, 2)