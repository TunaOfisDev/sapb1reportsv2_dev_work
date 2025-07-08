# backend/productconfig_simulator/serializers/simulated_variant_serializers.py
from rest_framework import serializers
from django.utils import timezone

from productconfig.models import (
    ProductModel, Option
)

from ..models.simulated_variant import SimulatedVariant


class SimulatedVariantSerializer(serializers.ModelSerializer):
    """
    Simüle edilmiş varyantlar için temel serializer.
    """
    product_model_name = serializers.SerializerMethodField()
    selected_option_names = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulatedVariant
        fields = [
            'id', 'simulation', 'product_model', 'product_model_name',
            'variant_code', 'variant_description', 'total_price',
            'text_answers', 'selected_option_names', 'old_component_codes',
            'created_at', 'is_active'
        ]
    
    def get_product_model_name(self, obj):
        """Ürün modeli adını döndürür."""
        return obj.product_model.name if obj.product_model else None
    
    def get_selected_option_names(self, obj):
        """Seçilen seçeneklerin isimlerini döndürür."""
        return [option.name for option in obj.selected_options.all()]


class SimulatedVariantDetailSerializer(serializers.ModelSerializer):
    """
    Simüle edilmiş varyantların detaylı görüntülenmesi için serializer.
    """
    product_model_name = serializers.SerializerMethodField()
    selected_options = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulatedVariant
        fields = [
            'id', 'simulation', 'product_model', 'product_model_name',
            'variant_code', 'variant_description', 'total_price',
            'text_answers', 'selected_options', 'old_component_codes',
            'created_at', 'updated_at', 'is_active'
        ]
    
    def get_product_model_name(self, obj):
        """Ürün modeli adını döndürür."""
        return obj.product_model.name if obj.product_model else None
    
    def get_selected_options(self, obj):
        """
        Seçilen seçenekleri detaylı olarak döndürür.
        """
        options = []
        for option in obj.selected_options.all():
            options.append({
                'id': option.id,
                'name': option.name,
                'option_type': option.option_type,
                'price_modifier': str(option.price_modifier)
            })
        return options


class SimulatedVariantListSerializer(serializers.ModelSerializer):
    """
    Simüle edilmiş varyantların listelenmesi için basitleştirilmiş serializer.
    """
    product_model_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulatedVariant
        fields = [
            'id', 'simulation', 'product_model_name',
            'variant_code', 'variant_description', 'total_price',
            'old_component_codes', 'created_at'
        ]
    
    def get_product_model_name(self, obj):
        """Ürün modeli adını döndürür."""
        return obj.product_model.name if obj.product_model else None


class SimulatedVariantComparisonSerializer(serializers.ModelSerializer):
    """
    Simüle edilmiş varyantları gerçek varyantlarla karşılaştırmak için serializer.
    """
    product_model_name = serializers.SerializerMethodField()
    comparison_result = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulatedVariant
        fields = [
            'id', 'product_model_name', 'variant_code', 
            'variant_description', 'total_price', 'comparison_result'
        ]
    
    def get_product_model_name(self, obj):
        """Ürün modeli adını döndürür."""
        return obj.product_model.name if obj.product_model else None
    
    def get_comparison_result(self, obj):
        """
        Simüle edilmiş varyantı gerçek varyant ile karşılaştırır.
        """
        return obj.compare_with_actual()


class SimulatedVariantExportSerializer(serializers.ModelSerializer):
    """
    Simüle edilmiş varyantları dışa aktarma için serializer.
    """
    product_model_name = serializers.SerializerMethodField()
    simulation_name = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulatedVariant
        fields = [
            'id', 'simulation', 'simulation_name', 'product_model', 'product_model_name',
            'variant_code', 'variant_description', 'total_price',
            'old_component_codes', 'created_at_formatted'
        ]
    
    def get_product_model_name(self, obj):
        """Ürün modeli adını döndürür."""
        return obj.product_model.name if obj.product_model else None
    
    def get_simulation_name(self, obj):
        """Simülasyon adını döndürür."""
        return obj.simulation.name if obj.simulation else None
    
    def get_created_at_formatted(self, obj):
        """Oluşturulma zamanını biçimlendirilmiş olarak döndürür."""
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return None