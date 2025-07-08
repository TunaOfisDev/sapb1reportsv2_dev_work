# backend/activities/serializers.py
from rest_framework import serializers
from .models.models import Activity
import datetime

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

    def validate_baslangic_tarihi(self, value):
        if value:
            try:
                # Gelen tarihi `DD.MM.YYYY` formatından `date` objesine dönüştür
                datetime_obj = datetime.datetime.strptime(value, '%d.%m.%Y')
                # `date` objesini `YYYY-MM-DD` formatına çevir
                return datetime_obj.strftime('%Y-%m-%d')
            except ValueError:
                raise serializers.ValidationError("Geçersiz başlangıç tarihi formatı, 'DD.MM.YYYY' formatında olmalıdır.")
        return value

    def validate_bitis_tarihi(self, value):
        if value:
            try:
                # Gelen tarihi `DD.MM.YYYY` formatından `date` objesine dönüştür
                datetime_obj = datetime.datetime.strptime(value, '%d.%m.%Y')
                # `date` objesini `YYYY-MM-DD` formatına çevir
                return datetime_obj.strftime('%Y-%m-%d')
            except ValueError:
                raise serializers.ValidationError("Geçersiz bitiş tarihi formatı, 'DD.MM.YYYY' formatında olmalıdır.")
        return value

    def create(self, validated_data):
        return Activity.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

