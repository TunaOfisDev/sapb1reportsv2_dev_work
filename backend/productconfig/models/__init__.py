# backend/productconfig/models/__init__.py
# Temel modeller
from .base import BaseModel
from .brand import Brand
from .product_group import ProductGroup
from .category import Category
from .product_model import ProductModel
from .price_multiplier_rule import PriceMultiplierRule
from .process_status import ProcessStatus

# Kural modelleri
from .dependent_rule import DependentRule
from .conditional_options import ConditionalOption

# Ana modeller
from .question import Question
from .option import Option
from .question_option_relation import QuestionOptionRelation
from .variant import Variant
from .old_component_code import OldComponentCode

from .guide import Guide

__all__ = [
    'BaseModel',
    'Brand',
    'ProductGroup',
    'Category',
    'ProductModel',
    'PriceMultiplierRule',
    'ProcessStatus',
    'DependentRule', 
    'ConditionalOption', 
    'Question',
    'Option',
    'QuestionOptionRelation',
    'Variant',
    "OldComponentCode",
    "Guide",
]