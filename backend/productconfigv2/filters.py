# backend/productconfigv2/filters.py

import django_filters
from .models import Variant

class VariantFilter(django_filters.FilterSet):
    """
    Variant modeli için sadeleştirilmiş ve güçlü filtreleme.
    Veritabanının tr_TR.UTF-8 collation'ına güvenir.
    """
    project_name = django_filters.CharFilter(lookup_expr='icontains')
    reference_code = django_filters.CharFilter(lookup_expr='icontains')
    new_variant_code = django_filters.CharFilter(lookup_expr='icontains')
    
    # YENİ FİLTRE: Açıklama alanında arama yapmak için.
    new_variant_description = django_filters.CharFilter(lookup_expr='icontains')

    # YENİ FİLTRE: Oluşturan kullanıcının email'inde arama yapmak için.
    # Frontend'de 'created_by_username' olarak isimlendireceğiz.
    created_by_username = django_filters.CharFilter(
        field_name='created_by__email', 
        lookup_expr='icontains'
    )

    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Variant
        fields = [
            'project_name',
            'reference_code',
            'new_variant_code',
            'new_variant_description', # Yeni alanı ekliyoruz
            'created_by_username',   # Yeni alanı ekliyoruz
            'product',
            'created_by',
        ]