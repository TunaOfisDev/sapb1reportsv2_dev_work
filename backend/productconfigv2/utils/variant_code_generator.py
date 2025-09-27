# backend/productconfigv2/utils/variant_code_generator.py

from ..models import SpecOption

def generate_variant_code(product, selection_map):
    """
    Seçilen özelliklere göre sıralı bir şekilde "30'lu" varyant kodu üretir.
    Daha verimli çalışması için tek bir veritabanı sorgusu kullanır.
    """
    if not product.code:
        raise ValueError("Ürün için 'code' alanı (örn: 30.BW) tanımlı olmalıdır.")

    # Kodun başlangıcı olarak ürünün ana kodunu (30.BW) alıyoruz.
    # product.variant_code yerine product.code kullanmak anlamsal olarak daha doğrudur.
    code_parts = [product.code]

    option_ids = [v for v in selection_map.values() if v]
    if not option_ids:
        return product.code

    # TEK SORGULAMA: Gerekli tüm seçenekleri, özellik sırasına göre tek seferde çekiyoruz.
    # Bu, N+1 sorgu problemini çözer ve performansı artırır.
    selected_options = SpecOption.objects.filter(id__in=option_ids) \
                                          .select_related('spec_type') \
                                          .order_by('spec_type__variant_order')

    for option in selected_options:
        if option.variant_code:
            code_parts.append(option.variant_code)

    return ".".join(filter(None, code_parts))

def generate_variant_description(product, selection_map):
    """
    Seçilen özelliklere göre sıralı bir şekilde varyant açıklaması üretir.
    Daha verimli çalışması için tek bir veritabanı sorgusu kullanır.
    """
    description_parts = []

    if product.variant_description:
        description_parts.append(product.variant_description)

    option_ids = [v for v in selection_map.values() if v]
    if not option_ids and not product.variant_description:
        return ""
    if not option_ids:
        return product.variant_description

    # TEK SORGULAMA: Gerekli tüm seçenekleri, özellik sırasına göre tek seferde çekiyoruz.
    selected_options = SpecOption.objects.filter(id__in=option_ids) \
                                          .select_related('spec_type') \
                                          .order_by('spec_type__variant_order')

    for option in selected_options:
        if option.variant_description:
            description_parts.append(option.variant_description)

    return " - ".join(filter(None, description_parts))