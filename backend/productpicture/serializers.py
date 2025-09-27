# backend/productpicture/serializers.py
from rest_framework import serializers
from .models.productpicture_models import Product

class ProductSerializer(serializers.ModelSerializer):
    # 'picture_path' alanını serializer'a ekleyin
    picture_path = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['item_code', 'item_name', 'group_name', 'price', 'currency', 'picture_name', 'picture_path']

    def get_picture_path(self, obj):
        # 'picture_name' alanını kullanarak resim yolunu al
        return Product.find_picture_path(obj.picture_name)

    def to_representation(self, instance):
        # Modelin JSON temsilini özelleştir
        representation = super().to_representation(instance)
        # Fiyat formatını istenilen şekilde ayarla
        if representation['price'] is not None:
            representation['price'] = "{:,.2f}".format(instance.price).replace(',', '.').replace('.', ',')
        # Resim yolu zaten 'get_picture_path' metodu ile doldurulmuş olacak
        return representation
    

    def create(self, validated_data):
        # Serializer üzerinden yeni bir Product nesnesi oluşturma
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Serializer üzerinden bir Product nesnesini güncelleme
        # 'picture_name' değişiklikleri güncelleme esnasında da kontrol edilir
        instance.item_code = validated_data.get('item_code', instance.item_code)
        instance.item_name = validated_data.get('item_name', instance.item_name)
        instance.group_name = validated_data.get('group_name', instance.group_name)
        instance.price = validated_data.get('price', instance.price)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.picture_name = validated_data.get('picture_name', instance.picture_name)
        
        instance.save()
        return instance

