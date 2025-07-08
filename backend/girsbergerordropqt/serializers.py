# backend/girsbergerordropqt/serializers.py
from rest_framework import serializers
from .models.models import OrdrDetailOpqt

class OrdrDetailOpqtSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdrDetailOpqt
        fields = '__all__'

    def create(self, validated_data):
        return OrdrDetailOpqt.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
