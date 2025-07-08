# productconfigv2/utils/data_importer.py

from ..models import (
    Product, ProductFamily
)
from ..services.specification_service import create_specification_type_with_options
from ..services.product_service import assign_specifications_to_product


def import_product_family_with_specs(data):
    """
    Dış kaynaklardan gelen JSON/CSV verisini kullanarak
    ürün ailesi, ürün, özellik tipi ve seçeneklerini içeri aktarır.

    data = {
        "product_family": {"code": "MB", "name": "Motorbike"},
        "products": [
            {
                "code": "MB12",
                "name": "Model MB12",
                "base_price": 6000,
                "specs": [
                    {
                        "spec_type": {"code": "ENG", "name": "Engine"},
                        "options": [
                            {"code": "250", "name": "250cc"},
                            {"code": "500", "name": "500cc"},
                        ]
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    family_data = data["product_family"]
    family, _ = ProductFamily.objects.get_or_create(code=family_data["code"], defaults={
        "name": family_data["name"]
    })

    for product_data in data["products"]:
        product, _ = Product.objects.get_or_create(
            family=family,
            code=product_data["code"],
            defaults={
                "name": product_data["name"],
                "base_price": product_data.get("base_price", 0),
                "currency": product_data.get("currency", "EUR")
            }
        )

        spec_type_ids = []
        for spec in product_data.get("specs", []):
            spec_type_data = spec["spec_type"]
            option_list = spec.get("options", [])
            spec_type = create_specification_type_with_options(spec_type_data, option_list)
            spec_type_ids.append(spec_type.id)

        assign_specifications_to_product(product.id, spec_type_ids)
