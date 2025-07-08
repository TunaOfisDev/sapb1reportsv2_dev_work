# backend/productconfigv2/resources/__init__.py

from .product_resource import *
from .specification_resource import *
from .variant_resource import *
from .rule_resource import *

__all__ = [
    "ProductResource",
    "ProductFamilyResource",
    "SpecificationTypeResource",
    "SpecOptionResource",
    "VariantResource",
    "RuleResource",
]
