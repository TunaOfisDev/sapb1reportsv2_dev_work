# backend/tunainstotalrisk/serializers.py
from rest_framework import serializers
from .models.models import TunainsTotalRiskReport

class TunainsTotalRiskReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TunainsTotalRiskReport
        fields = '__all__'

    def create(self, validated_data):
        # muhatap_kod alanına göre update_or_create metodunu kullanarak
        # nesnenin benzersiz olmasını sağlayın ve defaults ile diğer alanları güncelleyin.
        muhatap_kod = validated_data.get('muhatap_kod')
        instance, created = TunainsTotalRiskReport.objects.update_or_create(
            muhatap_kod=muhatap_kod,
            defaults={k: v for k, v in validated_data.items() if k != 'muhatap_kod'}
        )
        return instance

    def update(self, instance, validated_data):
        # Mevcut bir TotalRiskReport nesnesini güncelleme
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
