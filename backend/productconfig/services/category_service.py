# backend/productconfig/services/category_service.py
from ..models import Category
from ..utils.category_helper import CategoryHelper
from .base_service import BaseService

class CategoryService(BaseService):
    """
    Kategori işlemlerini yöneten servis sınıfı.
    """

    def __init__(self):
        super().__init__()
        self.helper = CategoryHelper()  # Category modeline özel helper sınıfı

    def get_categories_by_chain(self, brand=None, product_group=None):
        """
        Zincirleme marka ve grup eşleşmesine göre kategorileri döner.
        """
        return self.helper.get_categories_by_chain(brand=brand, product_group=product_group)

    def create_category(self, data):
        """
        Yeni bir kategori oluşturur.
        """
        return self.create_instance(Category, data)

    def update_category(self, category_id, data):
        """
        Belirtilen ID'ye sahip bir kategoriyi günceller.
        """
        category = self.get_instance(Category, category_id)
        return self.update_instance(category, data)

    def delete_category(self, category_id, soft_delete=True):
        """
        Belirtilen ID'ye sahip bir kategoriyi siler (soft veya hard).
        """
        category = self.get_instance(Category, category_id)
        self.delete_instance(category, soft_delete)

    def get_category(self, category_id):
        """
        Belirtilen ID'ye sahip aktif bir kategoriyi getirir.
        """
        return self.get_instance(Category, category_id)

    def list_categories(self):
        """
        Tüm aktif kategorileri listeler.
        """
        return self.helper.get_all_categories()

    def get_categories_by_brand(self, brand):
        """
        Verilen markaya ait kategorileri getirir.
        """
        return self.helper.get_categories_by_brand(brand)

    def get_categories_by_product_group(self, product_group):
        """
        Verilen ürün grubuna ait kategorileri getirir.
        """
        return self.helper.get_categories_by_product_group(product_group)

    def filter_categories(self, **criteria):
        """
        Verilen kriterlere göre kategorileri filtreler.
        """
        return self.helper.filter_categories_by_criteria(**criteria)
