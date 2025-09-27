# backend/productconfig/utils/brand_helper.py
from ..models import Brand
from .base_helper import BaseHelper

class BrandHelper(BaseHelper):
    """
    Brand modeline yönelik özel işlemleri sağlayan yardımcı sınıf.
    """
    
    def get_all_brands(self):
        """
        Tüm aktif markaları getirir.
        """
        return self.get_all(Brand)

    def get_brand_by_name(self, name):
        """
        İsme göre bir marka getirir.
        """
        return Brand.objects.filter(name=name, is_active=True).first()

    def filter_brands_by_criteria(self, **criteria):
        """
        Verilen kriterlere göre markaları filtreler.
        """
        return self.filter_by_params(Brand, **criteria)
