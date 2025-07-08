# backend/salesorder/serializers.py
from rest_framework import serializers
from .models.customersalesorder import CustomerSalesOrder 
from .models.models import SalesOrder
from import_export import resources


class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = '__all__'

    def create(self, validated_data):
        unique_master_no = validated_data.get('unique_master_no')
        instance, created = SalesOrder.objects.update_or_create(
            unique_master_no=unique_master_no,
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

# CustomerSalesOrder için yeni bir serializer sınıfı
class CustomerSalesOrderSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = CustomerSalesOrder
        fields = '__all__'

    def create(self, validated_data):
        musteri_kod = validated_data.get('musteri_kod')
        # update_or_create metodunu kullanarak musteri_kod alanının benzersiz olmasını sağlayın
        instance, created = CustomerSalesOrder.objects.update_or_create(
            musteri_kod=musteri_kod,
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        # Mevcut bir CustomerSalesOrder nesnesini güncelleme
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class LastUpdatedSerializer(serializers.Serializer):
    last_updated = serializers.SerializerMethodField()

    def get_last_updated(self, obj):
        # `obj` burada kullanılmayacak çünkü doğrudan bir model instance'ı üzerinden çalışmıyoruz.
        # Bunun yerine, yukarıda tanımladığınız `get_last_updated_time` fonksiyonunu kullanarak
        # en son güncellenme zamanını alacağız.
        last_updated_order = CustomerSalesOrder.objects.order_by('-updated_at').first()
        if last_updated_order:
            return last_updated_order.updated_at.strftime('%d.%m.%Y %H:%M')
        return None


class CustomerSalesOrderResource(resources.ModelResource):
    class Meta:
        model = CustomerSalesOrder
        fields = ('grup','musteri_kod', 'musteri_ad', 'yillik_toplam', 'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik')
        export_order = ('grup','musteri_kod', 'musteri_ad', 'yillik_toplam', 'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran', 'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik')
