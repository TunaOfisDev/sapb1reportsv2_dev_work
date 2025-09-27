# backend/logo_supplier_receivables_aging/serializers.py

from rest_framework import serializers
from .models.models import SupplierRawTransaction
from .models.closinginvoice import SupplierAgingSummary


class SupplierRawTransactionSerializer(serializers.ModelSerializer):
    """
    Logo'dan gelen ham verinin dışa açılımı için serializer.
    """

    class Meta:
        model = SupplierRawTransaction
        fields = [
            'id', 'cari_kod', 'cari_ad', 'ay', 'yil',
            'borc', 'alacak', 'created_at', 'updated_at'
        ]


class SupplierAgingSummarySerializer(serializers.ModelSerializer):
    aylik_kalan_alacak = serializers.SerializerMethodField()

    class Meta:
        model = SupplierAgingSummary
        fields = ['cari_kod', 'cari_ad', 'guncel_bakiye', 'aylik_kalan_alacak']

    def get_aylik_kalan_alacak(self, obj):
        return obj.sorted_aylik_kalan_alacak