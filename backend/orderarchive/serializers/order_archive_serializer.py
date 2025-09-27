# backend/orderarchive/serializers/order_archive_serializer.py
from rest_framework import serializers
from ..models.order_archive_model import OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    """
    OrderDetail modelini JSON formatına dönüştüren ve gerektiğinde içeri aktarım için kullanılabilecek serializer.
    """

    class Meta:
        model = OrderDetail
        fields = '__all__'  # Tüm alanları serileştir
        read_only_fields = ['id']  # Varsayılan id alanı sadece okunabilir
