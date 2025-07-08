# backend/bomcostmanager/api/serializers.py

from rest_framework import serializers
from ..models.bomcomponent_models import BOMComponent, BOMRecord
from ..models.bomproduct_models import BOMProduct

class BOMComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOMComponent
        fields = '__all__'
        read_only_fields = ('updated_cost',)  # updated_cost, save() metodu ile hesaplanır.

class BOMRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOMRecord
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')  # Otomatik timestamp alanları varsa.

class BOMProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOMProduct
        fields = '__all__'
        read_only_fields = ('last_fetched_at',)  # Verinin çekildiği zamanı kontrol eder.
