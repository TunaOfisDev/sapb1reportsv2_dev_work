# backend/productconfig/services/brand_service.py
from ..models import Brand
from ..utils.brand_helper import BrandHelper
from .base_service import BaseService
from django.core.exceptions import ObjectDoesNotExist

class BrandService(BaseService):
    """
    Marka işlemlerini yöneten servis sınıfı.
    """

    def __init__(self):
        super().__init__()
        self.helper = BrandHelper()  # Brand'e özel helper sınıfı.

    def create_brand(self, data):
        """
        Yeni bir marka oluşturur.
        """
        return self.create_instance(Brand, data)

    def update_brand(self, brand_id, data):
        """
        Belirtilen ID'ye sahip bir markayı günceller.
        """
        brand = self.get_instance(Brand, brand_id)
        return self.update_instance(brand, data)

    def delete_brand(self, brand_id, soft_delete=True):
        """
        Belirtilen ID'ye sahip bir markayı siler (soft veya hard).
        """
        brand = self.get_instance(Brand, brand_id)
        self.delete_instance(brand, soft_delete)

    def get_brand(self, brand_id):
        """
        Belirtilen ID'ye sahip aktif bir markayı getirir.
        """
        return self.get_instance(Brand, brand_id)

    def list_brands(self):
        """
        Tüm aktif markaları listeler.
        """
        return self.helper.get_all_brands()

    def get_brand_by_name(self, name):
        """
        İsme göre bir marka arar ve getirir.
        """
        brand = self.helper.get_brand_by_name(name)
        if not brand:
            raise ObjectDoesNotExist(f"Brand with name '{name}' not found.")
        return brand

    def filter_brands(self, **criteria):
        """
        Verilen kriterlere göre markaları filtreler.
        """
        return self.helper.filter_brands_by_criteria(**criteria)
