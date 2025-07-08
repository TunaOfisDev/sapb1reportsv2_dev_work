# backend/productconfig/utils/product_group_helper.py
from ..models import ProductGroup, Brand

class ProductGroupHelper:
    """
    ProductGroup modeline yönelik özel işlemleri sağlayan yardımcı sınıf.
    """

    def filter_groups_by_brand(self, brand: Brand):
        """
        Verilen markaya ait tüm ürün gruplarını döndürür.
        """
        return ProductGroup.objects.filter(brand=brand).order_by('name')

    def get_group_names_by_brand(self, brand: Brand):
        """
        Verilen markaya ait ürün gruplarının isimlerini döndürür.
        """
        groups = self.filter_groups_by_brand(brand)
        return [group.name for group in groups]

    def group_exists(self, brand: Brand, group_name: str):
        """
        Belirli bir marka altında verilen isimde bir ürün grubu olup olmadığını kontrol eder.
        """
        return ProductGroup.objects.filter(brand=brand, name=group_name).exists()
