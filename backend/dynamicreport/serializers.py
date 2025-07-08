# backend\dynamicreport\serializers.py
from rest_framework import serializers
from .models.models import SqlQuery, DynamicTable, DynamicHeaders, HanaDataType

class SqlQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SqlQuery
        fields = '__all__'

class DynamicTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicTable
        fields = '__all__'

class DynamicHeadersSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicHeaders
        fields = '__all__'

class HanaDataTypeSerializer(serializers.ModelSerializer):  # Yeni serializer ekleyin
    class Meta:
        model = HanaDataType
        fields = '__all__'

