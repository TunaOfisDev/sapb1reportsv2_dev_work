# backend/logocustomercollection/serializers.py

from rest_framework import serializers
from .models.models import LogoCustomerCollectionTransaction
from .models.closinginvoice import LogoCustomerCollectionAgingSummary


class LogoCustomerCollectionTransactionSerializer(serializers.ModelSerializer):
    """
    Logo'dan gelen müşteri ham verisinin dışa açılımı için serializer.
    """

    class Meta:
        model = LogoCustomerCollectionTransaction
        fields = [
            'cari_kod',
            'cari_ad',
            'ay',
            'yil',
            'borc',
            'alacak'
        ]


class LogoCustomerCollectionAgingSummarySerializer(serializers.ModelSerializer):
    """
    Her müşteri için aylık kalan borç özetini dışa açan serializer.
    JSONField içeriği sıralı olarak gösterilir.
    """
    aylik_kalan_borc = serializers.SerializerMethodField()

    class Meta:
        model = LogoCustomerCollectionAgingSummary
        fields = [
            'cari_kod',
            'cari_ad',
            'guncel_bakiye',
            'aylik_kalan_borc',
            'created_at',
            'updated_at',
        ]

    def get_aylik_kalan_borc(self, obj):
        return obj.sorted_aylik_kalan_borc
