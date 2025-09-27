# backend/deliverydocsum/serializers.py
from rest_framework import serializers
from .models.models import DeliveryDocSummary

class DeliveryDocSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDocSummary
        fields = [
            'id', 'cari_kod', 'cari_adi', 'temsilci', 'cari_grup',
            'gunluk_toplam', 'dun_toplam', 'onceki_gun_toplam', 'aylik_toplam', 'yillik_toplam',
            'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi',
            'gunluk_ilgili_siparis_numaralari', 'dun_ilgili_siparis_numaralari', 'onceki_gun_ilgili_siparis_numaralari',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        instance, created = DeliveryDocSummary.objects.update_or_create(
            cari_kod=validated_data.get('cari_kod', None),
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
