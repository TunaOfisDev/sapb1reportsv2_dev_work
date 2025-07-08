# backend/salesbudgetv2/serializers.py
from rest_framework import serializers
from .models.models import SalesBudgetv2

class SalesBudgetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SalesBudgetv2
        fields = '__all__'

    def create(self, validated_data):
        satici = validated_data.get('satici')
        # update_or_create metodunu kullanarak satici alanının benzersiz olmasını sağlayın
        instance, created = SalesBudgetv2.objects.update_or_create(
            satici=satici,
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        # Mevcut bir SalesBudget nesnesini güncelleme
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """ 
        Özelleştirilmiş to_representation metodu ile instance'ı serileştirin.
        Özellikle ondalık alanları string'e dönüştürmek için kullanılabilir.
        """
        ret = super().to_representation(instance)
        ret['yuzde_oran'] = instance.yuzde_oran_hesapla()
        return ret
