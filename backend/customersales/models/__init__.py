# backend/customersales/models/__init__.py

"""
CustomerSales Models Package

Bu dosya, model sınıflarını paket düzeyinde erişilebilir hale getirir,
böylece diğer uygulamalardan yapılan import işlemleri basitleştirilir.
"""

from .base import BaseModel
from .customersales_models import  CustomerSalesRawData

# 'from .models import *' kullanıldığında hangi sınıfların
# içe aktarılacağını belirleyen __all__ listesi.
__all__ = [
    'BaseModel',
    'CustomerSalesRawData',
]