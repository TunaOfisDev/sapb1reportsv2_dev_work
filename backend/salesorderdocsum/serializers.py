# backend/salesorderdocsum/serializers.py
from rest_framework import serializers
from .models.salesorderdetail import SalesOrderDetail
from .models.docsum import DocumentSummary


class SalesOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderDetail
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']  # Opsiyonel olarak belirtilebilir


class DocumentSummarySerializer(serializers.ModelSerializer):
    belge_iskonto_oran = serializers.FloatField(read_only=True)

    class Meta:
        model = DocumentSummary
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']  # Opsiyonel olarak belirtilebilir
