# backend/productgroupdeliverysum/api/serializers.py
from rest_framework import serializers
from ..models.delivery_summary import DeliverySummary

class DeliverySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverySummary
        fields = [
            'id', 'yil', 'yil_ay', 'teslimat_tutar', 'teslimat_girsberger', 
            'teslimat_mamul', 'teslimat_ticari', 'teslimat_nakliye', 'teslimat_montaj',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']  # ID ve zaman bilgileri sadece okunabilir

    def create(self, validated_data):
        """
        Yeni bir teslimat özeti oluşturmak için create metodunu kullanıyoruz.
        """
        return DeliverySummary.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Mevcut bir teslimat özetini güncellemek için update metodunu kullanıyoruz.
        """
        instance.yil = validated_data.get('yil', instance.yil)
        instance.yil_ay = validated_data.get('yil_ay', instance.yil_ay)
        instance.teslimat_tutar = validated_data.get('teslimat_tutar', instance.teslimat_tutar)
        instance.teslimat_girsberger = validated_data.get('teslimat_girsberger', instance.teslimat_girsberger)
        instance.teslimat_mamul = validated_data.get('teslimat_mamul', instance.teslimat_mamul)
        instance.teslimat_ticari = validated_data.get('teslimat_ticari', instance.teslimat_ticari)
        instance.teslimat_nakliye = validated_data.get('teslimat_nakliye', instance.teslimat_nakliye)
        instance.teslimat_montaj = validated_data.get('teslimat_montaj', instance.teslimat_montaj)
        instance.save()
        return instance

