# backend/productconfigv2/filters.py

import django_filters
from .models import Variant

class VariantFilter(django_filters.FilterSet):
    """
    Variant modeli için sadeleştirilmiş ve güçlü filtreleme.
    Veritabanının tr_TR.UTF-8 collation'ına güvenir.
    """
    # NİHAİ GÜNCELLEME: Tüm metin aramaları için standart `icontains` kullanıyoruz.
    project_name = django_filters.CharFilter(lookup_expr='icontains')
    reference_code = django_filters.CharFilter(lookup_expr='icontains')
    new_variant_code = django_filters.CharFilter(lookup_expr='icontains')
    
    # Tarih filtreleri olduğu gibi kalabilir, onlar düzgün çalışıyor.
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Variant
        # Filtrelenecek tüm alanları Meta.fields altında belirtmek en temiz yoldur.
        fields = [
            'project_name',
            'reference_code',
            'new_variant_code',
            'product',
            'created_by',
        ]