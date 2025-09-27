# backend/productconfig/services/product_group_service.py
from ..models import ProductGroup, Brand
from ..utils.product_group_helper import ProductGroupHelper

class ProductGroupService:
    """
    ProductGroup işlemlerini yöneten servis sınıfı.
    """

    def __init__(self):
        self.helper = ProductGroupHelper()

    def get_product_groups_for_brand(self, brand: Brand):
        """
        Verilen markaya ait ürün gruplarını döndürür.
        """
        return self.helper.filter_groups_by_brand(brand)

    def get_product_group_names_for_brand(self, brand: Brand):
        """
        Verilen markaya ait ürün grubu isimlerini döndürür.
        """
        return self.helper.get_group_names_by_brand(brand)

    def create_product_group(self, brand: Brand, group_name: str):
        """
        Yeni bir ürün grubu oluşturur. Eğer marka altında aynı isimde bir grup varsa, oluşturmaz.
        """
        if not self.helper.group_exists(brand, group_name):
            return ProductGroup.objects.create(brand=brand, name=group_name)
        return None

    def delete_product_group(self, product_group: ProductGroup):
        """
        Belirtilen ürün grubunu soft delete yapar.
        """
        product_group.delete()
