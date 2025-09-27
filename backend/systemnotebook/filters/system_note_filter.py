# backend/systemnotebook/filters/system_note_filter.py

import django_filters
from systemnotebook.models.system_note_model import SystemNote

class SystemNoteFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    source = django_filters.CharFilter(field_name='source', lookup_expr='exact')
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')

    class Meta:
        model = SystemNote
        fields = ['source', 'created_by', 'created_at__gte', 'created_at__lte']
