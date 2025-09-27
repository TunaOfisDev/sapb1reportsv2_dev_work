# backend/productconfigv2/filters.py (YENİ DOSYA)

import django_filters
from .models import Variant

class VariantFilter(django_filters.FilterSet):
    """
    Variant modeli için gelişmiş filtreleme seçenekleri sunar.
    """
    # Proje Adı, Referans Kodu ve Üretim Kodu için büyük/küçük harf duyarsız,
    # kısmi metin araması (içerir) sağlar.
    # Örn: /variants/?project_name=test
    project_name = django_filters.CharFilter(lookup_expr='icontains')
    reference_code = django_filters.CharFilter(lookup_expr='icontains')
    new_variant_code = django_filters.CharFilter(lookup_expr='icontains')

    # Oluşturulma tarihine göre filtreleme sağlamak için.
    # Örn: /variants/?created_after=2025-09-20
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Variant
        # Bu alanlarda tam eşleşme ile filtreleme yapar.
        # Örn: /variants/?product=7
        fields = [
            'project_name', 
            'reference_code', 
            'new_variant_code', 
            'product',
            'created_by',
        ]