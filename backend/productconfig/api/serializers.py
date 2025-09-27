# backend/productconfig/api/serializers.py
from rest_framework import serializers
from django.apps import apps
from ..models import Option
from django.conf import settings

class OptionSerializer(serializers.ModelSerializer):
    """
    Option modeli için özel serializer.
    Resim yükleme ve URL gösterimi için özelleştirilmiş.
    """
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    class Meta:
        model = Option
        fields = [
            'id', 'name', 'option_type', 'price_modifier', 'color_status',
            'variant_code_part', 'variant_description_part', 'image', 'image_url',
            'is_popular', 'applicable_brands', 'applicable_groups',
            'applicable_categories', 'applicable_product_models',
            'created_at', 'updated_at', 'is_active'
        ]

    def get_image_url(self, obj):
        """
        Resmin tam URL'sini döndürür.
        """
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_image(self, value):
        """
        Yüklenen resim için doğrulama kuralları.
        """
        if value:
            # Dosya boyutu kontrolü (5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Resim dosyası 5MB'dan büyük olamaz."
                )

            # Dosya tipi kontrolü
            allowed_types = ['image/jpeg', 'image/png']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Sadece JPEG ve PNG dosyaları desteklenir."
                )

        return value

class GenericModelSerializer(serializers.ModelSerializer):
    """
    Tüm modeller için dinamik serializer.
    Option modeli için özel durumu yönetir.
    """
    class Meta:
        model = None
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        model_name = kwargs.pop('model_name', None)
        if model_name:
            if model_name == 'Option':
                # Option modeli için özel serializer kullan
                self.__class__ = OptionSerializer
                kwargs['context'] = getattr(self, 'context', {})
            else:
                # Diğer modeller için genel serializer kullan
                self.Meta.model = apps.get_model('productconfig', model_name)
                self.Meta.fields = '__all__'
        super().__init__(*args, **kwargs)