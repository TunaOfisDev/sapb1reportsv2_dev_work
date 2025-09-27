# backend/productconfig/utils/category_helper.py
from ..models import Category
from .base_helper import BaseHelper

class CategoryHelper(BaseHelper):
    """
    Category modeline yönelik özel işlemleri sağlayan yardımcı sınıf.
    """

    def get_categories_by_chain(self, brand=None, product_group=None):
        """
        Marka ve ürün grubuna göre kategorileri zincirleme şekilde filtreler.
        """
        queryset = Category.objects.filter(is_active=True)

        if brand:
            queryset = queryset.filter(brand=brand)
        if product_group:
            queryset = queryset.filter(product_group=product_group)

        return queryset.order_by('name')

    def get_all_categories(self):
        """
        Tüm aktif kategorileri getirir.
        """
        return self.get_all(Category)

    def get_categories_by_brand(self, brand):
        """
        Verilen markaya ait kategorileri getirir.
        """
        return Category.objects.filter(brand=brand, is_active=True).order_by('product_group', 'name')

    def get_categories_by_product_group(self, product_group):
        """
        Verilen ürün grubuna ait kategorileri getirir.
        """
        return Category.objects.filter(product_group=product_group, is_active=True).order_by('name')

    def filter_categories_by_criteria(self, **criteria):
        """
        Verilen kriterlere göre kategorileri filtreler.
        """
        return self.filter_by_params(Category, **criteria)
