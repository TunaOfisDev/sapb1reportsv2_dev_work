# backend/productpicture/models/productpicture_models.py
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.conf import settings
from .base import BaseModel
from django.core.files.storage import default_storage
from loguru import logger
import os

price_format_validator = RegexValidator(
    regex=r'^\d{3}\.\d{3},\d{2}$',
    message="Price must be in the format '###.###,##'"
)

class Product(BaseModel):
    item_code = models.CharField(max_length=255, unique=True, db_index=True)
    item_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    group_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    price = models.DecimalField(max_digits=25, decimal_places=2, blank=True, null=True, db_index=True) 
    currency = models.CharField(max_length=3, blank=True, null=True, db_index=True)
    picture_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    @staticmethod
    def get_available_images():
        static_folder = 'backend_static'
        return [f for f in os.listdir(static_folder) if f.endswith('.jpg') and os.path.isfile(os.path.join(static_folder, f))]

    @staticmethod
    def find_picture_path(picture_name):
        available_images = Product.get_available_images()
        static_url = settings.SITE_URL + '/backend_static/'

        # Dosyanın listede olup olmadığını kontrol et
        if picture_name in available_images:
            full_path = static_url + picture_name
            logger.info(f"Resim bulundu: {full_path}")
            return full_path
        else:
            # Eğer dosya listede yoksa, varsayılan resmi döndür
            default_path = static_url + 'no_image.jpg'
            logger.warning(f"Resim bulunamadı: {picture_name} - Varsayılan resim dönüyor: {default_path}")
            return default_path

    @classmethod
    def get_statistics(cls):
        products = cls.objects.all()
        total_items = products.count()
        matching_images = sum(1 for product in products if product.picture_name in cls.get_available_images())

        return {
            'total_items': total_items,
            'matching_images': matching_images
        }

    @classmethod
    def update_from_api(cls, api_data):
        with transaction.atomic():
            # Mevcut verileri sil
            cls.objects.all().delete()

            for item in api_data:
                item_code = item['ItemCode']
                item_name = item['ItemName']
                group_name = item['ItmsGrpNam']
                picture_name = item['PicturName']
                price = item['Price']
                currency = item['Currency']

                formatted_price = cls.format_price(price) if price is not None else None

                # Yeni veriyi veritabanına ekleyin
                Product.objects.create(
                    item_code=item_code,
                    item_name=item_name,
                    group_name=group_name,
                    price=formatted_price,
                    currency=currency,
                    picture_name=picture_name,
                   
                )

    @staticmethod
    def format_price(price):
        """
        API'den gelen fiyat verisini uygun formata dönüştürür.
        Örnek: 123456.78 -> '123456.78'
        """
        if price is None:
            return "0.00"  # None değeri için varsayılan olarak "0.00" döndür

        # Fiyatı iki ondalık basamağa yuvarla
        formatted_price = f"{price:.2f}"

        return formatted_price