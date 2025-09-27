# backend/productconfigv2/resources/__init__.py

# Yıldız (*) import yerine, her bir class'ı kendi dosyasından açıkça import ediyoruz.
# Bu, import sırası hatalarını ve belirsizlikleri önler.
from .product_resource import ProductResource, ProductFamilyResource
from .specification_resource import SpecificationTypeResource, SpecOptionResource
from .variant_resource import VariantResource
from .rule_resource import RuleResource

# __all__ listesi, "from .resources import *" kullanıldığında nelerin import edileceğini tanımlar.
# Bu listenin kalması iyi bir pratiktir.
__all__ = [
    "ProductResource",
    "ProductFamilyResource",
    "SpecificationTypeResource",
    "SpecOptionResource",
    "VariantResource",
    "RuleResource",
]