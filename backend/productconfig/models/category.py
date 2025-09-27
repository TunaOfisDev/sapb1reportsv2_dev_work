# backend/productconfig/models/category.py
from django.db import models
from .base import BaseModel


class Category(BaseModel):
    """
    Kategori modeli, ürünlerin belirli bir grupta sınıflandırılmasını sağlar.
    Her kategori, bir marka ve ürün grubuna ait olarak tanımlanır.
    """
    name = models.CharField(max_length=255, verbose_name="Kategori Adı")
    brand = models.ForeignKey(
        'Brand', 
        on_delete=models.CASCADE, 
        related_name="categories", 
        verbose_name="Marka"
    )
    product_group = models.ForeignKey(
        'ProductGroup', 
        on_delete=models.CASCADE, 
        related_name="categories", 
        verbose_name="Ürün Grubu"
    )

    class Meta:
        verbose_name = "03-Kategori"
        verbose_name_plural = "03-Kategoriler"
        ordering = ['brand', 'product_group', 'name']
        # Aynı marka ve ürün grubu altında aynı isimde kategori olmamasını sağlar
        unique_together = ['brand', 'product_group', 'name']


    def __str__(self):
        return f"{self.brand.name} - {self.product_group.name} - {self.name}"

