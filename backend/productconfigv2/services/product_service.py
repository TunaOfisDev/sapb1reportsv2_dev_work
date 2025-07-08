# backend/productconfigv2/services/product_service.py

from django.db import transaction
from ..models import Product, ProductSpecification, SpecificationType


@transaction.atomic
def clone_product(original_product_id):
    """
    Bir ürünü tüm ilişkili özellikleriyle birlikte klonlar.
    """
    original = Product.objects.get(id=original_product_id)
    original_specs = ProductSpecification.objects.filter(product=original)

    # Yeni varyant kodu ve açıklaması üret (örnek: _COPY suffix eklenmiş)
    new_variant_code = f"{original.variant_code}_COPY" if original.variant_code else None
    new_variant_desc = f"{original.variant_description} (Kopya)" if original.variant_description else None

    # Ürünü kopyala
    new_product = Product.objects.create(
        family=original.family,
        code=f"{original.code}_COPY",
        name=f"{original.name} (Kopya)",
        image=original.image,
        base_price=original.base_price,
        currency=original.currency,
        variant_order=original.variant_order,
        variant_code=new_variant_code,
        variant_description=new_variant_desc,
    )

    # Özellik ilişkilerini kopyala
    for ps in original_specs:
        ProductSpecification.objects.create(
            product=new_product,
            spec_type=ps.spec_type,
            is_required=ps.is_required,
            allow_multiple=ps.allow_multiple,
            variant_order=ps.variant_order,
            display_order=ps.display_order,
        )

    return new_product


@transaction.atomic
def assign_specifications_to_product(product_id, spec_type_ids):
    """
    Belirli bir ürüne çoklu SpecificationType ata.
    """
    product = Product.objects.get(id=product_id)

    existing_spec_ids = ProductSpecification.objects.filter(product=product).values_list("spec_type_id", flat=True)
    new_specs = SpecificationType.objects.filter(id__in=spec_type_ids).exclude(id__in=existing_spec_ids)

    for index, spec_type in enumerate(new_specs, start=1):
        ProductSpecification.objects.create(
            product=product,
            spec_type=spec_type,
            is_required=spec_type.is_required,
            allow_multiple=spec_type.allow_multiple,
            variant_order=index + len(existing_spec_ids),
            display_order=index + len(existing_spec_ids),
        )


@transaction.atomic
def bulk_create_products_with_specs(product_family_id, product_data_list):
    """
    Belirli bir ürün ailesi altında, çoklu ürün ve özelliklerini oluşturur.
    `product_data_list`: [
        {
            "code": "MB01",
            "name": "Model MB01",
            "variant_code": "MB01VAR",
            "variant_description": "Model MB01 Açıklama",
            "spec_type_ids": [1, 2, 3]
        },
        ...
    ]
    """
    created_products = []

    for data in product_data_list:
        product = Product.objects.create(
            family_id=product_family_id,
            code=data["code"],
            name=data["name"],
            variant_code=data.get("variant_code"),
            variant_description=data.get("variant_description"),
            base_price=data.get("base_price", 0),
            currency=data.get("currency", "EUR"),
            variant_order=data.get("variant_order", 1),
        )

        assign_specifications_to_product(product.id, data["spec_type_ids"])
        created_products.append(product)

    return created_products
