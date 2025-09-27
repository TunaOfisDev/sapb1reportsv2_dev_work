# productconfigv2/services/specification_service.py
from django.db import transaction
from ..models import SpecificationType, SpecOption, SpecificationOption


@transaction.atomic
def create_specification_type_with_options(spec_type_data, option_list):
    """
    Yeni bir özellik tipi ve ona bağlı seçenekleri oluşturur.
    option_list: [{"name": "250cc", "reference_code": "250CC", ...}, ...]
    """
    spec_type = SpecificationType.objects.create(**spec_type_data)

    for index, option_data in enumerate(option_list, start=1):
        SpecOption.objects.create(
            spec_type=spec_type,
            name=option_data["name"],
            image=option_data.get("image"),
            variant_code=option_data.get("variant_code", ""),
            variant_description=option_data.get("variant_description", ""),
            # YENİ: reference_code'u da veri listesinden alıyoruz.
            reference_code=option_data.get("reference_code"),
            price_delta=option_data.get("price_delta", 0),
            is_default=option_data.get("is_default", False),
            display_order=index,
        )

    return spec_type


@transaction.atomic
def clone_spec_options(source_spec_type_id, target_spec_type_id):
    """
    Bir özellik tipinin seçeneklerini başka bir tip altına kopyalar.
    """
    source_options = SpecOption.objects.filter(spec_type_id=source_spec_type_id)
    target_spec_type = SpecificationType.objects.get(id=target_spec_type_id)

    for option in source_options:
        SpecOption.objects.create(
            spec_type=target_spec_type,
            name=f"{option.name} (Kopya)",
            image=option.image,
            variant_code=f"{option.variant_code}_COPY" if option.variant_code else None,
            variant_description=option.variant_description,
            price_delta=option.price_delta,
            is_default=False,
            display_order=option.display_order,
        )


def get_valid_options_for_product(product_id, spec_type_id):
    """
    Belirli bir ürün ve özellik tipi için geçerli seçenekleri getirir.
    """
    return SpecificationOption.objects.filter(
        product_id=product_id,
        spec_type_id=spec_type_id,
        option__is_active=True
    ).select_related("option").order_by("display_order")
