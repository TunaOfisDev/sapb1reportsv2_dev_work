# backend/productconfig/api/pcserializers.py
from rest_framework import serializers
from ..models import ProductModel, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductModelSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'category', 'base_price', 'min_price', 'max_price', 'is_configurable']
