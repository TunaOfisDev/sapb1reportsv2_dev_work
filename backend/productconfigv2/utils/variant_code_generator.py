# backend/productconfigv2/utils/variant_code_generator.py

from django.utils.text import slugify
from ..models import SpecificationType, SpecOption, Variant

def generate_variant_code(product, selection_map):
    """
    Seçilen özelliklere göre varyant kodu üretir.
    Format: product.variant_code + "." + her bir spec_option.variant_code
    Eğer herhangi bir variant_code boşsa o kısmı atlar.
    """
    if not product.variant_code:
        raise ValueError("Ürün için 'variant_code' tanımlı olmalıdır.")

    code_parts = [product.variant_code]

    try:
        spec_type_ids = [int(key) for key in selection_map.keys()]
    except ValueError:
        spec_type_ids = []

    spec_types = SpecificationType.objects.filter(id__in=spec_type_ids).order_by("variant_order")

    for spec_type in spec_types:
        option_id = selection_map.get(str(spec_type.id)) or selection_map.get(spec_type.id)
        if option_id:
            try:
                option = SpecOption.objects.get(id=option_id, spec_type=spec_type)
                if option.variant_code:
                    code_parts.append(option.variant_code)
            except SpecOption.DoesNotExist:
                continue

    return ".".join(code_parts)

def generate_variant_description(product, selection_map):
    """
    Format: product.variant_description + "-" + [her bir spec_option.variant_description]
    NOT: 
    - product.variant_description varsa eklenir.
    - spec_option.variant_description boşsa atlanır.
    - SpecType adı kullanılmaz.
    """
    description_parts = []

    # 1. Ürün açıklamasını başa ekle (varsa)
    if product.variant_description:
        description_parts.append(product.variant_description)

    # 2. SpecType'ları variant_order sırasıyla sırala
    try:
        spec_type_ids = [int(k) for k in selection_map.keys()]
    except ValueError:
        spec_type_ids = []

    spec_types = SpecificationType.objects.filter(id__in=spec_type_ids).order_by("variant_order")

    # 3. Her spec_type için seçilen option'ı bul, açıklaması varsa ekle
    for spec_type in spec_types:
        option_id = selection_map.get(str(spec_type.id)) or selection_map.get(spec_type.id)
        if not option_id:
            continue
        try:
            option = SpecOption.objects.get(id=option_id, spec_type=spec_type)
            if option.variant_description:  # Sadece doluysa ekle
                description_parts.append(option.variant_description)
        except SpecOption.DoesNotExist:
            continue

    # 4. Nokta ile birleştir ve dön
    return "-".join(description_parts)

