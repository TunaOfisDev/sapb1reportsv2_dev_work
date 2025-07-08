# backend/orderarchive/filters/order_archive_filter.py
from django_filters import rest_framework as filters
from ..models.order_archive_model import OrderDetail
import logging

logger = logging.getLogger(__name__)

class OrderDetailFilter(filters.FilterSet):
    """
    OrderDetail modeline göre filtreleme işlemleri.
    """
    order_date_start = filters.DateFilter(field_name="order_date", lookup_expr="gte")
    order_date_end = filters.DateFilter(field_name="order_date", lookup_expr="lte")
    delivery_date_start = filters.DateFilter(field_name="delivery_date", lookup_expr="gte")
    delivery_date_end = filters.DateFilter(field_name="delivery_date", lookup_expr="lte")
    
    # Yıl filtresi için özel method
    year = filters.NumberFilter(method='year_filter')
    month = filters.NumberFilter(field_name="month", lookup_expr="exact")
    
    customer_code = filters.CharFilter(field_name="customer_code", lookup_expr="icontains")
    customer_name = filters.CharFilter(field_name="customer_name", lookup_expr="icontains")
    item_code = filters.CharFilter(field_name="item_code", lookup_expr="icontains")
    item_description = filters.CharFilter(field_name="item_description", lookup_expr="icontains")
    order_number = filters.CharFilter(field_name="order_number", lookup_expr="icontains")
    document_description = filters.CharFilter(field_name="document_description", lookup_expr="icontains")  # Yeni alan

    def year_filter(self, queryset, name, value):
        """
        Özel yıl filtreleme methodu
        """
        try:
            year_value = int(value)
            # Yıl değerinin null olmadığı ve eşleştiği kayıtları getir
            return queryset.filter(year=year_value, year__isnull=False)
        except (ValueError, TypeError):
            logger.error(f"Geçersiz yıl değeri: {value}")
            return queryset.none()

    class Meta:
        model = OrderDetail
        fields = [
            'year',
            'month',
            'customer_code',
            'customer_name',
            'item_code',
            'item_description',
            'order_number',
            'document_description',  # Yeni filtre alanı
        ]
