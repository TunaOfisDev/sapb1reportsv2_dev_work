# dosya path yolu: backend/productconfig/admin/dependent_rule.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models import DependentRule
from .resources import GenericResource


class DependentRuleResource(GenericResource):
    """
    DependentRule için Import-Export kaynağı.
    """
    class Meta:
        model = DependentRule


@admin.register(DependentRule)
class DependentRuleAdmin(ImportExportModelAdmin):
    """
    DependentRule modeli için admin sınıfı.
    """
    resource_class = DependentRuleResource
    list_display = ['name', 'rule_type', 'is_active', 'parent_question', 'trigger_option', 'order']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name', 'parent_question__name', 'trigger_option__name']
    filter_horizontal = ['dependent_questions']
    ordering = ['id']

    # Oluşturma ve güncelleme tarihlerini gizlemek için:
    exclude = ['created_at', 'updated_at']



